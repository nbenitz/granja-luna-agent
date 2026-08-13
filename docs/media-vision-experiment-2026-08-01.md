# Experimento local de análisis visual con Qwen3-VL 4B

Estado: `pending_review`

Fecha: 2026-08-01

## Objetivo

Comprobar con medios reales de Granja Luna si `qwen3-vl:4b-instruct` puede ejecutarse en la
máquina disponible y aportar descripción, selección editorial y detección preliminar de riesgos sin
enviar fotos o videos a servicios externos.

El experimento no publica contenido, no modifica originales y no convierte inferencias visuales en
hechos confirmados.

## Entorno probado

- GPU: NVIDIA GeForce GTX 1660 Ti con 6 GB de VRAM;
- RAM: 15 GiB;
- CPU: Intel Core i5-10400F;
- Ollama: 0.31.1;
- modelo: `qwen3-vl:4b-instruct`, 3,3 GB en disco;
- ejecución observada por Ollama: 100% GPU.

## Muestra

- diez fotos de las dos ráfagas temporales más grandes del inventario;
- cinco tomas de pollitos bajo una fuente de calor;
- cinco tomas de un arcoíris sobre los árboles;
- un fotograma central de tres videos de duraciones distintas;
- una prueba adicional individual sobre el fotograma claramente borroso.

Para las evaluaciones individuales se generaron copias de trabajo con lado máximo de 1024 px. Para
las comparaciones se probaron imágenes separadas y láminas de cinco paneles. Todos los derivados y
resultados crudos viven bajo `runtime/state/media-vision-experiment/`, ignorado por Git.

## Resultados de rendimiento

| Prueba | Resultado | Latencia | Entrada | Pico de VRAM total observado |
|---|---|---:|---:|---:|
| Primera foto, 1600 px, carga fría | JSON válido | 54,5 s | 2.348 tokens | 5.442 MiB |
| Misma foto, 1024 px, modelo caliente | JSON válido | 21,0 s | 1.484 tokens | 5.458 MiB |
| Diez fotos individuales, 1024 px | 10/10 JSON válidos | promedio 19,7 s; 18,1–21,7 s | ~1.484 por foto | dentro del límite |
| Cinco imágenes separadas, contexto 8192 | HTTP 500 `unexpected EOF` | falló | 3.552 tokens | presión durante visión |
| Cinco imágenes separadas, contexto 4096 | respuesta truncada | 50,0 s | 3.552 + 544 de salida | 5.417 MiB |
| Cinco imágenes separadas, contexto 5120 | JSON válido | 45,8–55,5 s | ~3.550 | hasta 5.563 MiB |
| Lámina única de cinco paneles, contexto 4096 | 2/2 JSON válidos | 23,4–29,4 s | 1.578 | hasta 5.428 MiB |
| Lámina de tres fotogramas de video | JSON válido | 20,1 s | 1.465 | 5.430 MiB |
| Fotograma borroso individual | JSON válido y descarte correcto | 18,4 s | 1.540 | 5.429 MiB |

La reducción de 1600 a 1024 px mejoró mucho la latencia sin cambiar de forma relevante la respuesta
de control. En esta máquina, cinco imágenes separadas son una configuración frágil. Una lámina
comparativa numerada es más rápida, usa menos contexto y permitió incluir los cinco candidatos.

## Aciertos observados

- describió correctamente pollitos, comederos, fuente de calor, gallo, gallinas, vegetación y
  arcoíris;
- distinguió que el tercer fotograma no contenía aves;
- seleccionó el gallo como el mejor candidato de portada entre los tres fotogramas;
- descartó correctamente por movimiento el fotograma borroso cuando se analizó individualmente;
- no detectó personas, menores ni datos sensibles en la muestra;
- respondió en español y respetó JSON en todas las pruebas individuales y en las láminas finales;
- en la ráfaga de pollitos eligió `20260731_035023.jpg`, una de las tomas visualmente más útiles.

## Errores y límites observados

- llamó “baja resolución” o “baja nitidez” a casi todas las fotos aunque el archivo de entrada era
  suficiente; no debe medir calidad técnica por lenguaje;
- infirió movimiento o bebida de pollitos desde imágenes estáticas;
- confundió en distintas respuestas viruta, paja, forraje, serrín y elementos de calefacción;
- marcó revisión de bienestar en todas las fotos de pollitos sin un indicio concreto;
- propuso frases sobre “salud general” y “condiciones de cuidado” que no pueden afirmarse solo por la
  imagen;
- sugirió un tema de cambio climático sin evidencia ni relación necesaria con la foto;
- el ejemplo inicial del prompt indujo valores como `"feed|educativo"` en un solo campo; se corrigió
  el contrato del experimento para mostrar elementos separados;
- al corregir solamente ese ejemplo, la misma foto `20260801_181032.jpg` cambió de
  `publicable_con_retoque` a `descartar`; la recomendación editorial es sensible al prompt incluso
  con temperatura cero;
- la confianza declarada no está calibrada: devolvió `0.0` en respuestas visualmente correctas;
- comparando cinco imágenes separadas llegó a omitir dos candidatas;
- en la ráfaga de pollitos propuso una panorámica distinta de la finalmente preferida, pero el
  esquema inicial tampoco permitía conservar una segunda favorita con otro ángulo;

## Decisión técnica propuesta

Qwen3-VL 4B es viable como **analista semántico y editorial auxiliar local**, no como juez único ni
como fuente de verdad. La configuración inicial recomendada es:

1. calcular primero metadatos, duplicados, desenfoque, exposición y similitud con herramientas
   deterministas;
2. analizar individualmente copias de trabajo con lado máximo de 1024 px;
3. comparar ráfagas mediante una lámina numerada de hasta cinco paneles y contexto 4096;
4. conservar la respuesta como propuesta explicable, nunca como clasificación definitiva;
5. validar afirmaciones con el registro de marca antes de generar un texto público;
6. solicitar revisión humana para bienestar, privacidad, venta, raza, edad, salud y selección final;
7. ignorar la confianza autoasignada hasta tener un conjunto etiquetado por Néstor;
8. versionar y evaluar cada cambio de prompt contra ese conjunto antes de usarlo en la aplicación;
9. no ejecutar análisis masivo de los 349 recursos hasta integrar métricas técnicas y una pantalla de
   curaduría.

## Calibración humana confirmada

El 2026-08-02 Néstor confirmó las primeras dos etiquetas:

- pollitos: la intención original del grupo era panorámica. `20260731_035020.jpg`, panel 4, es la
  favorita principal porque obedece mejor ese objetivo. `20260731_034957.jpg`, panel 2, queda como
  favorita secundaria: se aparta del objetivo original, pero aporta un acercamiento válido para ver
  caras e interacción alrededor del bebedero. La aparente proximidad de una fuente de calor sigue
  provocando revisión humana;
- arcoíris: `20260801_181032.jpg`, panel 1. Coincide con el modelo, aunque las cinco tomas son casi
  equivalentes y la diferencia tiene poco margen.

Esto demuestra que el ranking necesita primero una intención editorial: `detalle`, `panorámica`,
`portada`, `proceso` o `archivo`. También puede conservar una favorita secundaria cuando aporte un
ángulo realmente diferente, sin confundirla con la ganadora del objetivo principal. Las etiquetas estructuradas viven en
`runtime/examples/media-curation-cases.json`.

El siguiente paso es incorporar pHash y una métrica objetiva de desenfoque/exposición, exponer
miniaturas por API y probar Florence-2 Base como descriptor literal antes de decidir si aporta valor
adicional.
