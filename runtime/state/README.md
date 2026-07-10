# Runtime state

Estado: `local_runtime_state`

Este directorio guarda estado local generado por herramientas del runtime.

## Archivos esperados

- `inbox.jsonl`: entradas pendientes creadas por `runtime/src/cli/granja_inbox.py`.
- `usage-events.jsonl`: eventos de uso de la app web local, sin copiar el texto completo de las entradas.
- `review-events.jsonl`: correcciones y decisiones humanas append-only con diffs estructurados.

## Regla

Los archivos JSON/JSONL de este directorio son estado operativo local y estan ignorados por git.

Una entrada del inbox representa una propuesta pendiente. No confirma compras, ventas, tratamientos, stock, tareas ni decisiones como hechos reales.

Estados de revision:

- `pending`: pendiente de revisar;
- `validated`: interpretacion validada;
- `needs_information`: faltan datos de la fuente o del usuario;
- `needs_correction`: correccion identificada y postergada;
- `rejected`: entrada descartada.

El estado operativo es independiente y permanece `draft` durante este MVP.
