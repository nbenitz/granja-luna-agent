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

## Datos típicos

- Fecha
- Lugar/galpón/lote si aplica
- Cantidad/unidad si aplica
- Producto/ave/tarea/evento relacionado
- Responsable si aplica
- Observaciones
- Evidencia o fuente

## Acciones permitidas sin confirmación

- Crear borrador.
- Resumir información.
- Preparar preguntas.
- Detectar inconsistencias.

## Acciones que requieren confirmación

- Registrar hecho definitivo.
- Cambiar stock real.
- Confirmar venta o compra.
- Confirmar tratamiento o procedimiento crítico.
- Cerrar evento productivo importante.

## Pendiente de validar

- Campos mínimos definitivos.
- Plantillas específicas.
- Futuras herramientas/API/MCP.
