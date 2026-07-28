# Movimientos operativos v1

Estado: `confirmed_by_user`

## Propósito

Registrar desde Personal Agent hechos simples de Granja Luna sin trasladar lógica ni datos al
orquestador. El runtime de Granja Luna valida, persiste y calcula las vistas derivadas.

## Flujo

1. `POST /api/operations/movements/{type}/drafts` valida datos explícitos y crea un movimiento
   `awaiting_confirmation`.
2. La respuesta incluye resumen, ID y código de confirmación ligados al borrador exacto.
3. El usuario revisa ese resumen.
4. `POST /api/operations/movements/{id}/confirm` requiere el código y
   `explicit_confirmation: true`.
5. Granja Luna agrega un evento `movement_applied`; no reescribe ni elimina eventos previos.

Un borrador todavía pendiente puede cancelarse mediante
`POST /api/operations/movements/{id}/cancel`, con su código, confirmación explícita y motivo. La
cancelación agrega `movement_cancelled` y no afecta inventario ni elimina la propuesta original.

## Tipos iniciales

- `egg_collection`: fecha, plantel y total de huevos; desglose y destino opcionales.
- `purchase`: fecha, proveedor, ítems, estado de precio y decisión explícita de inventario.
- `expense`: fecha, concepto, categoría, monto y moneda.
- `sale`: fecha, ítems, total, moneda y decisión explícita de inventario.

Las categorías, precios, fechas, planteles, productos, cantidades y unidades nunca se infieren en
esta API. Si falta un obligatorio, devuelve una sola pregunta en `detail.question` y el campo en
`detail.missing_field`.

## Trazabilidad

Cada movimiento conserva cuatro etapas:

- `trace.requested`: payload, fuente, actor, request ID y fecha;
- `trace.interpreted`: normalización determinista exacta;
- `trace.confirmed`: confirmación explícita, actor y fecha;
- `trace.registered`: evento append-only que convirtió el borrador en hecho aplicado.

## Consultas derivadas

- `GET /api/operations/status`
- `GET /api/operations/daily-summary?date=YYYY-MM-DD`
- `GET /api/operations/movements`
- `GET /api/operations/movements/{id}`
- `GET /api/operations/inventory`

Resumen e inventario declaran `scope: confirmed_bridge_movements_only`. No incluyen inventario ni
historia anteriores a este puente y por eso no deben presentarse como balance histórico completo.

## Límites de v1

- No hay endpoints `DELETE`.
- No hay ajustes manuales, tratamientos, bajas, mortalidad, incubación ni planteles operativos.
- Recolección de huevos se registra como producción; no aumenta inventario automáticamente.
- Compra o venta modifica el inventario derivado solo cuando `update_inventory` fue decidido de
  forma explícita.
- El código de confirmación evita aplicar otro borrador por error, pero no reemplaza autenticación.
