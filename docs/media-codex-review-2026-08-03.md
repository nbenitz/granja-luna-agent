# Revisión visual de contingencia con Codex

Estado: `suggestion_pending_human_review`

Fecha: 2026-08-03

## Alcance

Codex (`gpt-5.6-sol`) revisó los siete grupos que no pudieron procesarse con Gemini por el límite
gratuito: 15, 18, 19, 61, 64, 65 y 68. Son 19 fotos en total.

La revisión utilizó derivados locales reducidos y sin EXIF. No modificó originales, elecciones
humanas ni estados de curaduría. Los resultados estructurados locales se guardaron en
`runtime/state/media-library/codex-review-2026-08-03.json`, fuera de Git.

## Comparación con la curaduría humana

| Medida | Resultado |
|---|---:|
| Coincidencia exacta de favorita principal | 5/7 |
| Principal humana incluida entre las favoritas de Codex | 6/7 |
| Alguna favorita compartida | 6/7 |
| Sin favorita compartida | 1/7 |

Codex coincidió con la principal humana en los grupos 18, 19, 61, 64 y 65. En el grupo 68 eligió
como secundaria la principal humana. El único grupo sin coincidencia fue el 15: Codex favoreció la
foto 1 por perfil y visibilidad del ojo; Néstor había elegido la foto 3.

## Resultado por grupo

| Grupo | Principal humana | Principal Codex | Secundaria Codex | Lectura principal |
|---:|---:|---:|---:|---|
| 15 | 3 | 1 | — | Retrato de pollito; el fondo rotulado distrae y conviene recortarlo. |
| 18 | 1 | 1 | 3 | La 1 conserva la intención panorámica; la 3 aporta un retrato nítido diferente. |
| 19 | 1 | 1 | — | La 1 separa mejor el rostro de la actividad del fondo. |
| 61 | 2 | 2 | 1 | La 2 funciona como retrato del gallo y la 1 como escena ambiental. |
| 64 | 1 | 1 | — | La 1 distribuye mejor el grupo y evita el ave cortada dominante de la 2. |
| 65 | 2 | 2 | 1 | La 2 cuenta mejor la expansión entre sectores; la 1 documenta un sector con mayor claridad. |
| 68 | 2 | 1 | 2 | La 1 muestra mejor ojo y perfil; la 2 aporta un gesto más tierno y tranquilo. |

## Riesgos y oportunidades detectados

- Los grupos 15 y 68 tienen potencial emocional o comercial, pero raza, edad, sexo, identidad y
  disponibilidad necesitan confirmación humana.
- El grupo 18 combina bien una imagen de conjunto con otra de detalle; puede convertirse en un
  carrusel que vaya del plantel al ejemplar.
- El grupo 19 es uno de los retratos más fuertes por nitidez, pose e historia personal confirmada
  por Néstor.
- El grupo 61 permite separar retrato del reproductor y contexto ambiental sin afirmar que una sola
  foto demuestra el sistema habitual de crianza.
- El grupo 64 sirve mejor como documentación de crecimiento o contenido educativo que como imagen
  principal de lanzamiento.
- El grupo 65 tiene valor histórico para contar la expansión, pero lámparas, cableado, iluminación
  desigual y concentración visual de pollitos exigen contexto antes de publicar. La imagen no
  permite evaluar seguridad, temperatura, densidad ni bienestar.
- En el grupo 68 sólo aparece una mano; no hay una persona identificable. La historia del día uno y
  la identidad del ejemplar provienen del contexto humano, no de la foto.

## Validación

Los siete resultados incluyen exactamente todos los candidatos, como máximo dos favoritas, ranking
completo, afirmaciones pendientes de verificación y elección humana obligatoria. Todos superaron el
validador semántico existente. Las confidencias indicadas son apreciaciones del modelo, no
probabilidades calibradas.

## Estado de cobertura

Los 29 grupos curados y aptos ya tienen una revisión visual asistida: 22 con Gemini y 7 con Codex.
Esta cobertura es mixta y no debe presentarse como un único benchmark homogéneo. Los grupos 60
(`no_usable`) y 63 (`private`) siguen excluidos del procesamiento externo.

## Siguiente paso recomendado

Néstor debería revisar únicamente las dos discrepancias relevantes:

1. Grupo 15: foto 3 humana frente a foto 1 sugerida por Codex.
2. Grupo 68: foto 2 humana frente a foto 1 principal y foto 2 secundaria sugeridas por Codex.

Después se puede continuar con la curaduría del resto de la biblioteca, usando estos 29 grupos como
calibración y manteniendo cada proveedor identificado.
