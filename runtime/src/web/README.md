# Web local

Estado: `mvp_remote_pwa`

Aplicación responsive disponible por LAN y, detrás de Cloudflare Access, en
`https://granja.nodaluna.com`. Incluye manifiesto y service worker para instalarla como PWA desde
Chrome y conservar el flujo de identidad del navegador.

## Desarrollo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r runtime/requirements-dev.txt
uvicorn runtime.src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

Desde la computadora: `http://127.0.0.1:8000`.

Desde el celular: `http://IP_LOCAL_DE_LA_COMPUTADORA:8000`.

La pestaña `Contenido` muestra la ruta activa y permite cambiar entre `LAN rápida` e `Internet`.
El cambio navega toda la aplicación al otro origen porque un sitio HTTPS no puede subir archivos a
un endpoint HTTP privado mediante una petición mixta. Una carga activa nunca se interrumpe; si hay
archivos todavía sin subir, el navegador avisa que deberán seleccionarse de nuevo.

Una tanda interrumpida aparece en `Subidas recientes` con la acción `Reanudar`. El usuario puede
elegir nuevamente todos los archivos originales: la interfaz compara nombre y tamaño, omite los ya
guardados y transmite sólo los pendientes dentro de la misma tanda.

`Contenido` también muestra los MP4 de revisión guardados junto al estado persistente del Estudio.
El navegador los reproduce por rangos, sin copiar ni servir los originales de `media/inbox`. La
ruta remota conserva la protección de Cloudflare Access. La ruta LAN sólo está aislada por la red
local hasta que exista autenticación propia de la plataforma.

Las URLs pueden ajustarse al iniciar el runtime:

```env
GRANJA_LUNA_LAN_URL=http://192.168.18.15:8011
GRANJA_LUNA_REMOTE_URL=https://granja.nodaluna.com
```

## QA de navegador

```bash
npm install
npx playwright install chromium
npm run test:e2e
```

Playwright usa estado temporal y verifica el flujo de una compra con multiples items en telefono y escritorio. No escribe entradas de prueba en el inbox local.

## Estado local

- `runtime/state/inbox.jsonl`
- `runtime/state/usage-events.jsonl`

Ambos archivos estan ignorados por git.

## Limite actual

La UI acepta dictado directo mediante el puente nativo `agent.voice.v1` del APK. En un navegador compatible también usa Web Speech como respaldo, sujeto a HTTPS y a las políticas del navegador. El texto transcrito queda editable y nunca se envía automáticamente. El audio no se persiste en la aplicación; el reconocedor del sistema puede usar servicios de red de su proveedor.

La respuesta hablada no forma parte de este corte. Si se incorpora, usará un protocolo separado (`agent.audio.v1`), reproducción manual por defecto y exclusión mutua con el micrófono.
