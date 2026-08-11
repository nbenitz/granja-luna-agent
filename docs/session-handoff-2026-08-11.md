# Continuidad de trabajo — 11 de agosto de 2026

Estado: `current_handoff`

Este documento cierra la sesión de publicación remota, identidad, aplicaciones móviles y
organización del ecosistema Nodaluna. Para el estado detallado anterior de Marca y Comunidad,
consultar [`session-handoff-2026-08-10.md`](session-handoff-2026-08-10.md).

## Resultado operativo verificado

- Porkbun conserva el registro de `nodaluna.com`; Cloudflare administra el DNS autoritativo.
- El túnel saliente administrado `nodaluna-home` evita depender de IP pública, DDNS y reglas de
  entrada en el router.
- `https://app.nodaluna.com` publica únicamente la UI de Personal Agent.
- `https://granja.nodaluna.com` publica únicamente la UI de Granja Luna.
- Ambos hostnames están protegidos por Cloudflare Access mediante la política privada `Solo Néstor`.
- Docker está habilitado al iniciar la PC; los servicios y `cloudflared` usan
  `restart: unless-stopped`.
- Al cerrar la sesión, Personal Agent y Granja Luna estaban saludables, y el túnel estaba activo.

No se abrieron puertos del router. MCP, Career Agent, PostgreSQL y Chroma permanecen fuera del
túnel. La especificación operativa completa está en [`remote-access.md`](remote-access.md).

## Condiciones para usar la PC como servidor

La disponibilidad depende todavía de que:

- la PC permanezca encendida y con Internet;
- Docker y el conector de Cloudflare puedan arrancar;
- el firmware encienda la PC automáticamente después de recuperar energía;
- exista una estrategia posterior de respaldo y monitoreo.

El arranque automático de Docker está verificado. El encendido automático del firmware, el UPS,
las alertas externas y los respaldos siguen pendientes. La dirección LAN continúa siendo útil para
diagnóstico, pero no forma parte del acceso público.

## Android, PWA y autenticación

Se construyeron e instalaron estos clientes nativos de desarrollo:

| Aplicación | Versión | URL predeterminada | Estado |
|---|---:|---|---|
| Personal Agent | `0.4.1` | `https://app.nodaluna.com` | APK instalado |
| Granja Luna | `0.3.1` | `https://granja.nodaluna.com` | APK instalado |

Los APK están hechos con Expo/React Native y `react-native-webview`. Migran únicamente la antigua
URL LAN predeterminada; respetan una URL personalizada. Los artefactos actuales usan firma de
desarrollo y no son todavía builds de Google Play.

También quedaron instaladas y verificadas como PWA independientes en Android:

- Personal Agent;
- Granja Luna.

Las PWAs abren sin barra de Chrome y conservan la sesión del navegador. Son los clientes remotos
recomendados mientras no exista identidad propia de producto.

El problema observado con Google no era una falla del túnel: Google completa el login en el
navegador del sistema y la cookie de Chrome no se transfiere al WebView. La pantalla inicial de
Cloudflare puede navegar dentro del APK, pero seleccionar Google termina correctamente en Chrome y
deja aislada la sesión nativa. No se debe intentar copiar cookies entre ambos contextos.

La instalación PWA de Granja Luna fallaba además porque el navegador solicitaba el manifiesto sin
credenciales y Cloudflare Access lo redirigía al login. Se corrigió con
`crossorigin="use-credentials"`; Chrome volvió a ofrecer `Instalar Granja Luna` y la instalación se
verificó en modo independiente.

## Dirección de identidad

Cloudflare DNS y Tunnel publican los servicios; Cloudflare Access protege el perímetro privado.
Ninguna de esas capas debe convertirse accidentalmente en el sistema de usuarios del producto.

La dirección acordada es:

- identidad común de Nodaluna mediante OIDC/OAuth;
- Google como posible método de entrada, no como modelo de autorización;
- Authorization Code con PKCE y navegador del sistema en Android;
- identidad global en Personal Agent y permisos propios por dominio;
- mantener Access hasta validar login, autorización, revocación, recuperación y auditoría.

