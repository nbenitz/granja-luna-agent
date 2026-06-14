# Dominio: Stock e insumos

Estado: `draft`

## Propósito

Alimentos, vitaminas, cama, materiales, herramientas, desinfectantes y movimientos de inventario.

## Responsabilidades del subagente

- Interpretar mensajes relacionados con este dominio.
- Identificar datos detectados y faltantes.
- Proponer registros o tareas.
- Consultar memoria relacionada.
- Marcar riesgos y necesidad de confirmación.

## Campos mínimos para borrador

- Estado: `draft` o `pending_review`.
- Fecha informada o fecha pendiente.
- Producto/insumo.
- Categoría tentativa: alimento, medicamento, vitamina, cama, material, herramienta, desinfectante, otro.
- Movimiento propuesto: entrada, salida, consumo, ajuste, traslado o inventario observado.
- Cantidad y unidad, si fueron mencionadas.
- Origen/destino, si aplica.
- Motivo: compra, consumo, uso sanitario, mantenimiento, conteo, corrección, otro.
- Fuente de la información: conversación, factura, foto, conteo, nota, otro.
- Datos faltantes.

## Campos mínimos antes de confirmar

- Producto/insumo identificado sin ambigüedad.
- Cantidad y unidad confirmadas.
- Tipo de movimiento confirmado.
- Fecha real del movimiento.
- Origen/destino o área relacionada cuando aplique.
- Confirmación humana de Néstor.

## Registros sugeridos

- Borrador de movimiento de stock.
- Observación de inventario.
- Preguntas de datos faltantes.
- Tarea para conteo físico o revisión de depósito.

## Acciones permitidas sin confirmación

- Crear borrador.
- Resumir información.
- Preparar preguntas.
- Detectar inconsistencias.

## Acciones que requieren confirmación

- Registrar movimiento de stock como hecho definitivo.
- Ajustar inventario real.
- Confirmar consumo, merma, baja o traslado.
- Vincular stock a compras, ventas o tratamientos confirmados.

## Pendiente de validar

- Categorías reales de stock.
- Unidades usadas en la operación.
- Lugares físicos de almacenamiento.
- Criterio para stock mínimo/reposición.
- Futuras herramientas/API/MCP.
