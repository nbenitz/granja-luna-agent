# Granja Luna Mobile 0.3.1

Cliente Android de Granja Luna construido con Expo/React Native. Es un shell nativo deliberadamente
pequeño: carga la PWA del runtime en un `WebView`, permite cambiar la URL del servidor y registra el
enlace profundo `granja-luna://open` para recibir navegación desde Personal Agent.

La aplicación no copia datos operativos ni reglas del dominio. Granja Luna continúa siendo la fuente
de verdad y el APK solo presenta su interfaz.

El shell implementa dictado con el puente versionado `agent.voice.v1`: solicita `RECORD_AUDIO`
únicamente al tocar el micrófono, devuelve texto parcial/final a la PWA y nunca persiste audio ni
envía el mensaje automáticamente. La navegación permanece dentro del origen configurado y solo
delega enlaces web o los esquemas conocidos `personal-agent:` y `granja-luna:`.

La respuesta hablada se mantiene como una extensión futura separada. Antes de implementarla se
deben definir reproducción manual o automática, voz, velocidad, interrupciones y privacidad.

## Desarrollo y APK local

```bash
cd mobile
npm install
npm run typecheck
npm run prebuild:android
cd android
./gradlew app:assembleRelease
```

La URL predeterminada es `https://granja.nodaluna.com`, protegida por Cloudflare Access. El WebView
permite solamente el origen configurado y los dominios HTTPS oficiales que participan en ese flujo
de autenticación. Una instalación anterior que todavía conserve la dirección local predeterminada
se migra automáticamente; las URLs personalizadas se respetan.

Con el perímetro actual, Google completa el login en Chrome y la cookie no vuelve automáticamente al
WebView. Por eso la PWA instalada desde Chrome es el cliente remoto recomendado por ahora; este APK
continúa siendo útil para desarrollo, enlaces profundos y futuras capacidades nativas. El diseño
objetivo para una publicación formal es OAuth/OIDC con Authorization Code y PKCE.

Puede cambiarse desde el botón de configuración o al compilar con
`EXPO_PUBLIC_GRANJA_LUNA_URL=http://IP_DEL_SERVIDOR:8011` para una prueba LAN.

El artefacto local para pruebas queda en `mobile/artifacts/Granja-Luna-0.3.1.apk`. El build actual
usa el certificado Android Debug; para publicar se debe configurar una clave de release privada.
