# Granja Luna Mobile 0.2.0

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

La URL predeterminada es `http://192.168.18.15:8011`. Puede cambiarse desde el botón de configuración
o al compilar con `EXPO_PUBLIC_GRANJA_LUNA_URL=http://IP_DEL_SERVIDOR:8011`.

El artefacto local para pruebas queda en `mobile/artifacts/Granja-Luna-0.2.0.apk`. El build actual
usa el certificado Android Debug; para publicar se debe configurar una clave de release privada.
