# Auditoria inicial de `media/inbox`

Estado: `draft`

Fecha del inventario: 2026-08-01

Esta auditoria es descriptiva. No mueve, renombra, edita ni elimina originales y no convierte una
inferencia visual en un hecho confirmado de la granja.

## Resumen ejecutivo

La carpeta contiene 349 recursos y ocupa 3.829.723.182 bytes: 3,83 GB en unidades decimales o
aproximadamente 3,6 GiB. Hay 261 fotografias JPEG y 88 videos MP4. No se encontraron copias
binarias exactas mediante SHA-256, pero la cercania temporal indica una cantidad importante de
rafagas y variaciones de la misma escena.

| Tipo | Cantidad | Bytes | Peso promedio | Mediana | Rango |
|---|---:|---:|---:|---:|---:|
| Fotografias JPEG | 261 | 1.164.714.235 | 4,26 MiB | 4,26 MiB | 0,25-8,84 MiB |
| Videos MP4 | 88 | 2.665.008.947 | 28,88 MiB | 20,67 MiB | 2,54-126,11 MiB |
| Total | 349 | 3.829.723.182 | 10,47 MiB | 4,68 MiB | 0,25-126,11 MiB |

Los videos representan el 25,2 % de los recursos, pero el 69,6 % de los bytes.

## Cobertura temporal

Los nombres de archivo abarcan desde `20251015_184518` hasta `20260801_210648`. La concentracion
principal esta en junio y julio de 2026.

| Mes | Fotos | Videos | Total |
|---|---:|---:|---:|
| 2025-10 | 10 | 1 | 11 |
| 2025-11 | 5 | 0 | 5 |
| 2025-12 | 1 | 0 | 1 |
| 2026-01 | 36 | 2 | 38 |
| 2026-02 | 44 | 3 | 47 |
| 2026-03 | 7 | 5 | 12 |
| 2026-04 | 1 | 2 | 3 |
| 2026-05 | 10 | 5 | 15 |
| 2026-06 | 65 | 32 | 97 |
| 2026-07 | 70 | 36 | 106 |
| 2026-08 | 12 | 2 | 14 |

Las fechas se infieren de los nombres y deben cotejarse con metadatos antes de tratarlas como fecha
de captura confirmada.

## Fotografias

- 241 fotos son de 4000x3000 pixeles;
- 12 son de 4000x1868;
- 7 son de 3392x2544;
- 1 es de 4000x2252;
- las 261 declaran un Samsung Galaxy S23 Ultra como camara;
- la orientacion EXIF sugiere 149 tomas verticales y 112 horizontales;
- 173 contienen un bloque GPS no vacio segun la lectura estructurada de EXIF con Pillow.

La presencia de GPS es un riesgo operativo concreto. El original debe permanecer privado y todo
derivado para redes debe eliminar ubicacion y metadatos innecesarios antes de salir del sistema.
Esta auditoria no registra ni expone coordenadas.

Una inspeccion preliminar con el comando generico `file` habia marcado 176 recursos porque tambien
conto tres bloques declarados sin entradas GPS. El inventario persistente conserva el criterio
estructurado de Pillow y no extrae las coordenadas.

## Videos

- duracion total: 1.442,63 segundos, aproximadamente 24,04 minutos;
- duracion promedio: 16,39 segundos;
- mediana: 11,83 segundos;
- rango: 1,25-72 segundos;
- 87 videos son 1920x1080 y 1 es 1920x1440;
- los 88 usan H.265 Main Profile y contienen audio;
- 38 duran menos de 10 segundos;
- 40 duran entre 10 y 30 segundos;
- 8 duran entre 30 y 60 segundos;
- 2 duran 60 segundos o mas.

H.265 conserva buena calidad con menor peso, pero obliga a validar compatibilidad en generacion de
miniaturas, edicion y exportacion para cada red. El audio tambien debe revisarse por conversaciones,
nombres o informacion privada antes de recomendar un clip.

## Duplicados y rafagas

- duplicados binarios exactos encontrados con SHA-256: 0;
- grupos preliminares de dos o mas fotos separadas por no mas de 15 segundos: 68;
- fotos incluidas en esos grupos: 205 de 261, el 78,5 %;
- mayor grupo temporal preliminar: 7 fotos.

La cercania temporal no prueba que las imagenes sean visualmente iguales. Sirve para reducir el
espacio de comparacion. La implementacion debe combinar:

