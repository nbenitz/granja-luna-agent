# Dominio: Tareas y mantenimiento

Estado: `draft`

## Propósito

Tareas operativas, responsables, vencimientos, rutinas y checklists.

## Responsabilidades del subagente

- Interpretar mensajes relacionados con este dominio.
- Identificar datos detectados y faltantes.
- Proponer registros o tareas.
- Consultar memoria relacionada.
- Marcar riesgos y necesidad de confirmación.

## Campos mínimos para borrador

- Estado: `draft`, `pending_review` o `active`.
- Fecha de creación o fecha informada.
- Título breve de la tarea.
- Dominio primario y dominios secundarios si aplica.
- Área/lugar relacionado, si fue mencionado.
- Responsable, si fue mencionado.
- Prioridad tentativa: baja, media, alta.
- Riesgo: bajo, medio, alto o critico.
- Próximo paso.
- Fuente de la información: conversación, bitácora, revisión diaria, foto, otro.

## Campos mínimos antes de cerrar

- Tarea realizada o decisión de no realizarla.
- Fecha de cierre.
- Responsable o fuente que confirma el cierre.
- Efectos asociados, si los hubo: compra, stock, sanidad, infraestructura, otro.
- Confirmación humana cuando la tarea afecte datos operativos, dinero, sanidad o stock.

## Registros sugeridos

- Entrada en `tasks/inbox.md`.
- Tarea activa en `tasks/active.md`.
- Nota de seguimiento en bitácora.
- Preguntas de datos faltantes.

## Acciones permitidas sin confirmación

- Crear borrador.
- Resumir información.
- Preparar preguntas.
- Detectar inconsistencias.

## Acciones que requieren confirmación

- Asignar responsable o fecha como compromiso definitivo.
- Cerrar tarea como realizada.
- Registrar efectos reales sobre stock, compras, sanidad o infraestructura.
- Borrar, archivar o renombrar archivos importantes relacionados.

## Pendiente de validar

- Responsables reales.
- Criterios de prioridad.
- Rutinas operativas recurrentes.
- Relación entre tareas y bitácora diaria.
- Futuras herramientas/API/MCP.
