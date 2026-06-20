# Runtime state

Estado: `local_runtime_state`

Este directorio guarda estado local generado por herramientas del runtime.

## Archivos esperados

- `inbox.jsonl`: entradas pendientes creadas por `runtime/src/cli/granja_inbox.py`.

## Regla

Los archivos JSON/JSONL de este directorio son estado operativo local y estan ignorados por git.

Una entrada del inbox representa una propuesta `pending_review`. No confirma compras, ventas, tratamientos, stock, tareas ni decisiones como hechos reales.

Estados iniciales:

- `pending_review`: pendiente de revisar.
- `needs_edit`: requiere correccion o datos faltantes.
- `ready_to_apply`: revisado para un paso futuro, todavia no aplicado.
- `cancelled`: descartado por decision humana.
- `archived`: conservado como historial local.