1. SHA-256 para copias exactas;
2. fecha y hora para rafagas;
3. hash perceptual para encuadres casi iguales;
4. similitud visual o embeddings para angulos y momentos relacionados;
5. comparacion humana antes de archivar o eliminar.

## Muestra aleatoria de diez fotos

La muestra se eligio al azar y despues se ordeno por fecha para facilitar la lectura.

| Archivo | Lectura preliminar | Uso candidato | Observaciones |
|---|---|---|---|
| `20251015_184617.jpg` | Pollito en manos adultas | comunidad, historia, cercania | Emotiva y enfocada; requiere contexto de edad o linea antes de afirmarlo |
| `20251122_201908.jpg` | Luna creciente sobre fondo oscuro | identidad, pausa editorial | Coherente con el nombre; no documenta la operacion avicola |
| `20260221_110502.jpg` | Grupo de pollitos explorando pasto | educacion, vida natural, comunidad | Escena autentica y atractiva; luz dura y fondo cargado |
| `20260604_145127.jpg` | Huevo sostenido en primer plano dentro del corral | historia de campo, postura | Buen hecho narrativo; foco y composicion secundarios requieren comparar la rafaga |
| `20260610_120809.jpg` | Pollito oscuro en manos | archivo o historia | Desenfoque visible; buscar una toma cercana mejor antes de seleccionarla |
| `20260615_154126.jpg` | Persona adulta con ave sobre el sombrero | personalidad, fundador, comunidad | Muy expresiva; uso identificable requiere aprobacion y contexto |
| `20260616_100726.jpg` | Gallo en vegetacion | retrato de ave, educacion | Sujeto claro; luz intensa y raza no confirmada por la imagen sola |
| `20260703_122902.jpg` | Ave barrada en primer plano con otras aves | retrato, raza, comunidad | Fuerte candidata visual; confirmar raza o linea antes de etiquetar |
| `20260718_180840.jpg` | Vista amplia de terreno con aves y ganado | vision de finca, vida cotidiana | Expresa amplitud y coexistencia; sujetos pequeños para una publicacion de producto |
| `20260731_162946.jpg` | Estructura avicola vacia en construccion o preparacion | progreso, infraestructura | Documental; necesita historia antes/despues para ganar interes publico |

La muestra confirma al menos seis familias de contenido: animales y razas, pollitos, produccion,
personas e historia, paisaje/vida de finca e infraestructura. Tambien demuestra que una foto
tecnicamente imperfecta puede conservar valor documental.

## Escala de recomendacion propuesta

Antes de puntuar se aplican bloqueos revisables por privacidad, menores, contenido sensible,
bienestar animal o falta de permiso. Entre los recursos elegibles se calcula una recomendacion de
0 a 100:

- calidad tecnica: 40 puntos, con foco, exposicion, estabilidad y flexibilidad de recorte;
- fuerza narrativa: 35 puntos, con sujeto claro, accion o emocion y relevancia para Granja Luna;
- aptitud publica: 25 puntos, con contexto verificable, privacidad y percepcion de bienestar.

Interpretacion inicial:

- `A / 85-100`: candidata principal;
- `B / 70-84`: buena con ajuste menor;
- `C / 50-69`: documental, secundaria o necesita contexto/retoque;
- `D / 0-49`: no recomendada para publicar, aunque puede conservar valor privado.

La puntuacion debe mostrar sus razones y comparar cada foto con las de su propio grupo. Nestor elige
la ganadora; el sistema no borra las restantes automaticamente.

## Servicios y modelos candidatos

La gratuidad, cuotas y modelos pueden cambiar. Estas condiciones fueron verificadas el 2026-08-01.

### Gemini API / Google AI Studio

Es la opcion mas completa para un piloto contextual. Puede recibir imagen, video, audio y un prompt
de negocio; describir escenas, responder con marcas de tiempo y producir una salida estructurada con
calidad, riesgos y usos sugeridos. La File API admite hasta 2 GB por archivo en el nivel gratuito y
el dato inline es apropiado para archivos menores de 100 MB. En video, el procesamiento normal
muestra un fotograma por segundo, por lo que movimientos muy rapidos pueden perderse.

Ventajas:

- comprende instrucciones propias de Granja Luna y no solo etiquetas genericas;
- analiza imagen y video con audio;
- puede explicar por que recomienda portada, feed, historia, reel o archivo;
- permite probar sin costo con limites visibles en AI Studio.

Limites y riesgo:

