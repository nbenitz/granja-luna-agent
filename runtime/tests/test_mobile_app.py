import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class MobileAppTests(unittest.TestCase):
    def test_android_shell_has_distinct_identity_and_deep_link(self) -> None:
        app_config = json.loads(
            (PROJECT_ROOT / "mobile" / "app.json").read_text(encoding="utf-8")
        )
        expo = app_config["expo"]

        self.assertEqual(expo["name"], "Granja Luna")
        self.assertEqual(expo["scheme"], "granja-luna")
        self.assertEqual(expo["version"], "0.2.0")
        self.assertEqual(expo["android"]["package"], "com.nestorbenitez.granjaluna")
        self.assertEqual(
            set(expo["android"]["permissions"]),
            {"INTERNET", "android.permission.RECORD_AUDIO"},
        )
        self.assertTrue(
            any(
                plugin == "expo-speech-recognition"
                or (isinstance(plugin, list) and plugin[0] == "expo-speech-recognition")
                for plugin in expo["plugins"]
            )
        )

    def test_android_shell_loads_only_its_configured_runtime_origin(self) -> None:
        app_source = (PROJECT_ROOT / "mobile" / "App.tsx").read_text(encoding="utf-8")

        self.assertIn("EXPO_PUBLIC_GRANJA_LUNA_URL", app_source)
        self.assertIn('"http://192.168.18.15:8011"', app_source)
        self.assertIn("requestedUrl.origin === originOf(serverUrl)", app_source)
        self.assertIn('new Set(["personal-agent:", "granja-luna:"])', app_source)
        self.assertIn(
            "injectedJavaScriptBeforeContentLoaded={NATIVE_SHELL_SCRIPT}", app_source
        )
        self.assertIn("injectedJavaScript={NATIVE_SHELL_SCRIPT}", app_source)
        self.assertIn("cacheEnabled={false}", app_source)

    def test_android_shell_has_editable_non_persistent_voice_bridge(self) -> None:
        app_source = (PROJECT_ROOT / "mobile" / "App.tsx").read_text(encoding="utf-8")
        app_config = json.loads(
            (PROJECT_ROOT / "mobile" / "app.json").read_text(encoding="utf-8")
        )

        self.assertIn("ExpoSpeechRecognitionModule.requestPermissionsAsync()", app_source)
        self.assertIn('const VOICE_PROTOCOL = "agent.voice.v1"', app_source)
        self.assertIn("protocol: VOICE_PROTOCOL", app_source)
        self.assertIn('new CustomEvent("agent:native-voice"', app_source)
        self.assertIn("onMessage={handleWebMessage}", app_source)
        self.assertNotIn("recordingOptions:", app_source)
        self.assertIn(
            "android.permission.RECORD_AUDIO",
            app_config["expo"]["android"]["permissions"],
        )

    def test_android_shell_reports_link_failures_and_supports_web_fallback(self) -> None:
        app_source = (PROJECT_ROOT / "mobile" / "App.tsx").read_text(encoding="utf-8")
        app_config = json.loads(
            (PROJECT_ROOT / "mobile" / "app.json").read_text(encoding="utf-8")
        )
        config_plugin = (
            PROJECT_ROOT / "mobile" / "plugins" / "withCleartextTraffic.js"
        ).read_text(encoding="utf-8")

        self.assertIn('const LINK_PROTOCOL = "agent.link.v1"', app_source)
        self.assertIn('request.type !== "link.open"', app_source)
        self.assertIn('kind: "domain_app" | "external_url"', app_source)
        self.assertIn("target.fallback_url", app_source)
        self.assertIn("Linking.canOpenURL(link.url)", app_source)
        self.assertIn("No hay una app compatible", app_source)
        self.assertIn("Abrir versión web", app_source)
        self.assertNotIn("catch(() => undefined)", app_source)
        self.assertIn("./plugins/withCleartextTraffic", app_config["expo"]["plugins"])
        for scheme in ("http", "https", "personal-agent", "granja-luna"):
            self.assertIn(f'"{scheme}"', config_plugin)

    def test_pwa_renders_safe_typed_links_and_editable_voice_input(self) -> None:
        app_source = (
            PROJECT_ROOT / "runtime" / "src" / "web" / "static" / "app.js"
        ).read_text(encoding="utf-8")
        index_source = (
            PROJECT_ROOT / "runtime" / "src" / "web" / "static" / "index.html"
        ).read_text(encoding="utf-8")

        self.assertIn("function safeTypedLink(kind, value)", app_source)
        self.assertIn('data-ui-route="${escapeHtml(link.route)}"', app_source)
        self.assertIn("parsed.username || parsed.password", app_source)
        self.assertIn("window.ReactNativeWebView.postMessage", app_source)
        self.assertIn('type: "speech.start"', app_source)
        self.assertIn('window.addEventListener("agent:native-voice"', app_source)
        self.assertIn('id="voice-button"', index_source)


if __name__ == "__main__":
    unittest.main()
