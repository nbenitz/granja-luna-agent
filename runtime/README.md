# Runtime

Estado: `draft`

El runtime convierte la memoria y los workflows de Granja Luna en comportamiento operativo progresivo.

No es todavia una app completa. Es la capa que recibe mensajes, clasifica intencion y dominio, evalua riesgo, prepara borradores, solicita confirmacion y devuelve respuestas estructuradas para una UI.

## Objetivo inicial

El MVP 0.1 debe:

- recibir un mensaje natural;
- recibir contexto/memoria auxiliar opcional;
- clasificar intencion, dominio y riesgo;
- detectar datos de compras, stock y tareas;
- preparar borradores sin confirmar hechos reales;
- devolver `side_effects: []`;
- devolver una `ui_response` renderizable por una app;
- operar sin framework agentico obligatorio.

## Estructura

```text
runtime/
  contracts/
    granja-dry-run.schema.json
    ui-response.schema.json
  examples/
    dry-run-cases.json
    imported-cases-pending-review.json
    case-review-feedback.jsonl
  src/
    core/
      README.md
      classifier.py
      parsing.py
      risk.py
      builders.py
      dry_run.py
    cli/
      granja_dry_run.py
    ui/
      README.md
  tests/
    test_granja_dry_run.py
```

## Comandos

```bash
python3 runtime/src/cli/granja_dry_run.py "Compre 2 bolsas de maiz a 95000 cada una"
python3 runtime/src/cli/granja_dry_run.py "Compre 2 bolsas de maiz a 95000 cada una" --format summary
python3 runtime/src/cli/granja_dry_run.py "Quiero saber si puedo usar su huevo para meter en la incubadora" --context "Conversacion sobre huevos de aves medicadas para incubacion" --format summary
python3 runtime/src/cli/review_imported_cases.py --list
python3 runtime/src/cli/review_imported_cases.py --limit 3
python3 runtime/src/cli/review_imported_cases.py --summary
python3 -m unittest runtime/tests/test_granja_dry_run.py
```

## Ejemplos de evaluacion

`runtime/examples/dry-run-cases.json` contiene casos versionados para probar el router con frases reales o realistas.

`runtime/examples/imported-cases-pending-review.json` contiene casos recibidos desde asistentes externos. No se edita como fuente principal de feedback.

`runtime/src/cli/review_imported_cases.py` permite revisarlos desde terminal y guarda las respuestas en `runtime/examples/case-review-feedback.jsonl`.

## Diagramas

- `runtime/docs/granja-dry-run-flow.md`: diagrama Mermaid del flujo del CLI `dry_run`.
- `runtime/docs/module-emergence.md`: como una entrada real puede revelar un modulo candidato.

## Regla central

El runtime propone. No registra compras, ventas, stock, sanidad ni tareas como hechos reales sin confirmacion explicita.

El `context` de entrada ayuda a clasificar intencion, riesgo y datos faltantes. No confirma hechos operativos por si solo y no se usa para extraer compras, stock o tratamientos como registros reales.
