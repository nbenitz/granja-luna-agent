# Import review: ChatGPT + Gemini cases

Estado: `pending_review`

Fecha: `2026-06-15`

Origen: archivos provistos por Nestor desde ChatGPT y Gemini.

## Resumen

Se importaron casos candidatos a `runtime/examples/imported-cases-pending-review.json`.

| Fuente | Candidatos conversacionales | Variantes sinteticas |
|---|---:|---:|
| ChatGPT | 16 | 3 |
| Gemini | 4 | 1 |
| Total | 20 | 4 |

Estos casos no son registros operativos y no deben tratarse como hechos confirmados.

## Cobertura

Dominios cubiertos:

- sanidad;
- stock-insumos;
- alimentacion;
- incubacion;
- infraestructura;
- tareas-mantenimiento;
- reproductores;
- ventas;
- reportes;
- compras;
- finanzas.

Intenciones cubiertas:

- `registrar_evento_sanitario_borrador`;
- `analizar_decision_operativa`;
- `preguntar_datos_faltantes`;
- `registrar_movimiento_stock_borrador`;
- `analizar_existencias_reposicion`;
- `crear_tarea_borrador`;
- `registrar_bitacora_borrador`;
- `detectar_workflow_candidato`;
- `preparar_reporte`;
- `registrar_venta_borrador`;
- `registrar_compra`.

## Diagnostico contra el dry-run actual

Prueba exploratoria inicial, no bloqueante:

| Total | Intent ok | Dominio ok | Riesgo ok | Todo ok |
|---:|---:|---:|---:|---:|
| 24 | 6 | 9 | 8 | 3 |

Lectura:

- el router actual sirve para el MVP inicial de compras, tareas y stock simple;
- los casos nuevos muestran que sanidad, incubacion, reproductores, FVH y decisiones operativas todavia necesitan vocabulario, reglas de prioridad y posiblemente extraccion asistida por LLM;
- los casos de sanidad elevan la necesidad de manejar `critico`, datos faltantes y confirmacion explicita con mas precision;
- no conviene convertir todo esto en tests hasta curarlo en casos pequenos y ejecutables.

## Primera revision humana

Nestor reviso 5 casos desde el CLI:

| Total revisados | Promover | Necesita edicion | Textos representativos | Salidas esperadas aceptadas |
|---:|---:|---:|---:|---:|
| 5 | 4 | 1 | 5 | 5 |

Ideas detectadas en notas libres:

- el agente deberia proponer borradores de planteles, corrales, galpones, razas y ubicaciones cuando una conversacion revele esas entidades;
- una consulta sanitaria puede generar tareas derivadas de mantenimiento o infraestructura;
- algunos casos necesitan contexto conversacional adicional para interpretarse bien;
- si el usuario dice que ya paso una foto o etiqueta, el agente deberia intentar recuperar evidencia previa antes de pedirla otra vez.

## Diagnostico despues de la primera mejora

La primera mejora promovio 4 casos sanitarios al dataset ejecutable y ajusto el router para sanidad critica.

| Total | Intent ok | Dominio ok | Riesgo ok | Todo ok |
|---:|---:|---:|---:|---:|
| 24 | 10 | 14 | 13 | 7 |

## Segunda revision humana

Nestor reviso 5 casos adicionales desde el CLI:

| Total revisados acumulados | Promover | Necesita edicion | Textos representativos | Salidas esperadas aceptadas |
|---:|---:|---:|---:|---:|
| 10 | 9 | 1 | 10 | 10 |

La segunda mejora promovio 5 casos al dataset ejecutable y agrego soporte inicial para:

- distinguir diseno de modulo/workflow frente a registros operativos;
- detectar ideas de infraestructura como workflow candidato;
- interpretar comparativas de razas como decisiones operativas de reproductores;
- detectar planes reproductivos de alto impacto, como Black Star, con riesgo `alto`;
- pedir datos faltantes de decision: objetivo, lineas, espacio, mercado, presupuesto, incubadora y calendario.

Nota de politica: cuando un caso curado queda con riesgo `medio`, el runtime conserva `requires_confirmation: true` aunque el import original no lo pidiera, porque el contrato actual exige confirmacion para riesgo medio o superior.

## Diagnostico despues de la segunda mejora

| Total | Intent ok | Dominio ok | Riesgo ok | Todo ok |
|---:|---:|---:|---:|---:|
| 24 | 15 | 17 | 19 | 12 |

## Casos recomendados para promover primero

Promover en tandas pequenas:

1. Sanidad de alto riesgo: ivermectina/Oximed/Oxyclina como borrador sanitario, sin recomendaciones de dosis.
2. Incubacion: nota de bitacora sobre incubadora y huevos tratados.
3. FVH/alimentacion: riego o bandejas como workflow candidato.
4. Infraestructura: perchas o cerco como tarea/especificacion.
5. Compras mixtas: separar gastos de granja de gastos personales.

## Reglas de seguridad

- No registrar tratamientos como confirmados desde estos casos.
- No recomendar medicacion, dosis ni orden terapeutico como certeza.
- No convertir stock, compras o ventas en verdad operativa sin confirmacion.
- Mantener los casos sanitarios como material de clasificacion y trazabilidad.

## Siguiente paso propuesto

Curar 3 a 6 casos y agregarlos a `dry-run-cases.json`, ajustando el router solo para comportamientos que el MVP necesita ahora.

## Flujo de revision recomendado

Usar el CLI de revision para evaluar casos por tandas:

```bash
python3 runtime/src/cli/review_imported_cases.py --limit 5
```

El feedback se guarda en `runtime/examples/case-review-feedback.jsonl`.

No editar `imported-cases-pending-review.json` para registrar opiniones caso por caso; ese archivo queda como staging importado.
