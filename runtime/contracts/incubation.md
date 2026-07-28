# Incubación v1

Estado: `confirmed_by_user`

## Modelo

- `incubator`: activo físico con nombre y capacidad máxima en huevos.
- `batch`: lote ingresado a una incubadora, con fecha, cantidad y origen.
- `event`: observación fechada del lote: `candling`, `hatching_started`, `discard`, `observation`
  o `closure`.

La incubadora en construcción no se registra como capacidad operativa hasta que el usuario la
declare disponible.

## Flujo

Cada registro se crea como borrador y devuelve ID, resumen y código. La confirmación requiere
`explicit_confirmation: true` y debe respetar el orden incubadora → lote → eventos. Los borradores
pueden referenciar dependencias pendientes para revisar un historial completo antes de aplicarlo.
Un borrador pendiente puede cancelarse con `POST /api/operations/incubation/{record_id}/cancel`,
su código, confirmación explícita y un motivo; la cancelación queda en el historial append-only.

## Validaciones

- La capacidad y los huevos ingresados son enteros positivos.
- La suma de huevos de los lotes abiertos no puede superar la capacidad confirmada de la
  incubadora.
- Si se declaran lotes almacenados de origen, sus cantidades deben sumar el ingreso y no superar
  su disponibilidad confirmada.
- Un evento no puede anteceder al ingreso del lote.
- Los descartes acumulados no pueden superar la cantidad inicial.
- Un lote permanece abierto hasta confirmar un evento `closure` con nacidos vivos, huevos no
  eclosionados, pollitos muertos y pollitos con malformación. Los cuatro resultados, incluyendo
  ceros, deben sumar las unidades que todavía no fueron descartadas.

## Consultas

- `GET /api/operations/incubation/incubators`
- `GET /api/operations/incubation/batches`
- `GET /api/operations/incubation/batches/{batch_id}`
- `GET /api/operations/incubation/pending`

No hay eliminación, edición destructiva ni control físico de incubadoras.
