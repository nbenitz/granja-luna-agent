import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  ExpoSpeechRecognitionModule,
  useSpeechRecognitionEvent,
} from "expo-speech-recognition";
import { StatusBar } from "expo-status-bar";
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  AppState,
  BackHandler,
  Linking,
  Modal,
  Pressable,
  SafeAreaView,
  StatusBar as NativeStatusBar,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  WebView,
  WebViewMessageEvent,
  WebViewNavigation,
} from "react-native-webview";

const DEFAULT_SERVER_URL =
  process.env.EXPO_PUBLIC_GRANJA_LUNA_URL ?? "https://granja.nodaluna.com";
const LAN_SERVER_URL =
  process.env.EXPO_PUBLIC_GRANJA_LUNA_LAN_URL ?? "http://192.168.18.15:8011";
const SERVER_URL_KEY = "granja-luna.server-url";
const CONNECTION_SETTINGS_KEY = "granja-luna.connection-settings.v1";
const HEALTH_PATH = "/api/health";
const LAN_PROBE_TIMEOUT_MS = 1_800;
const VOICE_PROTOCOL = "agent.voice.v1";
const LINK_PROTOCOL = "agent.link.v1";
const DEFAULT_SPEECH_LANGUAGE = "es-PY";
const ALLOWED_APP_PROTOCOLS = new Set(["personal-agent:", "granja-luna:"]);
const NATIVE_SHELL_SCRIPT =
  'document.documentElement.dataset.nativeShell="true";true;';
const CLOUDFLARE_ACCESS_HOSTS = new Set([
  "dash.cloudflare.com",
  "oidc.iam.cfapi.net",
  "oauth-callbacks.cloudflareaccess.com",
]);

type VoiceEventType = "speech.state" | "speech.result" | "speech.error";

type VoiceBridgeDetail = {
  protocol: typeof VOICE_PROTOCOL;
  type: VoiceEventType;
  state: string;
  transcript: string;
  isFinal: boolean;
  error: string | null;
  requestId?: string;
};

type VoiceSessionPhase =
  | "requesting-permission"
  | "starting"
  | "listening"
  | "stopping"
  | "cancelling";

type VoiceSession = {
  requestId: string;
  generation: number;
  phase: VoiceSessionPhase;
  cancelled: boolean;
  suppressNativeEvents: boolean;
  terminalError: boolean;
};

type NativeLinkRequest = {
  url: string;
  kind: "domain_app" | "external_url";
  label: string;
  fallbackUrl: string | null;
};

type LinkFailure = {
  title: string;
  message: string;
  fallbackUrl: string | null;
};

type ConnectionMode = "automatic" | "manual";

type ConnectionSettings = {
  mode: ConnectionMode;
  manualUrl: string | null;
};

function normalizeServerUrl(value: string): string {
  const candidate = value.trim().replace(/\/+$/, "");
  const withProtocol = /^https?:\/\//i.test(candidate)
    ? candidate
    : `http://${candidate}`;

  try {
    const parsed = new URL(withProtocol);
    if (
      !candidate ||
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password
    ) {
      return DEFAULT_SERVER_URL;
    }
    return parsed.toString().replace(/\/$/, "");
  } catch {
    return DEFAULT_SERVER_URL;
  }
}

function originOf(value: string): string | null {
  try {
    const parsed = new URL(value);
    return ["http:", "https:"].includes(parsed.protocol)
      ? parsed.origin
      : null;
  } catch {
    return null;
  }
}

function isConnectionMode(value: unknown): value is ConnectionMode {
  return value === "automatic" || value === "manual";
}

function connectionSettingsFrom(value: string | null): ConnectionSettings | null {
  if (!value) return null;
  try {
    const parsed: unknown = JSON.parse(value);
    if (!parsed || typeof parsed !== "object") return null;
    const record = parsed as Record<string, unknown>;
    if (!isConnectionMode(record.mode)) return null;
    return {
      mode: record.mode,
      manualUrl:
        typeof record.manualUrl === "string"
          ? normalizeServerUrl(record.manualUrl)
          : null,
    };
  } catch {
    return null;
  }
}

function isDefaultConnectionUrl(value: string): boolean {
  return value === DEFAULT_SERVER_URL || value === LAN_SERVER_URL;
}

