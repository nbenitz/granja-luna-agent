# Acción autorizada y limitada

Usá exclusivamente el servidor MCP `chrome-devtools` y la sesión de Chrome que ya está abierta y
autenticada. Néstor autorizó compartir en la historia de Facebook de la página **Granja Luna** el
reel programado para hoy, sábado 8 de agosto de 2026 a las 07:15 (America/Asuncion).

El reel correcto es la pieza sobre los pollitos y el frío cuyo texto comienza con **“Hoy amaneció
frío”**. La ejecución ocurre después de su publicación, aproximadamente a las 08:00.

## Procedimiento

1. Comprobá que actuás como la página `Granja Luna` / `@GranjaLunaPy`.
2. Localizá el reel publicado hoy usando el texto y la hora, no sólo su posición en la lista.
3. Antes de actuar, verificá si existe una historia **activa y propiedad de la página Granja Luna**
   que contenga este reel. El texto de un menú como “Volver a compartir en las historias” no es
   evidencia suficiente por sí solo: podría referirse a otra identidad o a un historial anterior.
   Si confirmás la historia activa de la página, no la dupliques y devolvé `already_shared`.
4. Si es el reel correcto y todavía no está compartido, usá la opción de Facebook para compartir
   **ese reel** en la historia de la página. No subas el archivo como una historia independiente.
5. No agregues música, stickers, textos ni modificaciones. Si Facebook exige una decisión no
   contemplada, no publiques y devolvé `failed`.
6. Verificá una confirmación visible o una evidencia equivalente de que la historia se compartió.

## Límites estrictos

- No publiques contenido nuevo en el feed.
- No edites ni elimines publicaciones, historias, configuración, seguidores o mensajes.
- No respondas comentarios ni mensajes.
- No cambies de página o cuenta para publicar.
- No repitas la acción si hay ambigüedad, si no encontrás el reel exacto o si no podés verificar el
  resultado.
- Hacé como máximo un intento de publicación.

Al finalizar devolvé únicamente el objeto JSON solicitado por el esquema. En `evidence` incluí
textos de confirmación o URLs observadas, sin cookies, tokens ni datos personales.
