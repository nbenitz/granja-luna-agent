# Modelos locales para analisis de fotos y videos

Estado: `evaluated_locally`

Fecha de evaluacion: 2026-08-01

## Hardware disponible

- GPU: NVIDIA GeForce GTX 1660 Ti con 6 GB de VRAM;
- RAM: 15 GiB;
- CPU: Intel Core i5-10400F, 6 nucleos y 12 hilos;
- Ollama: 0.31.1;
- modelos ya instalados: `qwen2.5-coder:3b`, `qwen2.5-coder:7b` y `llama3.2:3b`;
- los medios actuales son JPEG y MP4 H.265.

No existe un unico modelo local que resuelva con la misma calidad duplicados, foco, estetica,
descripcion, privacidad, clasificacion editorial y video. La opcion mas eficiente para esta maquina
es una cadena de modelos pequenos y herramientas deterministas.

## Recomendacion principal

### Qwen3-VL 4B Instruct cuantizado

Uso: analista contextual y editorial final sobre fotos o fotogramas seleccionados.

La variante de Ollama ocupa aproximadamente 3,3 GB y acepta texto e imagen. En principio cabe en la
GTX 1660 Ti de 6 GB, dejando un margen limitado para cache y procesamiento visual. Debe usarse con
contexto moderado y una imagen o un grupo pequeno por solicitud.

Es el candidato principal para:

- describir el hecho visible sin afirmar contexto no observado;
- detectar personas, texto, instalaciones, animales y acciones;
- aplicar el prompt y las reglas de marca de Granja Luna;
- proponer uso para feed, historia, reel, educacion o archivo;
- comparar miembros de una rafaga ya reducida;
- devolver JSON explicable con dudas y riesgos.

Aunque la familia Qwen3-VL declara capacidades de comprension de video dinamico, la ficha de Ollama
de la variante local expone entrada `Text, Image`. Para el MVP no se debe depender de video crudo:
se analizaran fotogramas representativos y el audio por separado.

