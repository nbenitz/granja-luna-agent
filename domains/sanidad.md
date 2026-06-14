# Dominio: Sanidad

Estado: `draft`

## Propósito

Eventos sanitarios, medicamentos, tratamientos, bioseguridad, observaciones de enfermedad y prevención.

## Responsabilidades del subagente

- Interpretar mensajes relacionados con este dominio.
- Identificar datos detectados y faltantes.
- Proponer registros o tareas.
- Consultar memoria relacionada.
- Marcar riesgos y necesidad de confirmación.

## Campos mínimos para borrador

- Estado: `draft` o `pending_review`.
- Fecha informada o fecha pendiente.
- Animal, lote, galpón o área si fue mencionado.
- Cantidad de aves afectadas, si fue mencionada.
- Signos observados, sin convertirlos en diagnóstico.
- Acción ya realizada, si fue informada.
- Producto sanitario mencionado, si aplica.
- Fuente de la información: conversación, foto, observación, veterinario, etiqueta, otro.
- Riesgo estimado.
- Datos faltantes.

## Campos mínimos antes de confirmar

- Fecha real del evento.
- Animal/lote/área afectada.
- Hecho observado separado de inferencias.
- Tratamiento, dosis, responsable y criterio veterinario/humano cuando corresponda.
- Confirmación humana de Néstor para registrar tratamiento, baja, mortalidad o cambio sanitario.

## Registros sugeridos

- Borrador de evento sanitario.
- Preguntas de triage operativo.
- Tarea de observación o seguimiento.
- Ficha de medicamento/producto sanitario si aparece un producto nuevo.

## Acciones permitidas sin confirmación

- Crear borrador.
- Resumir información.
- Preparar preguntas.
- Detectar inconsistencias.
- Organizar datos de etiqueta en una ficha sanitaria.

## Acciones que requieren confirmación

- Registrar evento sanitario como hecho definitivo.
- Confirmar tratamiento, medicación, dosis, baja o mortalidad.
- Cambiar procedimientos sanitarios estables.
- Recomendar diagnóstico o medicación como certeza.
- Cambiar stock real de medicamentos o productos sanitarios.

## Pendiente de validar

- Productos sanitarios confirmados.
- Procedimientos sanitarios estables.
- Criterios de seguimiento por tipo de evento.
- Relación entre tratamiento confirmado y stock.
- Futuras herramientas/API/MCP.
