# Runtime state

Estado: `local_runtime_state`

Este directorio guarda estado local generado por herramientas del runtime.

## Archivos esperados

- `inbox.jsonl`: entradas pendientes creadas por `runtime/src/cli/granja_inbox.py`.
- `usage-events.jsonl`: eventos de uso de la app web local, sin copiar el texto completo de las entradas.
- `review-events.jsonl`: correcciones y decisiones humanas append-only con diffs estructurados.
- `operation-events.jsonl`: borradores y confirmaciones operativas append-only creados por la API.
- `structure-events.jsonl`: altas append-only de galpones, planteles y almacenes de huevos.
- `incubation-events.jsonl`: incubadoras, lotes y eventos de seguimiento confirmados.
- `brooding-events.jsonl`: zonas, lotes de pollitos y eventos de cría, con borradores y auditoría.

## Regla

Los archivos JSON/JSONL de este directorio son estado operativo local y estan ignorados por git.

Una entrada del inbox representa una propuesta pendiente. No confirma compras, ventas, tratamientos,
stock, tareas ni decisiones como hechos reales. Un evento de `operation-events.jsonl` con estado
`applied` sí representa un hecho operativo confirmado mediante el flujo estructurado; Granja Luna
es su propietario y Personal Agent no copia ese registro.

Estados de revision:

- `pending`: pendiente de revisar;
- `validated`: interpretacion validada;
- `needs_information`: faltan datos de la fuente o del usuario;
- `needs_correction`: correccion identificada y postergada;
- `rejected`: entrada descartada.

El inbox mantiene su estado operativo independiente en `draft`. La API de operaciones usa
`awaiting_confirmation` y `applied`; no expone borrado, cancelación ni edición destructiva.
