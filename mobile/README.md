# Granja Luna Mobile 0.3.2

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

El modo de conexión predeterminado es **Automática**: prueba primero la LAN
`http://192.168.18.15:8011` y, si no está disponible, usa
`https://granja.nodaluna.com`, protegida por Cloudflare Access. Al volver a primer plano la app vuelve
a comprobar la LAN, por lo que puede regresar a la conexión local al volver a casa. Las instalaciones
anteriores configuradas con una de esas dos direcciones se migran a este modo; una URL personalizada
se conserva como modo manual.

El WebView permite solamente el origen activo y los dominios HTTPS oficiales que participan en el
flujo de autenticación de Cloudflare Access.

Con el perímetro actual, Google completa el login en Chrome y la cookie no vuelve automáticamente al
WebView. Por eso la PWA instalada desde Chrome es el cliente remoto recomendado por ahora; este APK
continúa siendo útil para desarrollo, enlaces profundos y futuras capacidades nativas. El diseño
objetivo para una publicación formal es OAuth/OIDC con Authorization Code y PKCE.

Puede cambiarse desde el botón de configuración: **Automática** conserva LAN + Internet; **Manual**
permite indicar otra dirección. Al compilar, se pueden sobrescribir `EXPO_PUBLIC_GRANJA_LUNA_URL`
para Internet y `EXPO_PUBLIC_GRANJA_LUNA_LAN_URL` para LAN.

El artefacto local para pruebas queda en `mobile/artifacts/Granja-Luna-0.3.2.apk`. El build actual
usa el certificado Android Debug; para publicar se debe configurar una clave de release privada.
