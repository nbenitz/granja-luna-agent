# Core Runtime

Estado: `draft`

El core contiene la logica reutilizable del runtime de Granja Luna.

El CLI, una futura API, una app web o una integracion con el Asistente Personal deberian llamar a este core en vez de depender de la consola.

## Modulos

| Modulo | Responsabilidad |
|---|---|
| `text.py` | Normalizacion simple de texto. |
| `context.py` | Normalizacion de contexto/memoria auxiliar para analisis. |
| `classifier.py` | Deteccion de dominios e intencion. |
| `risk.py` | Evaluacion de riesgo. |
| `parsing.py` | Extraccion basica de items y numeros. |
| `builders.py` | Construccion de borradores, confirmacion, tareas y UI response. |
| `dry_run.py` | Orquestacion del flujo completo `dry_run`. |
| `inbox.py` | Persistencia JSONL de propuestas pendientes del inbox operativo. |
| `summary.py` | Formato humano resumido para CLI u otras superficies simples. |
| `case_review.py` | Carga, resumen y persistencia JSONL de feedback humano sobre casos importados. |

## Evaluacion

Los casos de ejemplo viven en `runtime/examples/dry-run-cases.json`.

Las pruebas usan ese dataset para verificar intencion, dominio, riesgo, confianza y borradores esperados.

La clasificacion devuelve:

- `matched_signals`: senales encontradas por dominio;
- `domain_scores`: cantidad de senales por dominio;
- `confidence`: confianza inicial del router.

La primera calibracion con feedback humano agrego soporte inicial para:

- vocabulario sanitario frecuente: ivermectina, IVERM, Oxyclina, antibiotico, antiparasitario, sintomas y aves debiles;
- distincion entre tratamiento ya aplicado, consulta de decision sanitaria y pedido de datos faltantes;
- datos faltantes sanitarios por tipo de intencion;
- tarea derivada cuando una consulta sanitaria revela mantenimiento de comederos/platos.

La segunda calibracion agrego soporte inicial para:

- diseno de modulos o workflows candidatos;
- ideas de infraestructura que no deben convertirse automaticamente en tareas;
- comparativas y planes de reproductores como decisiones operativas;
- datos faltantes para decisiones de reproductores e infraestructura.

La tercera calibracion agrego soporte inicial para:

- inventario sanitario comprado como stock pendiente de confirmar;
- tareas FVH/forraje germinado;
- observaciones de postura por color de huevo;
- restricciones de infraestructura por galpones;
- workflows de ficha sanitaria para clientes.

La cuarta calibracion completo la revision inicial de 24 casos y agrego soporte para:

- reportes sanitarios por periodo;
- bitacoras de incubacion;
- tareas de infraestructura;
- decisiones FVH por riego/secado;
- mantenimiento de cama con consumo de insumos;
- compras con precios hablados y casos mixtos con gasto personal.

La quinta mejora agrego soporte inicial para contexto/memoria auxiliar:

- `build_dry_run` acepta `context` opcional;
- el contexto se usa para clasificacion, riesgo y datos faltantes;
- las extracciones de compras, stock e inventario siguen usando solo el texto principal;
- el caso de huevos para incubadora de aves medicadas se promueve como regression test contextual.

La sexta mejora agrega el primer inbox operativo:

- `granja_inbox.py capture` guarda el resultado del dry-run como propuesta `pending_review`;
- `granja_inbox.py list/show/review/summary` permite revisar la bandeja desde terminal;
- el storage local vive en `runtime/state/inbox.jsonl` y esta ignorado por git;
- guardar en inbox no confirma hechos operativos ni aplica cambios reales.

## Regla

El core puede analizar y proponer. En modo `dry_run` no debe escribir archivos ni confirmar hechos operativos. En modo inbox solo puede persistir propuestas pendientes.