async function canReachServer(url: string, timeoutMs = LAN_PROBE_TIMEOUT_MS): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${url}${HEALTH_PATH}`, {
      method: "GET",
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

function isCloudflareAccessNavigation(requestedUrl: URL, serverUrl: string): boolean {
  try {
    const server = new URL(serverUrl);
    if (server.protocol !== "https:" || !server.hostname.endsWith("nodaluna.com")) {
      return false;
    }
    return (
      requestedUrl.protocol === "https:" &&
      (requestedUrl.hostname.endsWith(".cloudflareaccess.com") ||
        CLOUDFLARE_ACCESS_HOSTS.has(requestedUrl.hostname))
    );
  } catch {
    return false;
  }
}

function recordOf(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object"
    ? (value as Record<string, unknown>)
    : null;
}

function safeWebUrl(value: unknown): string | null {
  if (typeof value !== "string") return null;
  try {
    const parsed = new URL(value.trim());
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password
    ) {
      return null;
    }
    return parsed.toString();
  } catch {
    return null;
  }
}

function safeAppUrl(value: unknown): string | null {
  if (typeof value !== "string") return null;
  try {
    const parsed = new URL(value.trim());
    if (
      !ALLOWED_APP_PROTOCOLS.has(parsed.protocol) ||
      parsed.username ||
      parsed.password
    ) {
      return null;
    }
    return value.trim();
  } catch {
    return null;
  }
}

function safeWebFallback(value: unknown): string | null {
  const candidate = recordOf(value);
  if (candidate) {
    return candidate.kind === "external_url"
      ? safeWebUrl(candidate.value)
      : null;
  }
  return safeWebUrl(value);
}

function nativeLinkRequest(value: Record<string, unknown>): NativeLinkRequest | null {
  const target = recordOf(value.target);
  if (!target) return null;

  const kind = target.kind;
  const url =
    kind === "domain_app"
      ? safeAppUrl(target.value)
      : kind === "external_url"
        ? safeWebUrl(target.value)
        : null;
  if (!url || (kind !== "domain_app" && kind !== "external_url")) return null;

  const messageFallback =
    value.fallback ?? value.fallback_url ?? value.fallbackUrl ?? value.web_url ?? value.webUrl;
  const targetFallback =
    target.fallback ??
    target.fallback_url ??
    target.fallbackUrl ??
    target.web_url ??
    target.webUrl;
  const fallbackUrl =
    safeWebFallback(targetFallback) ?? safeWebFallback(messageFallback);
  const rawLabel = target.label ?? value.label;

  return {
    url,
    kind,
    label:
      typeof rawLabel === "string" && rawLabel.trim()
        ? rawLabel.trim().slice(0, 100)
        : kind === "domain_app"
          ? "la aplicación de destino"
          : "el enlace externo",
    fallbackUrl,
  };
}

function speechLanguage(value: unknown): string {
  return typeof value === "string" &&
    /^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/i.test(value)
    ? value
    : DEFAULT_SPEECH_LANGUAGE;
}

function voiceRequestId(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 && value.length <= 128
    ? value
    : undefined;
}

export default function App() {
  const webViewRef = useRef<WebView>(null);
  const voiceSessionRef = useRef<VoiceSession | null>(null);
  const voiceGenerationRef = useRef(0);
  const linkAttemptRef = useRef(0);
  const mountedRef = useRef(true);
  const [serverUrl, setServerUrl] = useState(DEFAULT_SERVER_URL);
  const [draftUrl, setDraftUrl] = useState(DEFAULT_SERVER_URL);
  const [connectionMode, setConnectionMode] = useState<ConnectionMode>("automatic");
  const [draftConnectionMode, setDraftConnectionMode] =
    useState<ConnectionMode>("automatic");
  const [settingsVisible, setSettingsVisible] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);
  const [canGoBack, setCanGoBack] = useState(false);
  const [ready, setReady] = useState(false);
  const [webViewKey, setWebViewKey] = useState(0);
  const [linkFailure, setLinkFailure] = useState<LinkFailure | null>(null);

  const selectAutomaticServer = useCallback(async (): Promise<string> => {
    const lanIsAvailable = await canReachServer(LAN_SERVER_URL);
    return lanIsAvailable ? LAN_SERVER_URL : DEFAULT_SERVER_URL;
  }, []);

  const persistConnectionSettings = useCallback(async (settings: ConnectionSettings) => {
    await AsyncStorage.setItem(CONNECTION_SETTINGS_KEY, JSON.stringify(settings));
  }, []);

  const sendVoiceEvent = useCallback(
    (event: Partial<VoiceBridgeDetail> & Pick<VoiceBridgeDetail, "type" | "state">) => {
      const detail: VoiceBridgeDetail = {
        protocol: VOICE_PROTOCOL,
        transcript: "",
        isFinal: false,
        error: null,
        requestId: voiceSessionRef.current?.requestId,
        ...event,
      };
      const serialized = JSON.stringify(detail)
        .replace(/</g, "\\u003c")
        .replace(/\u2028/g, "\\u2028")
        .replace(/\u2029/g, "\\u2029");
      webViewRef.current?.injectJavaScript(
        `window.dispatchEvent(new CustomEvent("agent:native-voice", {detail:${serialized}}));true;`,
      );
    },
    [],
  );

  useSpeechRecognitionEvent("start", () => {
    const session = voiceSessionRef.current;
    if (!session || session.cancelled) return;
    session.phase = "listening";
    sendVoiceEvent({
      type: "speech.state",
      state: "listening",
      requestId: session.requestId,
    });
  });

  useSpeechRecognitionEvent("end", () => {
    const session = voiceSessionRef.current;
    if (!session) return;
    if (!session.suppressNativeEvents && !session.terminalError) {
      sendVoiceEvent({
        type: "speech.state",
        state: "idle",
        requestId: session.requestId,
      });
    }
    voiceSessionRef.current = null;
  });

  useSpeechRecognitionEvent("result", (event) => {
    const session = voiceSessionRef.current;
    if (!session || session.cancelled || session.suppressNativeEvents) return;
    sendVoiceEvent({
      type: "speech.result",
      state: event.isFinal ? "processing" : session.phase,
      transcript: event.results[0]?.transcript ?? "",
      isFinal: event.isFinal,
      requestId: session.requestId,
    });
  });

  useSpeechRecognitionEvent("error", (event) => {
    const session = voiceSessionRef.current;
    if (!session || session.suppressNativeEvents) return;
    session.terminalError = true;
    sendVoiceEvent({
      type: "speech.error",
      state: "error",
      error: event.message ? `${event.error}: ${event.message}` : event.error,
      requestId: session.requestId,
    });
  });

  useEffect(() => {
    Promise.all([
      AsyncStorage.getItem(CONNECTION_SETTINGS_KEY),
      AsyncStorage.getItem(SERVER_URL_KEY),
    ])
      .then(async ([savedSettings, savedUrl]) => {
        const settings = connectionSettingsFrom(savedSettings);
        if (settings) {
          const selectedUrl =
            settings.mode === "automatic"
              ? await selectAutomaticServer()
              : settings.manualUrl ?? DEFAULT_SERVER_URL;
          setConnectionMode(settings.mode);
          setDraftConnectionMode(settings.mode);
          setServerUrl(selectedUrl);
          setDraftUrl(settings.manualUrl ?? selectedUrl);
          return;
        }

        const normalizedLegacyUrl = savedUrl ? normalizeServerUrl(savedUrl) : DEFAULT_SERVER_URL;
        const migratedSettings: ConnectionSettings = isDefaultConnectionUrl(normalizedLegacyUrl)
          ? { mode: "automatic", manualUrl: null }
          : { mode: "manual", manualUrl: normalizedLegacyUrl };
        const selectedUrl =
          migratedSettings.mode === "automatic"
            ? await selectAutomaticServer()
            : normalizedLegacyUrl;
        await persistConnectionSettings(migratedSettings);
        setConnectionMode(migratedSettings.mode);
        setDraftConnectionMode(migratedSettings.mode);
        setServerUrl(selectedUrl);
        setDraftUrl(migratedSettings.manualUrl ?? selectedUrl);
      })
      .finally(() => setReady(true));
  }, [persistConnectionSettings, selectAutomaticServer]);

  const cancelSpeech = useCallback(
    (notifyPage = false) => {
      const session = voiceSessionRef.current;
      if (!session || session.cancelled) return;

      const wasAwaitingPermission = session.phase === "requesting-permission";
      voiceGenerationRef.current += 1;
      session.cancelled = true;
      session.suppressNativeEvents = true;
      session.phase = "cancelling";

      if (notifyPage && mountedRef.current) {
        sendVoiceEvent({
          type: "speech.state",
          state: "idle",
          requestId: session.requestId,
        });
      }

      if (wasAwaitingPermission) {
        voiceSessionRef.current = null;
        return;
      }

      try {
        ExpoSpeechRecognitionModule.abort();
      } catch {
        voiceSessionRef.current = null;
      }
    },
    [sendVoiceEvent],
  );

  const stopSpeech = useCallback(
    (requestId: string) => {
      const session = voiceSessionRef.current;
      if (!session) {
        sendVoiceEvent({ type: "speech.state", state: "idle", requestId });
        return;
      }
      if (session.requestId !== requestId) {
        sendVoiceEvent({
          type: "speech.error",
          state: "error",
          error: "La sesión de dictado indicada ya no está activa.",
          requestId,
        });
        return;
      }
      if (session.cancelled) {
        sendVoiceEvent({ type: "speech.state", state: "idle", requestId });
        return;
      }
      if (session.phase === "requesting-permission") {
        voiceGenerationRef.current += 1;
        session.cancelled = true;
        voiceSessionRef.current = null;
        sendVoiceEvent({ type: "speech.state", state: "idle", requestId });
        return;
      }

      session.phase = "stopping";
      sendVoiceEvent({ type: "speech.state", state: "stopping", requestId });
      try {
        ExpoSpeechRecognitionModule.stop();
      } catch (error) {
        session.terminalError = true;
        sendVoiceEvent({
          type: "speech.error",
          state: "error",
          error: error instanceof Error ? error.message : "No se pudo detener el dictado.",
          requestId,
        });
        session.cancelled = true;
        session.suppressNativeEvents = true;
        session.phase = "cancelling";
        try {
          ExpoSpeechRecognitionModule.abort();
        } catch {
          voiceSessionRef.current = null;
        }
      }
    },
    [sendVoiceEvent],
  );

  const startSpeech = useCallback(
    async (lang: string, requestId: string) => {
      if (voiceSessionRef.current) {
        sendVoiceEvent({
          type: "speech.error",
          state: "error",
          error: "Hay otro dictado activo o terminando. Intenta de nuevo en un instante.",
          requestId,
        });
        return;
      }

      const generation = voiceGenerationRef.current + 1;
      voiceGenerationRef.current = generation;
      const session: VoiceSession = {
        requestId,
        generation,
        phase: "requesting-permission",
        cancelled: false,
        suppressNativeEvents: false,
        terminalError: false,
      };
      voiceSessionRef.current = session;
      sendVoiceEvent({
        type: "speech.state",
        state: "requesting-permission",
        requestId,
      });
      try {
        const permission =
          await ExpoSpeechRecognitionModule.requestPermissionsAsync();
        if (
          !mountedRef.current ||
          voiceSessionRef.current !== session ||
          session.cancelled ||
          voiceGenerationRef.current !== generation
        ) {
          return;
        }
        if (!permission.granted) {
          sendVoiceEvent({
            type: "speech.error",
            state: "error",
            error: "El permiso de micrófono y reconocimiento de voz no fue concedido.",
            requestId,
          });
          voiceSessionRef.current = null;
          return;
        }

        session.phase = "starting";
        sendVoiceEvent({ type: "speech.state", state: "starting", requestId });
        ExpoSpeechRecognitionModule.start({
          lang,
          interimResults: true,
          continuous: false,
          // El audio se usa en vivo: no se activa recordingOptions.persist.
        });
      } catch (error) {
        if (voiceSessionRef.current !== session || session.cancelled) return;
        sendVoiceEvent({
          type: "speech.error",
          state: "error",
          error: error instanceof Error ? error.message : "No se pudo iniciar el dictado.",
          requestId,
        });
        voiceSessionRef.current = null;
      }
    },
    [sendVoiceEvent],
  );

  const openExternalLink = useCallback(async (link: NativeLinkRequest) => {
    const attempt = linkAttemptRef.current + 1;
    linkAttemptRef.current = attempt;
    setLinkFailure(null);

    try {
      const supported = await Linking.canOpenURL(link.url);
      if (!mountedRef.current || linkAttemptRef.current !== attempt) return;
      if (!supported) {
        setLinkFailure({
          title: "No hay una app compatible",
          message:
            link.kind === "domain_app"
              ? `Instala o habilita ${link.label} para abrir este destino.`
              : `No encontramos un navegador capaz de abrir ${link.label}.`,
          fallbackUrl: link.fallbackUrl,
        });
        return;
      }

      await Linking.openURL(link.url);
    } catch {
      if (!mountedRef.current || linkAttemptRef.current !== attempt) return;
      setLinkFailure({
        title: "No se pudo abrir el enlace",
        message:
          link.kind === "domain_app"
            ? `Android no pudo abrir ${link.label}. Comprueba que la app esté instalada y actualizada.`
            : `Android no pudo entregar ${link.label} al navegador. Intenta nuevamente.`,
        fallbackUrl: link.fallbackUrl,
      });
    }
  }, []);

  const handleWebMessage = useCallback(
    (event: WebViewMessageEvent) => {
      let message: unknown;
      try {
        message = JSON.parse(event.nativeEvent.data);
      } catch {
        return;
      }
      if (!message || typeof message !== "object") return;
      if (originOf(event.nativeEvent.url) !== originOf(serverUrl)) return;

      const request = message as Record<string, unknown>;
      if (request.protocol === LINK_PROTOCOL) {
        if (request.type !== "link.open") return;
        const link = nativeLinkRequest(request);
        if (link) void openExternalLink(link);
        return;
      }
      if (request.protocol !== VOICE_PROTOCOL) return;
      const requestId = voiceRequestId(request.requestId);
      if (!requestId) return;

      if (
        request.type === "speech.start" ||
        request.type === "voice.start" ||
        request.type === "voice:start"
      ) {
        void startSpeech(speechLanguage(request.lang), requestId);
      } else if (
        request.type === "speech.stop" ||
        request.type === "voice.stop" ||
        request.type === "voice:stop"
      ) {
        stopSpeech(requestId);
      }
      // Otros tipos versionados (por ejemplo speech.play futuro) se ignoran de forma segura.
    },
    [openExternalLink, serverUrl, startSpeech, stopSpeech],
  );

  useEffect(() => {
    mountedRef.current = true;
    const appStateSubscription = AppState.addEventListener("change", (nextState) => {
      if (nextState === "background") {
        cancelSpeech(true);
        return;
      }
      if (nextState === "active" && connectionMode === "automatic") {
        void selectAutomaticServer().then((selectedUrl) => {
          if (!mountedRef.current) return;
          setServerUrl((currentUrl: string) => {
            if (currentUrl === selectedUrl) return currentUrl;
            setLoadFailed(false);
            setLoading(true);
            setWebViewKey((current) => current + 1);
            return selectedUrl;
          });
        });
      }
    });
    return () => {
      mountedRef.current = false;
      appStateSubscription.remove();
      cancelSpeech(false);
    };
  }, [cancelSpeech, connectionMode, selectAutomaticServer]);

  useEffect(() => {
    const subscription = BackHandler.addEventListener("hardwareBackPress", () => {
      if (linkFailure) {
        setLinkFailure(null);
        return true;
      }
      if (settingsVisible) {
        setSettingsVisible(false);
        return true;
      }
      if (canGoBack) {
        cancelSpeech(false);
        webViewRef.current?.goBack();
        return true;
      }
      return false;
    });
    return () => subscription.remove();
  }, [canGoBack, cancelSpeech, linkFailure, settingsVisible]);

  const reload = useCallback(() => {
    cancelSpeech(false);
    setLoadFailed(false);
    setLoading(true);
    if (connectionMode === "automatic") {
      void selectAutomaticServer().then((selectedUrl) => {
        if (!mountedRef.current) return;
        setServerUrl(selectedUrl);
        setWebViewKey((current) => current + 1);
      });
      return;
    }
    setWebViewKey((current) => current + 1);
  }, [cancelSpeech, connectionMode, selectAutomaticServer]);

  const saveServerUrl = useCallback(async () => {
    const settings: ConnectionSettings =
      draftConnectionMode === "automatic"
        ? { mode: "automatic", manualUrl: null }
        : { mode: "manual", manualUrl: normalizeServerUrl(draftUrl) };
    const selectedUrl =
      settings.mode === "automatic"
        ? await selectAutomaticServer()
        : settings.manualUrl ?? DEFAULT_SERVER_URL;
    await persistConnectionSettings(settings);
    await AsyncStorage.setItem(SERVER_URL_KEY, selectedUrl);
    setConnectionMode(settings.mode);
    setDraftConnectionMode(settings.mode);
    setServerUrl(selectedUrl);
    setDraftUrl(settings.manualUrl ?? selectedUrl);
    setSettingsVisible(false);
    cancelSpeech(false);
    setLoadFailed(false);
    setLoading(true);
    setWebViewKey((current) => current + 1);
  }, [
    cancelSpeech,
    draftConnectionMode,
    draftUrl,
    persistConnectionSettings,
    selectAutomaticServer,
  ]);

  const shouldStartLoad = useCallback(
    (request: { url: string }) => {
      if (request.url === "about:blank") return true;

      let requestedUrl: URL;
      try {
        requestedUrl = new URL(request.url);
      } catch {
        return false;
      }

      if (["http:", "https:"].includes(requestedUrl.protocol)) {
        if (
          requestedUrl.origin === originOf(serverUrl) ||
          isCloudflareAccessNavigation(requestedUrl, serverUrl)
        ) {
          return true;
        }
        const url = safeWebUrl(request.url);
        if (url) {
          void openExternalLink({
            url,
            kind: "external_url",
            label: "el enlace externo",
            fallbackUrl: null,
          });
        }
        return false;
      }

      if (ALLOWED_APP_PROTOCOLS.has(requestedUrl.protocol)) {
        const url = safeAppUrl(request.url);
        if (url) {
          void openExternalLink({
            url,
            kind: "domain_app",
            label: "la aplicación de destino",
            fallbackUrl: null,
          });
        }
      }
      return false;
    },
    [openExternalLink, serverUrl],
  );
  const allowedWebOrigin = originOf(serverUrl);

  if (!ready) {
    return (
      <SafeAreaView style={styles.splash}>
        <StatusBar style="light" backgroundColor="#080c0a" />
        <View style={styles.agentMark}>
          <Text style={styles.moonGlyph}>◐</Text>
        </View>
        <View style={styles.splashWords}>
          <Text style={styles.splashTitle}>Granja Luna</Text>
          <Text style={styles.splashSubtitle}>Operación viva, siempre trazable</Text>
        </View>
        <ActivityIndicator color="#e5c86b" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" backgroundColor="#080c0a" />
      <View style={styles.toolbar}>
        <View style={styles.identity}>
          <View style={styles.compactMark}>
            <Text style={styles.compactMoon}>◐</Text>
          </View>
          <View>
            <Text style={styles.title}>Granja Luna</Text>
            <View style={styles.statusLine}>
              <View
                style={[
                  styles.connectionDot,
                  loadFailed ? styles.connectionDotFailed : undefined,
                ]}
              />
              <Text style={styles.statusText}>
                {loadFailed ? "Sin conexión" : loading ? "Conectando" : "Operativa"}
              </Text>
            </View>
          </View>
        </View>
        <View style={styles.toolbarActions}>
          <Pressable
            accessibilityLabel="Recargar"
            android_ripple={{ color: "#34301e", borderless: true }}
            onPress={reload}
            style={styles.iconButton}
          >
            <Text style={styles.iconText}>↻</Text>
          </Pressable>
          <Pressable
            accessibilityLabel="Configurar servidor"
            android_ripple={{ color: "#34301e", borderless: true }}
            onPress={() => {
              cancelSpeech(true);
              setDraftUrl(serverUrl);
              setDraftConnectionMode(connectionMode);
              setSettingsVisible(true);
            }}
            style={styles.iconButton}
          >
            <Text style={styles.settingsIcon}>•••</Text>
          </Pressable>
        </View>
      </View>

      <View style={styles.webContainer}>
        <WebView
          key={webViewKey}
          ref={webViewRef}
          source={{ uri: serverUrl }}
          style={styles.webView}
          injectedJavaScriptBeforeContentLoaded={NATIVE_SHELL_SCRIPT}
          injectedJavaScript={NATIVE_SHELL_SCRIPT}
          javaScriptEnabled
          domStorageEnabled
          thirdPartyCookiesEnabled
          sharedCookiesEnabled
          cacheEnabled={false}
          pullToRefreshEnabled
          setSupportMultipleWindows={false}
          javaScriptCanOpenWindowsAutomatically={false}
          allowFileAccess={false}
          allowUniversalAccessFromFileURLs={false}
          mixedContentMode="never"
          originWhitelist={[
            ...(allowedWebOrigin ? [allowedWebOrigin] : []),
            "https://*.cloudflareaccess.com",
            "https://dash.cloudflare.com",
            "https://oidc.iam.cfapi.net",
            "personal-agent://*",
            "granja-luna://*",
          ]}
          onMessage={handleWebMessage}
          onShouldStartLoadWithRequest={shouldStartLoad}
          onNavigationStateChange={(navigation: WebViewNavigation) => setCanGoBack(navigation.canGoBack)}
          onLoadStart={() => {
            cancelSpeech(false);
            setLoading(true);
            setLoadFailed(false);
          }}
          onLoadEnd={() => setLoading(false)}
          onError={() => {
            setLoading(false);
            setLoadFailed(true);
          }}
          onHttpError={({ nativeEvent }) => {
            if (nativeEvent.statusCode >= 400) setLoadFailed(true);
          }}
          onContentProcessDidTerminate={reload}
        />
        {loading ? (
          <View pointerEvents="none" style={styles.loadingOverlay}>
            <ActivityIndicator color="#e5c86b" size="large" />
            <Text style={styles.loadingText}>Abriendo la operación</Text>
          </View>
        ) : null}
        {loadFailed ? (
          <View style={styles.errorOverlay}>
            <View style={styles.errorMark}>
              <Text style={styles.errorMarkText}>!</Text>
            </View>
            <Text style={styles.errorTitle}>No pudimos conectar</Text>
            <Text style={styles.errorCopy}>
              Verifica tu conexión a Internet y que el servidor de Granja Luna esté encendido.
            </Text>
            <Text selectable style={styles.serverAddress}>{serverUrl}</Text>
            <Pressable onPress={reload} style={styles.primaryButton}>
              <Text style={styles.primaryButtonText}>Volver a intentar</Text>
            </Pressable>
            <Pressable
              onPress={() => {
                cancelSpeech(true);
                setDraftUrl(serverUrl);
                setDraftConnectionMode(connectionMode);
                setSettingsVisible(true);
              }}
              style={styles.secondaryButton}
            >
              <Text style={styles.secondaryButtonText}>Cambiar servidor</Text>
            </Pressable>
          </View>
        ) : null}
      </View>

      <Modal
        animationType="fade"
        transparent
        visible={linkFailure !== null}
        onRequestClose={() => setLinkFailure(null)}
      >
        <View style={styles.modalBackdrop}>
          <View accessibilityViewIsModal style={styles.modalCard}>
            <View style={styles.modalHandle} />
            <Text style={styles.linkErrorEyebrow}>ENLACE NO DISPONIBLE</Text>
            <Text accessibilityRole="header" style={styles.modalTitle}>
              {linkFailure?.title}
            </Text>
            <Text style={styles.modalCopy}>{linkFailure?.message}</Text>
            <View style={styles.modalActions}>
              <Pressable
                accessibilityRole="button"
                onPress={() => setLinkFailure(null)}
                style={
                  linkFailure?.fallbackUrl
                    ? styles.secondaryButtonCompact
                    : styles.primaryButtonCompact
                }
              >
                <Text
                  style={
                    linkFailure?.fallbackUrl
                      ? styles.secondaryButtonText
                      : styles.primaryButtonText
                  }
                >
                  Cerrar
                </Text>
              </Pressable>
              {linkFailure?.fallbackUrl ? (
                <Pressable
                  accessibilityRole="link"
                  onPress={() => {
                    const url = linkFailure.fallbackUrl;
                    if (!url) return;
                    void openExternalLink({
                      url,
                      kind: "external_url",
                      label: "la versión web",
                      fallbackUrl: null,
                    });
                  }}
                  style={styles.primaryButtonCompact}
                >
                  <Text style={styles.primaryButtonText}>Abrir versión web</Text>
                </Pressable>
              ) : null}
            </View>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="fade"
        transparent
        visible={settingsVisible}
        onRequestClose={() => setSettingsVisible(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHandle} />
            <Text style={styles.modalEyebrow}>CONEXIÓN</Text>
            <Text style={styles.modalTitle}>Servidor de Granja Luna</Text>
            <Text style={styles.modalCopy}>
              Automática usa la red local en casa y el acceso seguro por Internet fuera de ella.
            </Text>
            <View style={styles.connectionModeOptions}>
              <Pressable
                accessibilityRole="button"
                accessibilityState={{ selected: draftConnectionMode === "automatic" }}
                onPress={() => setDraftConnectionMode("automatic")}
                style={[
                  styles.connectionModeOption,
                  draftConnectionMode === "automatic"
                    ? styles.connectionModeOptionSelected
                    : undefined,
                ]}
              >
                <Text
                  style={[
                    styles.connectionModeOptionText,
                    draftConnectionMode === "automatic"
                      ? styles.connectionModeOptionTextSelected
                      : undefined,
                  ]}
                >
                  Automática
                </Text>
              </Pressable>
              <Pressable
                accessibilityRole="button"
                accessibilityState={{ selected: draftConnectionMode === "manual" }}
                onPress={() => setDraftConnectionMode("manual")}
                style={[
                  styles.connectionModeOption,
                  draftConnectionMode === "manual"
                    ? styles.connectionModeOptionSelected
                    : undefined,
                ]}
              >
                <Text
                  style={[
                    styles.connectionModeOptionText,
                    draftConnectionMode === "manual"
                      ? styles.connectionModeOptionTextSelected
                      : undefined,
                  ]}
                >
                  Manual
                </Text>
              </Pressable>
            </View>
            {draftConnectionMode === "manual" ? (
            <TextInput
              accessibilityLabel="Dirección del servidor"
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="url"
              onChangeText={setDraftUrl}
              placeholder="https://granja.nodaluna.com"
              placeholderTextColor="#89958d"
              selectTextOnFocus
              style={styles.input}
              value={draftUrl}
            />
            ) : (
              <Text style={styles.connectionModeHint}>
                En casa: {LAN_SERVER_URL}\nFuera: {DEFAULT_SERVER_URL}
              </Text>
            )}
            <View style={styles.modalActions}>
              <Pressable
                onPress={() => setSettingsVisible(false)}
                style={styles.secondaryButtonCompact}
              >
                <Text style={styles.secondaryButtonText}>Cancelar</Text>
              </Pressable>
              <Pressable onPress={saveServerUrl} style={styles.primaryButtonCompact}>
                <Text style={styles.primaryButtonText}>Guardar</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: NativeStatusBar.currentHeight ?? 0,
    backgroundColor: "#080c0a",
  },
  splash: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 18,
    paddingTop: NativeStatusBar.currentHeight ?? 0,
    backgroundColor: "#080c0a",
  },
  agentMark: {
    width: 76,
    height: 76,
    borderRadius: 27,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#756737",
    backgroundColor: "#282419",
  },
  moonGlyph: { color: "#f1d985", fontSize: 36, fontWeight: "700" },
  splashWords: { alignItems: "center", gap: 4 },
  splashTitle: { color: "#f4f5ee", fontSize: 24, fontWeight: "800" },
  splashSubtitle: { color: "#89958d", fontSize: 14 },
  toolbar: {
    minHeight: 58,
    paddingHorizontal: 14,
    paddingVertical: 7,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "#0a100c",
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#29342d",
  },
  identity: { flexDirection: "row", alignItems: "center", gap: 10 },
  compactMark: {
    width: 36,
    height: 36,
    borderRadius: 13,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#675c35",
    backgroundColor: "#242116",
  },
  compactMoon: { color: "#ecd477", fontSize: 20, fontWeight: "700" },
  title: { color: "#f4f5ee", fontSize: 15, fontWeight: "800" },
  statusLine: { marginTop: 2, flexDirection: "row", alignItems: "center", gap: 5 },
  connectionDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: "#65d69e" },
  connectionDotFailed: { backgroundColor: "#ff8a7a" },
  statusText: { color: "#89958d", fontSize: 11, fontWeight: "600" },
  toolbarActions: { flexDirection: "row", gap: 2 },
  iconButton: { width: 44, height: 44, alignItems: "center", justifyContent: "center", borderRadius: 15 },
  iconText: { color: "#acb5ad", fontSize: 23 },
  settingsIcon: { color: "#acb5ad", fontSize: 17, fontWeight: "800", letterSpacing: 1, transform: [{ translateY: -3 }] },
  webContainer: { flex: 1, backgroundColor: "#080c0a" },
  webView: { flex: 1, backgroundColor: "#080c0a" },
  loadingOverlay: { ...StyleSheet.absoluteFillObject, alignItems: "center", justifyContent: "center", gap: 14, backgroundColor: "#080c0a" },
  loadingText: { color: "#89958d", fontSize: 13, letterSpacing: 0.2 },
  errorOverlay: { ...StyleSheet.absoluteFillObject, alignItems: "center", justifyContent: "center", paddingHorizontal: 30, backgroundColor: "#080c0a" },
  errorMark: { width: 50, height: 50, marginBottom: 18, alignItems: "center", justifyContent: "center", borderRadius: 18, borderWidth: 1, borderColor: "#743f3c", backgroundColor: "#281615" },
  errorMarkText: { color: "#ff9a8e", fontSize: 22, fontWeight: "800" },
  errorTitle: { color: "#f4f5ee", fontSize: 23, fontWeight: "800" },
  errorCopy: { maxWidth: 340, marginTop: 10, color: "#89958d", fontSize: 15, lineHeight: 22, textAlign: "center" },
  serverAddress: { marginTop: 13, marginBottom: 22, color: "#e5c86b", fontSize: 13 },
  primaryButton: { minWidth: 176, paddingHorizontal: 18, paddingVertical: 13, alignItems: "center", borderRadius: 14, backgroundColor: "#e5c86b" },
  primaryButtonCompact: { minWidth: 104, paddingHorizontal: 18, paddingVertical: 12, alignItems: "center", borderRadius: 13, backgroundColor: "#e5c86b" },
  primaryButtonText: { color: "#17150b", fontSize: 15, fontWeight: "800" },
  secondaryButton: { minWidth: 176, marginTop: 10, paddingHorizontal: 18, paddingVertical: 13, alignItems: "center", borderRadius: 14, borderWidth: 1, borderColor: "#303d34", backgroundColor: "#101713" },
  secondaryButtonCompact: { minWidth: 104, paddingHorizontal: 18, paddingVertical: 12, alignItems: "center", borderRadius: 13, borderWidth: 1, borderColor: "#303d34", backgroundColor: "#101713" },
  secondaryButtonText: { color: "#c8d0c9", fontSize: 15, fontWeight: "700" },
  modalBackdrop: { flex: 1, justifyContent: "flex-end", padding: 12, backgroundColor: "rgba(1, 4, 2, 0.8)" },
  modalCard: { paddingHorizontal: 20, paddingTop: 12, paddingBottom: 22, borderRadius: 24, borderWidth: 1, borderColor: "#334036", backgroundColor: "#111914" },
  modalHandle: { width: 38, height: 4, marginBottom: 18, alignSelf: "center", borderRadius: 2, backgroundColor: "#3a463e" },
  modalEyebrow: { color: "#e5c86b", fontSize: 11, fontWeight: "800", letterSpacing: 1.4 },
  linkErrorEyebrow: { color: "#ff9a8e", fontSize: 11, fontWeight: "800", letterSpacing: 1.4 },
  modalTitle: { marginTop: 5, color: "#f4f5ee", fontSize: 21, fontWeight: "800" },
  modalCopy: { marginTop: 8, color: "#89958d", fontSize: 14, lineHeight: 20 },
  input: { marginTop: 18, paddingHorizontal: 14, paddingVertical: 13, color: "#f0f3ed", fontSize: 15, borderRadius: 14, borderWidth: 1, borderColor: "#39473d", backgroundColor: "#090e0b" },
  connectionModeOptions: { marginTop: 18, flexDirection: "row", gap: 10 },
  connectionModeOption: { flex: 1, alignItems: "center", paddingVertical: 12, borderRadius: 13, borderWidth: 1, borderColor: "#39473d", backgroundColor: "#090e0b" },
  connectionModeOptionSelected: { borderColor: "#e5c86b", backgroundColor: "#282419" },
  connectionModeOptionText: { color: "#aeb8b0", fontSize: 14, fontWeight: "700" },
  connectionModeOptionTextSelected: { color: "#f1d985" },
  connectionModeHint: { marginTop: 18, color: "#aeb8b0", fontSize: 12, lineHeight: 19 },
  modalActions: { marginTop: 20, flexDirection: "row", justifyContent: "flex-end", gap: 10 },
});
