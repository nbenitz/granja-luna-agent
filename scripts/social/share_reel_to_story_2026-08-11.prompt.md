# Acción autorizada y limitada

Usá exclusivamente el servidor MCP `chrome-devtools` y la sesión de Chrome abierta y autenticada.
Néstor autorizó compartir en la historia de Facebook de la página **Granja Luna** el reel publicado
hoy, martes 11 de agosto de 2026 a las 06:00 (`America/Asuncion`).

El reel correcto:

- trata sobre las cuatro gallinas Brahma;
- su descripción comienza con **“En Granja Luna viven cuatro gallinas Brahma”**;
- su portada muestra una Brahma clara y el texto **“SE BUSCA NOVIO BRAHMA”**;
- identificador de contenido de Meta: `122107542111420801`;
- URL pública observada: `https://www.facebook.com/reel/1742982856736147/`.

## Procedimiento

1. Comprobá que actuás como la página `Granja Luna` / `@GranjaLunaPy`.
2. Localizá el reel exacto usando al menos dos de los identificadores anteriores; no dependas sólo
   de su posición en una lista.
3. Confirmá que el reel reproduce y mantiene `Audio original`. Si aparece silenciado, retirado o
   con un problema de derechos, no lo compartas y devolvé `skipped`.
4. Revisá las historias activas de la página. Si ese reel ya está compartido, no lo dupliques y
   devolvé `already_shared`.
5. Usá la acción de Facebook para compartir **ese reel** en la historia de la página. No vuelvas a
   subir el MP4.
6. No agregues música, texto, stickers, efectos, menciones ni enlaces.
7. Antes de confirmar, revisá la vista previa. El rótulo `SE BUSCA NOVIO BRAHMA` debe seguir
   legible y no quedar claramente oculto por la interfaz. Si no podés comprobarlo o aparece
   claramente tapado, no publiques y devolvé `failed`.
8. Hacé como máximo un intento y verificá una confirmación visible o la aparición de la historia
   activa de la página.

## Límites estrictos

- No publiques contenido nuevo en el feed.
- No edites ni elimines publicaciones, historias, configuración, seguidores o mensajes.
- No respondas comentarios ni mensajes.
- No cambies de página o cuenta para publicar.
- No repitas la acción ante ambigüedad o falta de verificación.

Al finalizar devolvé únicamente el objeto JSON solicitado por el esquema. En `evidence` incluí
textos de confirmación o URLs observadas, sin cookies, tokens ni datos personales.
