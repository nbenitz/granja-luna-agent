# Calibración humano–Gemini para la biblioteca de medios

Estado: `evaluated_pending_prompt_revalidation`

Fecha: 2026-08-03

## Muestra y privacidad

- Biblioteca: 68 ráfagas de fotos.
- Curadas por Néstor: 31.
- Comparaciones válidas con Gemini: 10.
- Grupo 60: `no_usable`, sin favorita, por la posible percepción de encierro o aglomeración.
- Grupo 63: `private`; conserva su valor histórico interno, pero no se envía a Gemini ni se publica
  sin revisar el permiso de imagen de la persona retratada.
- El lote nuevo se revisó localmente antes del envío. No contenía rostros identificables; dos grupos
  mostraban manos. Gemini recibió copias reducidas sin EXIF.

## Resultado cuantitativo

| Medida | Resultado |
|---|---:|
| Coincidencia exacta de favorita principal | 4/10 |
| Principal de Gemini incluida entre las favoritas humanas | 6/10 |
| Alguna favorita compartida, sin importar prioridad | 8/10 |
| Sin coincidencia de favoritas | 2/10 |
| Latencia total | 327,2 s |
| Latencia promedio | 32,7 s |
| Tokens totales informados | 71.467 |

Las coincidencias exactas ocurrieron en los grupos 14, 16, 20 y 62. En los grupos 17 y 33 Gemini
eligió como principal la secundaria humana. En el grupo 59 conservó la principal humana como
secundaria. En el 67 coincidió con la secundaria humana. Los grupos 12 y 13 no tuvieron favorita
compartida.

## Lectura cualitativa

La diferencia más útil apareció cuando una misma ráfaga tenía dos valores editoriales:

- Néstor priorizó paisaje, contexto, significado o fidelidad a la intención original.
- Gemini tendió a priorizar sujeto visible, ausencia de obstrucciones y nitidez aparente.

Esto confirma que la biblioteca necesita principal y secundaria por intención. Una discrepancia no
equivale automáticamente a error; puede revelar dos usos legítimos.

Gemini conservó todos los temas y pilares que Néstor había aportado en los grupos donde existían.
Ese resultado no mide reconocimiento independiente: el modelo recibió el contexto humano, aunque
no recibió las elecciones principal/secundaria.

## Problemas detectados

La salida todavía formuló inferencias demasiado fuertes, entre ellas:

- describir una caja de cartón como transporte seguro;
- relacionar una sola foto con vida libre o crianza responsable;
- sugerir que una imagen permite evaluar pureza racial sin recordar suficientemente la
  incertidumbre;
- convertir elementos visibles de infraestructura en conclusiones sobre manejo o bienestar.

El prompt se ajustó para impedir que una imagen pruebe seguridad, cumplimiento, bienestar, salud,
pureza, resistencia o manejo adecuado. La salida estructurada ahora separa las afirmaciones que
requieren verificación.

## Guardianes implementados

- confirmación separada de envío externo y revisión de privacidad;
- bloqueo de grupos `private` y `no_usable` antes de cualquier llamada externa;
- registro de que sólo se enviaron derivados reducidos y sin EXIF;
- validación de nombres, favoritas, prioridades, ranking completo y revisión humana obligatoria;
- sugerencias inaplicables cuando la validación semántica falla;
- reintentos limitados para errores transitorios `429`, `500`, `502`, `503` y `504`.

## Decisión

Gemini queda habilitado como analista visual y generador de candidatos. No queda habilitado para:

- reemplazar la selección humana;
- descartar originales;
- aprobar material privado;
- confirmar afirmaciones de raza, salud, bienestar, seguridad o disponibilidad;
- publicar.

Antes del análisis masivo de los grupos restantes se realizará una validación pequeña con el prompt
ajustado. El grupo 66 también se reintentará porque sus dos llamadas anteriores recibieron `503 high
demand`; eso no se interpreta como fallo del medio ni del flujo local.

## Avance posterior al endurecimiento

La validación difícil se completó sobre los grupos 12, 16, 59 y 66. Los cuatro resultados finales
superaron los guardianes; el 66 preservó correctamente el paso histórico desde incubadora a
criadero. Luego se analizaron los grupos 1 al 11. En total existen resultados para 22 de los 29
grupos humanos aptos para procesamiento externo.

Quedaron pendientes los grupos 15, 18, 19, 61, 64, 65 y 68 por el límite gratuito comunicado por
Google: 20 solicitudes para `gemini-3.5-flash` en la ventana de cuota. El cliente ahora respeta el
`RetryInfo` del proveedor, con espera máxima de 60 segundos por intento, y el proceso reanudable
omite automáticamente cualquier grupo que ya tenga un resultado guardado.

## Cobertura de contingencia con Codex

Los siete grupos pendientes fueron revisados posteriormente con Codex (`gpt-5.6-sol`) sobre
derivados locales, sin modificar la curaduría humana ni mezclarlos dentro de los resultados de
Gemini. Con ello, los 29 grupos curados y aptos cuentan con revisión visual asistida: 22 de Gemini y
7 de Codex. Esta es una cobertura mixta, no una ampliación del benchmark homogéneo de Gemini.

El resultado detallado y las discrepancias se documentan en
`docs/media-codex-review-2026-08-03.md`.