Proveedor, multitenencia, roles iniciales, MFA/passkeys y duración de sesión permanecen en diseño.
La fuente vigente es
[`../../nodaluna/docs/identity-strategy.md`](../../nodaluna/docs/identity-strategy.md).

## Empresa, plataforma y productos

Nodaluna es la empresa de servicios de software y la propietaria del dominio; no es un agente. El
modelo acordado conserva repositorios separados:

| Repositorio | Responsabilidad |
|---|---|
| `nodaluna` | identidad corporativa, sitio público y portafolio |
| `personal-agent-platform` | entrada privada, catálogo y coordinación |
| `granja-luna-agent` | dominio y aplicación Granja Luna |
| `nestor-career-repo` | Career Agent y AI Interview Coach |
| `supermercado-integral` | proyecto separado; no publicable por defecto |

`nodaluna.com` queda reservado para el sitio corporativo. Existe un borrador local con `noindex`,
pero no fue publicado porque texto comercial, contacto, información legal y casos públicos
requieren aprobación humana.

El catálogo ejecutable vive en `personal-agent-platform/config/domains.yaml`. Career Agent es hoy un
servicio interno; AI Interview Coach conserva su identidad de aplicación. Los proyectos de clientes
no entran al superagente ni al portafolio por coexistir bajo `dev/`.

## Estrategia profesional de aplicaciones

- Una PWA puede ser el producto profesional principal cuando cubre bien el flujo y no necesita
  capacidades profundas del dispositivo.
- Expo es tooling de producción alrededor de React Native; permite generar APK para pruebas y AAB
  firmado para Google Play.
- Los shells WebView actuales son una transición útil, no la meta de publicación mientras el login
  no pueda volver de forma segura a la app.
- Cámara, notificaciones, biometría, audio avanzado, segundo plano y offline justifican incorporar
  pantallas o módulos React Native reales de forma progresiva.
- No conviene publicar varias apps casi idénticas. Cada aplicación debe tener audiencia, identidad y
  valor propios.

Para Google Play faltan como mínimo firma de producción, AAB, login OIDC/OAuth con PKCE, política de
privacidad, declaraciones de datos, ficha de tienda, acceso para revisión y pruebas internas.

## Validación realizada

- Suite de Granja Luna: `83` pruebas correctas contra el repositorio montado en sólo lectura;
  las `8` pruebas web también pasaron dentro del contenedor desplegado.
- Suite de Personal Agent: `64` pruebas correctas con los repositorios de dominio montados en sólo
  lectura; se observó un warning de Pydantic sobre una referencia adelantada en settings.
- Typecheck de ambos clientes Expo: correcto.
- Builds Android de ambos clientes: correctos e instalados mediante ADB.
- Acceso externo autenticado a ambas UIs: verificado.
- PWAs de ambas UIs: instaladas y abiertas en modo independiente.
- `git diff --check`: correcto en los tres repositorios al preparar el cierre.

## Secretos y límites

- El token del túnel permanece únicamente en `.env.cloudflare`, ignorado por Git y con permisos
  locales restrictivos.
- No versionar cookies, tokens de Access, URLs firmadas ni datos privados del navegador.
- No retirar Access, publicar servicios internos, abrir puertos del router ni desplegar el sitio
  corporativo sin una decisión explícita.
- No presentar `supermercado-integral` ni otro proyecto de cliente como caso público sin autorización.

## Próximos pasos recomendados

1. Verificar en BIOS/UEFI el encendido automático al recuperar energía y decidir si se necesita UPS.
2. Añadir monitoreo externo y una estrategia de respaldo/restauración probada.
3. Diseñar usuarios, organizaciones, roles y sesiones antes de elegir proveedor de identidad.
4. Elegir qué producto será el primer lanzamiento en Google Play y preparar un build de producción.
5. Aprobar posicionamiento, contacto, privacidad y contenido legal antes de publicar `nodaluna.com`.
6. Validar cargas remotas grandes antes de abandonar la LAN para material pesado.
7. Para Marca y Comunidad, continuar desde el handoff anterior y no publicar sin preflight y
   aprobación humana.
