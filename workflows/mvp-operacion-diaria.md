# Workflow: MVP de operación diaria

Estado: `draft`

## Objetivo

Convertir mensajes, notas y observaciones de Granja Luna en bitácora, tareas, fichas y registros sugeridos sin confirmar hechos críticos automáticamente.

## Entrada

- Mensajes naturales de Néstor.
- Notas de voz transcritas.
- Fotos o facturas futuras.
- Observaciones de sanidad.
- Compras, consumos, stock o tareas mencionadas.

## Pasos

1. Registrar o preparar una entrada de bitácora en estado `draft` o `pending_review`.
2. Clasificar dominio primario y dominios secundarios.
3. Separar datos detectados, inferencias y datos faltantes.
4. Asignar nivel de riesgo.
5. Proponer registros estructurados si corresponde.
6. Crear o proponer tareas operativas cuando haya próximo paso claro.
7. Pedir confirmación explícita si hay impacto en dinero, sanidad, stock, ventas, compras o procedimientos.
8. Registrar decisiones relevantes en `memory/granja/decisiones.md`.

## Salida mínima

- Resumen breve.
- Bitácora sugerida o archivo afectado.
- Registros sugeridos.
- Tareas sugeridas.
- Riesgos.
- Preguntas para Néstor.
- Confirmaciones requeridas.

## Reglas de seguridad

- No marcar información como `confirmed` sin confirmación humana.
- No registrar compras, ventas, tratamientos, bajas, mortalidad ni ajustes de stock como hechos reales sin confirmación explícita.
- No recomendar medicación, dosis o diagnóstico como certeza.
- No crear BD/API/código hasta que el flujo se repita y lo justifique.

## Archivos relacionados

- `memory/granja/bitacora/_template-entrada.md`
- `tasks/inbox.md`
- `tasks/active.md`
- `domains/compras.md`
- `domains/stock-insumos.md`
- `domains/sanidad.md`
- `domains/tareas-mantenimiento.md`