- las cuotas gratuitas varian por modelo y proyecto;
- el contenido del nivel gratuito puede usarse para mejorar productos de Google;
- no se deben enviar originales con GPS, menores ni material privado sin una decision consciente;
- una respuesta generativa puede equivocarse en raza, salud, edad o contexto.

Fuentes: [precios de Gemini](https://ai.google.dev/gemini-api/docs/pricing),
[comprension de video](https://ai.google.dev/gemini-api/docs/video-understanding) y
[comprension de imagen](https://ai.google.dev/gemini-api/docs/image-understanding).

### Gemini Embedding 2

Es un complemento especializado para similitud, clustering y busqueda semantica. Convierte texto,
imagenes, video y audio en vectores comparables. El nivel gratuito incluye entrada multimodal sin
costo, aunque comparte la consideracion de uso de datos del nivel gratuito de Gemini.

Es especialmente compatible con esta biblioteca: acepta JPEG, MP4, H.265 y videos de hasta 120
segundos; todos los videos actuales duran 72 segundos o menos. Procesa hasta 32 fotogramas por
video y no usa la pista de audio del video para el embedding.

Puede ayudar a encontrar:

- fotos visual o semanticamente relacionadas;
- todos los recursos cercanos a una consulta como “pollitos pastando”;
- grupos candidatos a una misma publicacion;
- escenas similares entre fotos y videos.

No reemplaza SHA-256 ni hash perceptual: esos metodos locales son mas baratos y precisos para
duplicados exactos o casi exactos.

Fuentes: [modelo Gemini Embedding 2](https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2)
y [guia de embeddings multimodales](https://ai.google.dev/gemini-api/docs/embeddings).

### Google Cloud Vision API

Es un analizador especializado y mas determinista para fotos. Ofrece etiquetas, contenido
explicito, propiedades de imagen, sugerencias de recorte, texto, logos y localizacion de objetos.
Las primeras 1.000 unidades mensuales de cada funcion figuran sin costo; cada funcion aplicada a
una imagen cuenta como una unidad separada.

Ventajas:

- bueno como filtro tecnico y de seguridad repetible;
- util para etiquetas, colores y recortes;
- suficiente cuota para experimentar con las 261 fotos.

Limites:

- sus etiquetas genericas no saben por si solas que una foto sirve para la historia de Granja Luna;
- activar Google Cloud puede requerir cuenta de facturacion aunque el uso quede en la cuota gratis;
- no debe usarse deteccion facial para identificar personas.

Fuente: [precios oficiales de Cloud Vision](https://cloud.google.com/vision/pricing).

### Google Cloud Video Intelligence API

Es apropiado para segmentar videos y obtener etiquetas por fotograma, toma o segmento, ademas de
contenido explicito, objetos, personas, texto y cambios de toma. Los primeros 1.000 minutos
mensuales de cada funcion aparecen sin costo, pero las fracciones se redondean al minuto completo.

La coleccion suma solo 24,04 minutos reales. Como hay 88 archivos cortos, una funcion aplicada a
todos consumiría al menos 88 minutos facturables por el redondeo, todavia muy por debajo de 1.000.

Ventajas:

- salida temporal estable para clips;
- deteccion de tomas y etiquetas sin depender de un prompt abierto;
- buen prefiltro antes de pedir una evaluacion editorial a un LLM.

Limites:

- no decide bien por si solo si una escena encaja con la voz de marca;
- cada funcion cuenta su propio consumo;
- puede haber costos adicionales de almacenamiento u otros recursos de Google Cloud.

Fuentes: [precios de Video Intelligence](https://cloud.google.com/video-intelligence/pricing) y
[deteccion de etiquetas](https://docs.cloud.google.com/video-intelligence/docs/analyze-labels).

### Ollama con un modelo visual local

Ollama permite enviar imagenes y texto a modelos visuales locales como Gemma 3. No cobra por
solicitud y las fotos no salen de la computadora. La maquina actual tiene una GTX 1660 Ti de 6 GB,
15 GiB de RAM y un i5-10400F; es razonable probar un modelo visual cuantizado pequeno, pero el
rendimiento y la calidad deben medirse antes de adoptar uno para los 349 recursos.

Ventajas:

- privacidad y costo marginal cero;
- integracion local simple;
- util para descripciones preliminares y etiquetas que luego revisa otro modelo o una persona.

Limites:

- la calidad editorial y el reconocimiento fino de aves puede ser inferior a un modelo cloud;
- Ollama recibe imagenes, no analiza de forma nativa el video completo: hay que extraer fotogramas y
  audio primero;
- consume tiempo local y requiere administrar modelos, memoria y colas.

Fuente: [capacidad visual de Ollama](https://docs.ollama.com/capabilities/vision).

### Hugging Face Spaces

Sirve para experimentar manualmente con demos y modelos diferentes. Los usuarios gratuitos tienen
una cuota diaria limitada de ZeroGPU y los Spaces publicos no son una base adecuada para una
biblioteca privada de finca. Es util para comparar modelos con recursos desensibilizados, no como
pipeline principal.

Fuente: [cuotas de ZeroGPU](https://huggingface.co/docs/hub/main/en/spaces-zerogpu).

## Recomendacion de arquitectura

Usar un pipeline hibrido y escalonado:

1. procesar localmente metadatos, GPS, SHA-256, miniaturas, hash perceptual, foco, exposicion y
   grupos temporales;
2. permitir que Nestor corrija contexto por lote antes del analisis semantico;
3. probar Ollama sobre un conjunto pequeno para medir calidad y velocidad;
4. usar Gemini Flash sobre copias reducidas y sin EXIF para la evaluacion editorial detallada;
5. evaluar Gemini Embedding 2 solo si mejora materialmente los grupos obtenidos localmente;
6. reservar Cloud Vision y Video Intelligence para filtros deterministas si Gemini u Ollama no son
   consistentes en seguridad, etiquetas o segmentacion;
7. guardar modelo, version, prompt, fecha y respuesta como sugerencia reproducible, nunca como
   verdad confirmada.

Este orden reduce costo, protege originales y evita enviar a un proveedor 3,8 GB cuando gran parte
del trabajo puede resolverse con metadatos y comparacion local.

## Contexto minimo para el analizador

El modelo debe saber:

- que el material pertenece a una finca avicola real de Paraguay llamada Granja Luna;
- que el objetivo es seleccionar evidencia autentica para Facebook e Instagram;
- que los ejes son clientes, documentacion del proyecto y comunidad educativa;
- que debe distinguir hecho visible, contexto provisto e inferencia;
- que no puede confirmar raza, sexo, edad, salud, bienestar ni disponibilidad solo por apariencia;
- que las fotos reales no pueden alterarse para inventar animales, instalaciones o resultados;
- que toda persona identificable exige revision y todo menor queda bloqueado;
- que debe evaluar calidad, privacidad, bienestar percibido, sensibilidad y posible uso editorial;
- que debe responder en una estructura estable y pedir el contexto faltante.

## Salida estructurada propuesta

```json
{
  "asset_id": "...",
  "factual_description": "...",
  "visible_subjects": [],
  "provided_context": [],
  "uncertain_inferences": [],
  "technical_quality": {
    "focus": 0,
    "exposure": 0,
    "composition": 0,
    "stability_or_motion": 0,
    "audio": "not_applicable"
  },
  "risks": {
    "person": false,
    "possible_minor": false,
    "private_information": false,
    "sensitive_animal_content": false,
    "welfare_context_needed": false,
    "commercial_claim_risk": false
  },
  "content_fit": {
    "facebook_feed": 0,
    "instagram_feed": 0,
    "story": 0,
    "reel": 0,
    "educational": 0,
    "commercial": 0,
    "behind_the_scenes": 0,
    "brand_identity": 0
  },
  "safe_edits": [],
  "questions_for_user": [],
  "recommendation_score": 0,
  "recommendation_tier": "A|B|C|D",
  "recommended_status": "needs_context|selected|private|quality_reject|archive"
}
```

Para videos se agregan resumen, momentos con `MM:SS`, calidad de audio, estabilidad, inicio y final
recortables y mejor fotograma de portada. Para un grupo de rafaga se envia una segunda solicitud que
compara solo sus miembros y explica por que recomienda primero, segundo y tercero.

## Proximo experimento recomendado

Antes del analisis total:

1. construir el inventario persistente sin subir binarios a terceros;
2. formar grupos temporales y perceptuales;
3. elegir unas 30 fotos y 8-10 videos que cubran familias diferentes y niveles de calidad;
4. ejecutar el mismo esquema con un modelo local y Gemini;
5. revisar manualmente coincidencia, errores, latencia y privacidad;
6. congelar el prompt y los umbrales recien despues de esa calibracion.

El analisis de los 349 recursos no debe comenzar hasta que esta muestra etiquetada permita medir si
las recomendaciones realmente coinciden con el criterio de Nestor.
