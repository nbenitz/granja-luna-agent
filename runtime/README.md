# Runtime

Estado: `draft`

El runtime convierte la memoria y los workflows de Granja Luna en comportamiento operativo progresivo.

No es todavia una app completa. Es la capa que recibe mensajes, clasifica intencion y dominio, evalua riesgo, prepara borradores, solicita confirmacion y devuelve respuestas estructuradas para una UI.

El CLI `granja_dry_run.py` no escribe archivos. El CLI `granja_inbox.py` agrega una primera bandeja operativa local: guarda propuestas con `review_status: pending` en `runtime/state/inbox.jsonl`, sin aplicar cambios reales.

La web local en `runtime/src/web/` permite capturar y revisar esas propuestas desde un celular conectado a la misma red.
Para compras, muestra una ficha `purchase.v2` de lectura con datos generales y productos. Las correcciones se habilitan por seccion y no modifican el estado operativo.

## Objetivo inicial

El MVP 0.1 debe:

- recibir un mensaje natural;
- recibir contexto/memoria auxiliar opcional;
- clasificar intencion, dominio y riesgo;
- detectar datos de compras, stock y tareas;
- preparar borradores sin confirmar hechos reales;
- devolver `side_effects: []`;
- devolver una `ui_response` renderizable por una app;
- guardar propuestas pendientes en un inbox local;
- operar sin framework agentico obligatorio.

## Estructura

```text
runtime/
  contracts/
    granja-dry-run.schema.json
    ui-response.schema.json
  state/
    inbox.jsonl
    usage-events.jsonl
    review-events.jsonl
  examples/
    dry-run-cases.json
    imported-cases-pending-review.json
    case-review-feedback.jsonl
  src/
    core/
      README.md
      classifier.py
      parsing.py
      intent_forms.py
      review_log.py
      risk.py
      builders.py
      dry_run.py
    cli/
      granja_dry_run.py
      granja_inbox.py
    ui/
      README.md
    web/
      app.py
      static/
  tests/
    test_granja_dry_run.py
```

## Comandos

Las integraciones externas pueden cargar credenciales desde un `.env` local en la raíz del repo.
El archivo está ignorado por Git y debe tener permisos `600`. `.env.example` documenta solamente
los nombres esperados; ninguna clave debe aparecer en código, documentación, logs o resultados.

```bash
python3 runtime/src/cli/granja_dry_run.py "Compre 2 bolsas de maiz a 95000 cada una"
python3 runtime/src/cli/granja_dry_run.py "Compre 2 bolsas de maiz a 95000 cada una" --format summary
python3 runtime/src/cli/granja_dry_run.py "Quiero saber si puedo usar su huevo para meter en la incubadora" --context "Conversacion sobre huevos de aves medicadas para incubacion" --format summary
python3 runtime/src/cli/granja_inbox.py capture "Compre 2 bolsas de maiz a 95000 cada una"
python3 runtime/src/cli/granja_inbox.py list
python3 runtime/src/cli/granja_inbox.py show inbox-id
python3 runtime/src/cli/granja_inbox.py review inbox-id --decision needs_correction --notes "Falta proveedor"
python3 runtime/src/cli/granja_inbox.py summary
python3 runtime/src/cli/curate_review_feedback.py review-event-id --primary-reason system_error --label extraction_miss --training-eligibility eligible --note-usage evidence --explanation "El dato estaba en el texto"
uvicorn runtime.src.web.app:app --host 0.0.0.0 --port 8000
python3 runtime/src/cli/review_imported_cases.py --list
python3 runtime/src/cli/review_imported_cases.py --limit 3
python3 runtime/src/cli/review_imported_cases.py --summary
python3 runtime/src/cli/media_library.py scan
python3 runtime/src/cli/media_library.py summary
python3 runtime/src/cli/media_library.py clusters --type temporal_burst --limit 10
python3 -m runtime.src.cli.media_vision_benchmark --prompt-type photo --image ruta/a/copia.jpg --output runtime/state/media-vision-experiment/results/prueba.json
python3 -m runtime.src.cli.media_gemini_benchmark --image ruta/a/copia-sin-exif.jpg --prompt-type photo --output runtime/state/gemini-media-experiment/results/prueba.json
python3 -m runtime.src.cli.media_gemini_benchmark --video ruta/a/video-sin-metadatos.mp4 --output runtime/state/gemini-media-experiment/results/video.json
python3 -m unittest runtime/tests/test_granja_dry_run.py
npm run test:e2e
```

## Biblioteca local de medios

`media_library.py scan` inventaria JPEG y MP4 dentro de `media/inbox` sin modificar originales.
Guarda metadatos, SHA-256 y grupos temporales en `runtime/state/media-library/library.sqlite3`, que esta
ignorado por Git. Un segundo escaneo reutiliza los resultados de archivos cuyo tamaño y fecha de
modificacion no cambiaron. Los archivos ausentes quedan marcados como faltantes; no se borran de la
base.

La agrupacion `temporal_burst` enlaza fotos consecutivas del mismo dia cuando la separacion entre
tomas no supera 15 segundos. Es una preseleccion y no prueba similitud visual. El analisis perceptual,
las miniaturas y la curaduria humana se exponen ahora en la sección `Contenido` de la app.

La API de curaduría incluye:

- `GET /api/media/clusters`: ráfagas y estado de selección;
- `POST /api/media/clusters/{id}/technical-analysis`: miniaturas sin EXIF, brillo, contraste,
  nitidez heurística y hash perceptual;
