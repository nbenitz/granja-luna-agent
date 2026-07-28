# Contrato de seguimiento de cría

La fuente de verdad es `runtime/state/brooding-events.jsonl`. El historial es append-only y
contiene tres tipos de registro:

- `area`: zona física de cría, con nombre y capacidad opcional en pollitos.
- `batch`: lote de pollitos alojado en una zona, con fecha, cantidad, edad inicial y origen.
- `event`: mortalidad, traslado de salida, observación o cierre de un lote.

## Reglas determinísticas

- Todo alta o evento nace como borrador y requiere confirmación explícita.
- El orden de confirmación es zona, lote y eventos.
- Un lote vinculado a incubación solo puede usar un lote confirmado y cerrado.
- La suma de lotes de cría vinculados no puede superar los nacidos vivos del lote de incubación.
- La ocupación de lotes abiertos no puede superar la capacidad informada de la zona.
- Mortalidades y traslados no pueden superar el conteo actual.
- El cierre requiere un conteo final igual al conteo actual calculado.

## Cancelación segura

Solo los borradores pendientes pueden cancelarse. La cancelación requiere el código del borrador,
confirmación explícita y un motivo. No elimina datos: agrega un evento y conserva la auditoría.

## API

- `GET /api/operations/brooding/areas`
- `GET /api/operations/brooding/batches`
- `GET /api/operations/brooding/batches/{batch_id}`
- `GET /api/operations/brooding/pending`
- `POST /api/operations/brooding/{area|batch|event}/drafts`
- `POST /api/operations/brooding/{record_id}/confirm`
- `POST /api/operations/brooding/{record_id}/cancel`
