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

## Regla

El core puede analizar y proponer, pero no debe escribir archivos ni confirmar hechos operativos en modo `dry_run`.
