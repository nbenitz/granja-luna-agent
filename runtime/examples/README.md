# Dry-run examples

Estado: `draft`

`dry-run-cases.json` contiene casos versionados para evaluar el router inicial de Granja Luna.

`imported-cases-pending-review.json` contiene casos recibidos desde asistentes externos y queda como bandeja de curaduria. No es una suite de tests ni un registro operativo.

`case-review-feedback.jsonl` es el archivo append-only donde el CLI de revision guarda el feedback humano. Puede no existir hasta la primera revision.

Cada caso define:

- mensaje de entrada;
- contexto/memoria auxiliar opcional;
- intencion esperada;
- dominio primario esperado;
- dominios secundarios esperados;
- riesgo esperado;
- confirmacion esperada;
- confianza esperada;
- borradores esperados.

## Para que sirve

Este archivo funciona como una mini suite de aprendizaje:

- muestra frases que el sistema debe entender;
- evita romper casos ya cubiertos;
- permite ver donde las reglas son fragiles;
- ayuda a decidir cuando hace falta mejorar vocabulario, regex, ejemplos o usar un LLM.

## Regla

Agregar ejemplos reales o realistas antes de tocar mucho el router.

Si una frase falla, primero decidir si:

- falta vocabulario;
- falta una regla de prioridad;
- falta un parser;
- falta contexto/memoria conversacional;
- la frase es ambigua y el sistema debe preguntar.

## Importaciones pendientes

Cuando se importen casos desde ChatGPT, Gemini u otro asistente:

- mantenerlos como `pending_review`, `draft` o `inferred`;
- no marcar compras, ventas, stock, tratamientos o decisiones sanitarias como hechos confirmados;
- revisar duplicados y casos sinteticos antes de promoverlos;
- mover solo casos pequenos y claros a `dry-run-cases.json`;
- usar los casos de mayor riesgo para mejorar clasificacion, datos faltantes y confirmacion, no para ejecutar acciones.

## Revision por CLI

Comandos utiles:

```bash
python3 runtime/src/cli/review_imported_cases.py --list
python3 runtime/src/cli/review_imported_cases.py --case-id gl-001-ivermectina-agua-26-aves
python3 runtime/src/cli/review_imported_cases.py --limit 3
python3 runtime/src/cli/review_imported_cases.py --summary
```

El CLI muestra:

- texto importado;
- salida esperada importada;
- salida actual del runtime;
- preguntas de revision.

Decisiones posibles:

- `promote_to_learning_dataset`: el caso merece pasar a `dry-run-cases.json` despues de curarlo;
- `keep_pending`: el caso sirve, pero todavia no debe promoverse;
- `needs_edit`: el texto o la salida esperada necesitan ajuste;
- `discard`: el caso no conviene usarlo;
- `skip`: no guardar feedback.

El feedback no confirma hechos operativos. Si un caso revela algo que podria registrarse como compra, tratamiento, stock o venta real, se marca como seguimiento aparte.