- `PATCH /api/media/clusters/{id}/curation`: intenciones, objetivos de campaña y hasta dos favoritas;
- `POST /api/media/clusters/{id}/gemini`: comparación externa únicamente con confirmación explícita;
- `GET /api/media/assets/{id}/thumbnail`: derivado privado, nunca el original.
- `GET /api/content/drafts`: enumera únicamente MP4 derivados preparados para revisión local.
- `GET /api/content/drafts/{filename}/media`: reproduce el borrador con soporte de rangos; nunca
  expone originales de `media/inbox`.

La carga supervisada agrega:

- `POST /api/media/upload-batches`: crea una tanda y valida nombres, cantidades, tamaños y espacio;
- `PUT /api/media/upload-batches/{batch}/items/{item}`: sube un archivo crudo con progreso desde la
  UI, valida firma e integridad y lo mueve atómicamente;
- `POST /api/media/upload-batches/{batch}/complete`: inventaría únicamente los nuevos recursos;
- `GET /api/media/upload-batches`: conserva recibos y contexto sin exponer los originales;
- `POST /api/content/requests`: registra el intake trazable del Estudio de contenido.

El corte incremental no reconstruye ráfagas: el algoritmo global actual todavía debe estabilizar
la identidad de grupos para garantizar que una nueva foto no invalide curaduría humana existente.

La pantalla mantiene visible la misión `Lanzamiento de Facebook` y la cobertura mínima definida en
`campaigns/facebook-launch/media-selection.md`. El flujo técnico y sus límites se documentan en
`docs/media-curation-mvp.md`.

`media_vision_benchmark.py` ejecuta pruebas locales y explícitas contra Ollama. Acepta una o varias
imágenes derivadas, exige una salida JSON y registra latencia, métricas de Ollama y pico observado de
VRAM. No debe apuntarse directamente al inventario completo ni tratar su salida como decisión de
publicación. El protocolo validado y sus límites se documentan en
`docs/media-vision-experiment-2026-08-01.md`.

`media_gemini_benchmark.py` carga `GEMINI_API_KEY` desde el entorno o el `.env` local sin imprimirla.
Admite fotos sanitizadas y un video completo por ejecución, solicita JSON Schema, registra tokens y
elimina el video remoto al terminar. No debe recibir originales con EXIF, menores, datos privados o
material que no haya superado el filtro local. La comparación está en
`docs/gemini-media-experiment-2026-08-02.md`.

La prueba Playwright inicia un servidor aislado, recorre el flujo en telefono y escritorio, y verifica captura, deteccion multiple, inbox, validacion y revision de una compra sin tocar el estado local del usuario.

## Ejemplos de evaluacion

`runtime/examples/dry-run-cases.json` contiene casos versionados para probar el router con frases reales o realistas.

`runtime/examples/imported-cases-pending-review.json` contiene casos recibidos desde asistentes externos. No se edita como fuente principal de feedback.

`runtime/src/cli/review_imported_cases.py` permite revisarlos desde terminal y guarda las respuestas en `runtime/examples/case-review-feedback.jsonl`.

## Diagramas

- `runtime/docs/granja-dry-run-flow.md`: diagrama Mermaid del flujo del CLI `dry_run`.
- `runtime/docs/module-emergence.md`: como una entrada real puede revelar un modulo candidato.

## Regla central

El runtime propone. No registra compras, ventas, stock, sanidad ni tareas como hechos reales sin confirmacion explicita.

El `context` de entrada ayuda a clasificar intencion, riesgo y datos faltantes. No confirma hechos operativos por si solo y no se usa para extraer compras, stock o tratamientos como registros reales.

El inbox operativo guarda propuestas pendientes. Es estado local ignorado por git y no equivale a bitacora confirmada, stock confirmado, compra confirmada ni tarea activa.

## API de operaciones confirmadas

La primera integración MCP agrega una API estructurada separada del inbox narrativo. Admite
borradores de recolección de huevos, compras, gastos y ventas. Cada borrador queda en
`awaiting_confirmation`; solo el endpoint de confirmación explícita lo convierte en `applied`.

Los eventos viven en `runtime/state/operation-events.jsonl`, son append-only y pertenecen a Granja
Luna. Inventario y resumen diario se derivan únicamente de esos movimientos confirmados y lo
declaran en el campo `scope`. El contrato completo está en
`runtime/contracts/operational-movements.md`.

Galpones y planteles viven en `runtime/state/structure-events.jsonl`. Un galpón representa una
ubicación física y un plantel representa un grupo de aves con una referencia opcional a su galpón
actual. Las altas requieren borrador y confirmación explícita; traslados, bajas y edición quedan
fuera de v1. El contrato está en `runtime/contracts/farm-structure.md`.

Incubadoras, lotes y eventos de seguimiento viven en
`runtime/state/incubation-events.jsonl`. También son append-only y requieren confirmación
explícita. El detalle de un lote calcula descartes y unidades todavía sin resultado final. El
contrato está en `runtime/contracts/incubation.md`.

El seguimiento posterior a la eclosión vive en `runtime/state/brooding-events.jsonl`. Registra
zonas de cría, lotes de pollitos y eventos de mortalidad, traslado, observación y cierre según
`runtime/contracts/brooding.md`. La interfaz web permite preparar, confirmar y cancelar borradores
sin borrar su historial.

La web local registra eventos de uso en `runtime/state/usage-events.jsonl`. El log conserva tipo, fecha y referencias, pero no duplica el texto completo de las entradas.

Las correcciones y decisiones humanas se guardan en `runtime/state/review-events.jsonl`. Cada correccion conserva un diff y un motivo estructurado para evaluacion futura, sin tratar automaticamente esos registros como un dataset confirmado.

La curaduria agrega eventos `feedback_curated` sobre las revisiones originales. Permite separar errores de extraccion, enriquecimiento externo, ambiguedades, feedback de producto y ejemplos que deben excluirse.
