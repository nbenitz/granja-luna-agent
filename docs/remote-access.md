# Acceso remoto seguro

Estado: `active — verified 2026-08-10`

## Decisión

Publicar las interfaces privadas en `https://granja.nodaluna.com` y
`https://app.nodaluna.com` mediante un único Cloudflare Tunnel y Cloudflare Access. El túnel inicia
conexiones salientes y evita depender de una IPv4 pública, DDNS tradicional o reglas de entrada en
el router.

No se debe habilitar DMZ ni publicar directamente el puerto `8011`. La aplicación no implementa
todavía autenticación propia; el hostname remoto debe permanecer detrás de una política Access.

## Estado verificado

- Porkbun conserva el registro y usa los nameservers autoritativos de Cloudflare.
- Los registros de correo y SPF anteriores se conservaron.
- El túnel administrado `nodaluna-home` mantiene rutas hacia Granja Luna y Personal Agent.
- Ambas rutas están protegidas por la política Access `Solo Néstor` antes de llegar al origen.
- Granja Luna respondió de extremo a extremo en `https://granja.nodaluna.com` después de autenticar.
- Personal Agent respondió de extremo a extremo en `https://app.nodaluna.com` después de autenticar.
- Android alcanzó ambos hostnames y recibió el desafío Access mediante depuración inalámbrica.
- Los APK `Granja Luna 0.3.1` y `Personal Agent 0.4.1` quedaron instalados con las URLs remotas y
  migración del valor LAN anterior. El desafío propio de Access puede navegar dentro de los
  WebView; al elegir Google, la autenticación continúa en Chrome y no comparte su cookie de sesión
  con el WebView.
- Las PWA de Personal Agent y Granja Luna quedaron instaladas y verificadas en Android en modo
  independiente. Comparten la sesión segura de Chrome y son el cliente remoto recomendado mientras
  se diseña el login OIDC/OAuth propio de Nodaluna.
- El conector se reinició de forma controlada, recuperó cuatro conexiones QUIC y volvió a pasar
  todas las comprobaciones de red.
- Docker está habilitado al arrancar la PC; los servicios usan `restart: unless-stopped`.

## Despliegue

El servicio de dominio continúa dentro del proyecto Compose `personal-agent-platform`. El archivo
[`../deploy/cloudflare-tunnel.compose.yml`](../deploy/cloudflare-tunnel.compose.yml) añade
`cloudflared` al mismo proyecto y red interna, sin exponer puertos nuevos.

1. Crear un túnel administrado remotamente en Cloudflare con el nombre `nodaluna-home`.
2. Configurar el hostname público `granja.nodaluna.com` con origen `http://granja:8011`.
3. Configurar `app.nodaluna.com` con origen `http://api:8090`.
4. Crear primero una aplicación Access por hostname que permita únicamente la identidad aprobada
   por Néstor.
5. No incluir MCP (`8091`), Career Agent (`8021`), Chroma, PostgreSQL ni AI Interview Coach en el
   túnel.
6. Copiar `deploy/cloudflare-tunnel.env.example` como `.env.cloudflare` y guardar allí el token.
7. Levantar la composición desde este repo:

```bash
docker compose \
  --env-file .env.cloudflare \
  -f ../personal-agent-platform/docker-compose.yml \
  -f deploy/cloudflare-tunnel.compose.yml \
  up -d --build api granja cloudflared
```

La regla `restart: unless-stopped` conserva los servicios tras reinicios. Granja Luna comprueba
`/api/health`, Personal Agent comprueba `/healthz` y `cloudflared` espera a que ambos controles estén
sanos.

El catálogo canónico de aplicaciones y URLs vive en
`../personal-agent-platform/config/domains.yaml`. `personal-agent-platform` coordina el ecosistema;
cada repo de dominio conserva su propia semántica y fuente de verdad.

## DNS

El dominio permanece registrado en Porkbun. Cloudflare pasa a ser el proveedor DNS autoritativo;
esto no transfiere el registro. Antes de reemplazar nameservers se deben conservar los registros
existentes de web, correo, SPF y ACME.

## Límites operativos

- La PC, Docker y la conexión a Internet deben permanecer activos.
- Los archivos grandes se deben cargar desde la red local mientras el límite de carga del proxy
  no esté validado para el plan contratado.
- La pestaña `Contenido` permite alternar entre `LAN rápida` e `Internet`. El cambio queda bloqueado
  durante una carga activa y navega toda la app al origen elegido; los archivos seleccionados pero
  aún no enviados deben elegirse otra vez por una restricción de seguridad del navegador.
- El acceso local permanece en `http://192.168.18.15:8011`; conviene reservar esa dirección por
  DHCP para que no cambie.
- Si una carga se interrumpe, `Contenido > Subidas recientes > Reanudar` conserva la tanda y evita
  volver a transmitir los elementos que el servidor ya guardó.
- Una caída prolongada de energía requiere que el firmware de la PC tenga habilitado el encendido
  automático al recuperar corriente.
- Si la cuenta de Cloudflare usa Google, esa autenticación se completa en el navegador del sistema;
  Google no debe forzarse dentro del WebView. Access seguirá como perímetro hasta implementar el
  futuro login OIDC/OAuth propio de Nodaluna.