Fuente: [Qwen3-VL en Ollama](https://ollama.com/library/qwen3-vl) y
[tags y tamaños](https://ollama.com/library/qwen3-vl/tags).

### Alternativa: Gemma 3 4B

Tambien ocupa aproximadamente 3,3 GB en Ollama y acepta texto e imagen. Es una alternativa util
para comparar obediencia al esquema, descripcion y velocidad. No hace falta instalar ambos antes de
tener un conjunto de evaluacion: Qwen3-VL 4B debe probarse primero y Gemma 3 4B solo si aparecen
problemas consistentes.

Fuente: [Gemma 3 en Ollama](https://registry.ollama.com/library/gemma3/tags).

## Modelos especializados complementarios

### Florence-2 Base

Uso: descripcion literal, deteccion de objetos, OCR y regiones.

Florence-2 Base tiene 0,23B parametros y licencia MIT. Es mucho mas pequeño que un VLM conversacional
y ofrece tareas concretas como caption detallado, deteccion de objetos, OCR y descripcion por
regiones. Es adecuado para una primera pasada local mas objetiva antes del criterio editorial.

No decide por si solo si una imagen encaja con la voz de Granja Luna y tampoco debe confirmar raza,
salud o edad.

Fuente: [modelo oficial Florence-2 Base](https://huggingface.co/microsoft/Florence-2-base).

### DINOv2 o SigLIP 2

Uso: similitud, busqueda y agrupacion.

DINOv2 produce representaciones visuales robustas sin necesitar etiquetas y es apropiado para
comparar tomas parecidas. SigLIP 2 agrega alineacion entre imagen y texto, por lo que permite
clasificacion zero-shot y consultas como “pollitos pastando” o “infraestructura en construccion”.

Para las rafagas se priorizaria DINOv2 pequeño o un hash perceptual. Para busqueda semantica se
evaluaria SigLIP 2 Base. El modelo publicado `siglip2-base-patch16-224` pesa alrededor de 1,5 GB y
deberia caber en el hardware disponible, aunque su velocidad debe medirse.

Fuentes: [DINOv2 oficial](https://github.com/facebookresearch/dinov2) y
[SigLIP 2 Base](https://huggingface.co/google/siglip2-base-patch16-224).

### IQA-PyTorch

Uso: calidad tecnica y estetica como señales auxiliares.

La biblioteca incluye metricas sin referencia como BRISQUE, NIQE, TOPIQ, MUSIQ y NIMA. Puede ayudar
a medir desenfoque, distorsion o calidad percibida, pero una puntuacion estetica generica no conoce
la historia de Granja Luna. Sus resultados deben ser componentes de la recomendacion, nunca la
decision final.

Fuente: [IQA-PyTorch](https://github.com/chaofengc/IQA-PyTorch).

## Pipeline local para video

Los 88 clips actuales son cortos, pero estan codificados en H.265. El MVP propuesto es:

1. usar FFmpeg para decodificar sin modificar el original;
2. detectar cambios de escena con PySceneDetect;
3. extraer inicio, centro, final y fotogramas de cambios relevantes;
4. puntuar nitidez, exposicion y estabilidad por fotograma;
5. analizar los fotogramas con Florence-2 y Qwen3-VL 4B;
6. transcribir audio localmente con Whisper cuando aporte contexto;
7. producir un resumen temporal con advertencias de privacidad;
8. elegir una portada y sugerir recortes sin renderizar una version publica automaticamente.

PySceneDetect puede detectar cortes por contenido y guardar imagenes representativas de cada escena.
Fuente: [documentacion de PySceneDetect](https://github.com/Breakthrough/PySceneDetect/blob/main/website/pages/cli.md).

Un modelo de video generativo grande no es la primera opcion para esta GPU. La extraccion de escenas
permite reutilizar modelos de imagen mas pequeños, revisar cada evidencia y reducir VRAM y tiempo.

## Composicion recomendada para el MVP

| Etapa | Herramienta/modelo | Funcion | GPU |
|---|---|---|---|
| Inventario | Python, Pillow y FFprobe | metadatos, GPS, dimensiones y duracion | no necesaria |
| Duplicado exacto | SHA-256 | copias binarias | no necesaria |
| Rafaga | fecha/hora | candidatos temporales | no necesaria |
| Casi duplicado | pHash y DINOv2 pequeño | similitud visual | opcional |
| Calidad | OpenCV + IQA pequeño | foco, exposicion, ruido y estetica auxiliar | opcional |
| Descripcion | Florence-2 Base | caption, objetos, OCR y regiones | recomendada |
| Criterio editorial | Qwen3-VL 4B Instruct Q4 | contexto de marca, riesgos y usos | recomendada |
| Video | FFmpeg + PySceneDetect | escenas y fotogramas | no necesaria |
| Audio | Whisper pequeño | transcripcion local | recomendada |

## Modelos especificos de aves

Un detector entrenado exclusivamente para aves o gallinas podria contar o localizar animales, pero
no resolveria seleccion editorial, composicion, privacidad o narrativa. Los modelos publicos de
razas tampoco deben asumirse confiables para las lineas reales de Granja Luna.

Si en el futuro se confirma una necesidad repetida, se puede entrenar un clasificador o detector
propio con fotos etiquetadas por Nestor. Hasta entonces, raza, sexo, edad y condicion sanitaria se
mantienen como contexto humano o inferencia pendiente.

## Prueba recomendada antes de instalar toda la cadena

1. instalar `qwen3-vl:4b-instruct` en Ollama;
2. evaluar las diez fotos ya revisadas y diez miembros de dos rafagas;
3. medir VRAM, latencia, JSON valido y errores factuales;
4. probar Florence-2 Base sobre la misma muestra;
5. elegir DINOv2 o SigLIP 2 solo despues de implementar pHash;
6. incorporar IQA y video cuando la UI ya pueda mostrar comparaciones;
7. no analizar los 349 recursos hasta aprobar el conjunto de calibracion.

La eleccion se hara con evidencia local, no solo por benchmarks generales.

## Resultado de la prueba local

La prueba se completó el 2026-08-01. Qwen3-VL 4B cabe en la GTX 1660 Ti y Ollama lo ejecutó 100% en
GPU. Diez fotos a 1024 px tardaron en promedio 19,7 segundos cada una con el modelo caliente. Las
comparaciones de cinco archivos separados fueron frágiles; una lámina numerada de cinco paneles
redujo la latencia a 23–29 segundos y produjo rankings completos.

El modelo fue útil para descripción y propuesta editorial, pero generó falsos juicios de baja
resolución, alarmas genéricas de bienestar, inferencias de comportamiento y sugerencias públicas no
respaldadas. Por eso se mantiene como analista auxiliar después de filtros deterministas y antes de
la revisión humana. Métricas, ejemplos y configuración están en
`docs/media-vision-experiment-2026-08-01.md`.

## Comparación con Gemini

Gemini 3.5 Flash se evaluó el 2026-08-02 sobre las mismas diez fotos y tres videos completos. Fue más
rápido en fotografías, comparó cinco archivos directamente y superó con claridad a Qwen en video al
usar secuencia y audio. También produjo inferencias discutibles de bienestar y no reprodujo la
preferencia humana de detalle, por lo que conserva revisión y guardián de afirmaciones.

La decisión propuesta es Gemini primero para copias sanitizadas autorizadas para nube y Qwen como
respaldo local para privacidad, falta de conexión o cuota. El informe completo está en
`docs/gemini-media-experiment-2026-08-02.md`.
