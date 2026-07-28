# Estructura productiva v1

Estado: `confirmed_by_user`

## Propósito

Registrar galpones, planteles y almacenes de huevos como datos maestros de Granja Luna sin copiar esa verdad al
Orquestador Personal.

## Relación

- `barn`: ubicación física permanente (galpón).
- `flock`: grupo biológico de aves (plantel).
- `egg_storage_area`: zona de almacenamiento previa a incubación, venta o clasificación.
- Un plantel puede referenciar como ubicación actual un galpón previamente confirmado.
- Un galpón puede alojar más de un plantel cuando la operación los mantiene separados.

La relación es opcional en v1 para permitir registrar un plantel antes de conocer o confirmar el
nombre del galpón. Los traslados con historial temporal quedan fuera de este contrato inicial.

## Flujo seguro

1. `POST /api/operations/structure/{record_type}/drafts` crea un borrador.
2. La respuesta devuelve el resumen exacto, ID y código de confirmación.
3. `POST /api/operations/structure/{record_id}/confirm` exige el código y
   `explicit_confirmation: true`.
4. Granja Luna agrega un evento append-only y recién entonces publica el registro en las lecturas.

Un borrador pendiente puede cancelarse con `POST /api/operations/structure/{record_id}/cancel`,
el código exacto, confirmación explícita y un motivo. Los registros aplicados no pueden cancelarse.

## Consultas

- `GET /api/operations/barns`
- `GET /api/operations/flocks`
- `GET /api/operations/egg-storage/areas`
- `GET /api/operations/structure/pending`

## Campos iniciales

Un galpón requiere `name`; `capacity` y `notes` son opcionales.

Un plantel requiere `name` y al menos una entrada en `hen_breeds`. Puede incluir
`bird_count`, `rooster_breeds`, `bird_groups`, `purpose`, `egg_label`, `barn_id` y `notes`. `bird_count` es la
cantidad total opcional de aves y, cuando se informa, debe ser un entero positivo. No se infieren
razas, cantidades, capacidad, ubicación ni propósito.

Un almacén de huevos requiere `name` y `purpose`; capacidad y modo de clasificación son opcionales.

## Límites de v1

- No hay eliminación, edición ni archivo de registros aplicados.
- No hay traslados ni historial de ocupación.
- No se controla automáticamente la capacidad del galpón.
- El registro no reemplaza conteos de aves, nacimientos, bajas, mortalidad ni incubación.
