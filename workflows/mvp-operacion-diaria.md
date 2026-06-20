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

1. Recibir mensaje natural o transcripción.
2. Ejecutar `dry_run` para clasificar, detectar datos y evaluar riesgo.
3. Guardar una propuesta en inbox en estado `pending_review`.
4. Revisar la propuesta y sus datos faltantes.
5. Registrar o preparar una entrada de bitácora en estado `draft` o `pending_review`.
6. Proponer registros estructurados si corresponde.
7. Crear o proponer tareas operativas cuando haya próximo paso claro.
8. Pedir confirmación explícita si hay impacto en dinero, sanidad, stock, ventas, compras o procedimientos.
9. Registrar decisiones relevantes en `memory/granja/decisiones.md`.

## Salida mínima

- Resumen breve.
- Entrada de inbox pendiente.
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

- `runtime/state/inbox.jsonl`
- `memory/granja/bitacora/_template-entrada.md`
- `tasks/inbox.md`
- `tasks/active.md`
- `domains/compras.md`
- `domains/stock-insumos.md`
- `domains/sanidad.md`
- `domains/tareas-mantenimiento.md`
