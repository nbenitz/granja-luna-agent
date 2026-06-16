# Core Runtime

Estado: `draft`

El core contiene la logica reutilizable del runtime de Granja Luna.

El CLI, una futura API, una app web o una integracion con el Asistente Personal deberian llamar a este core en vez de depender de la consola.

## Modulos

| Modulo | Responsabilidad |
|---|---|
| `text.py` | Normalizacion simple de texto. |
| `classifier.py` | Deteccion de dominios e intencion. |
| `risk.py` | Evaluacion de riesgo. |
| `parsing.py` | Extraccion basica de items y numeros. |
| `builders.py` | Construccion de borradores, confirmacion, tareas y UI response. |
| `dry_run.py` | Orquestacion del flujo completo `dry_run`. |
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

## Regla

El core puede analizar y proponer, pero no debe escribir archivos ni confirmar hechos operativos en modo `dry_run`.
