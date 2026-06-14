# Dominio: Compras

Estado: `draft`

## Propósito

Registro y análisis de compras, proveedores, precios, comprobantes y reposición.

## Responsabilidades del subagente

- Interpretar mensajes relacionados con este dominio.
- Identificar datos detectados y faltantes.
- Proponer registros o tareas.
- Consultar memoria relacionada.
- Marcar riesgos y necesidad de confirmación.

## Campos mínimos para borrador

- Estado: `draft` o `pending_review`.
- Fecha informada o fecha pendiente.
- Proveedor, si fue mencionado.
- Comprobante o evidencia, si existe.
- Items: producto/insumo, cantidad, unidad, precio unitario y subtotal cuando estén disponibles.
- Total, moneda y forma de pago cuando estén disponibles.
- Destino o área relacionada, si aplica.
- Indicación de si podría afectar stock.
- Fuente de la información: conversación, factura, foto, nota, otro.
- Datos faltantes.

## Campos mínimos antes de confirmar

- Fecha real de compra.
- Proveedor confirmado.
- Items confirmados con cantidad y unidad.
- Precio total o criterio para registrar precio pendiente.
- Decisión explícita sobre impacto en stock.
- Confirmación humana de Néstor.

## Registros sugeridos

- Borrador de compra.
- Preguntas de datos faltantes.
- Posible movimiento de stock asociado, siempre como propuesta.
- Tarea de seguimiento si falta factura, proveedor, precio o recepción.

## Acciones permitidas sin confirmación

- Crear borrador.
- Resumir información.
- Preparar preguntas.
- Detectar inconsistencias.

## Acciones que requieren confirmación

- Registrar compra como hecho definitivo.
- Cambiar stock real o generar movimiento de stock confirmado.
- Confirmar precio, proveedor o pago si no fueron validados por Néstor.
- Publicar o compartir información de compras/proveedores.

## Pendiente de validar

- Proveedores reales.
- Moneda y formato de precio preferidos.
- Flujo real de recepción de compras.
- Relación exacta entre compra confirmada y movimiento de stock.
- Futuras herramientas/API/MCP.
