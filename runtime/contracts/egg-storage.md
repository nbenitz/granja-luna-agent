# Almacenamiento y lotes de huevos v1

Estado: `confirmed_by_user`

## Modelo

- `egg_storage_area`: infraestructura lógica o física donde permanecen huevos recolectados antes
  de su siguiente destino.
- `egg lot`: lote derivado de una recolección confirmada que referencia un almacén confirmado.
- `classification`: observación sobre una parte del lote. Cada eje (por ejemplo `shell_color` o
  `probable_maternal_origin`) se conserva por separado y puede describir los mismos huevos.

Un lote puede permanecer físicamente mezclado (`physical_separation: false`). Una clasificación no
implica separación física ni identidad genética confirmada. `identification_stage: hatch` indica
que la identificación definitiva se hará al nacer.

## Conservación

`disponible = recolectado - asignado`

Una entrada confirmada a incubación puede declarar `source_egg_lots`. Esas cantidades deben sumar
exactamente `eggs_set`, no pueden exceder la disponibilidad y solo se descuentan cuando el lote de
incubación queda confirmado. Los movimientos históricos que no indicaron almacén no generan stock
retroactivo ficticio.

## Clasificación preparada para automatización

Cada observación conserva `axis`, `value`, `quantity`, `certainty`, `information_status`, `method`,
`station_id` y `confidence`. En v1 `method` es `manual`; una futura clasificadora o cinta puede
emitir `automatic` y registrar estación y confianza sin cambiar el modelo de lotes.

La suma de cantidades dentro de un mismo eje no puede superar el total recolectado. Distintos ejes
no se suman entre sí porque son perspectivas sobre el mismo lote.

## Flujo seguro y consultas

El almacén usa el protocolo de borrador y confirmación de estructura. La recolección usa el
protocolo de movimientos operativos. No existe edición destructiva.

- `GET /api/operations/egg-storage/areas`
- `GET /api/operations/egg-storage/lots`
- `GET /api/operations/egg-storage/lots/{lot_id}`
- `POST /api/operations/structure/egg_storage_area/drafts`
- `POST /api/operations/movements/egg_collection/drafts`

