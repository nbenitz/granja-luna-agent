# Runtime

Estado: `draft`

El runtime convierte la memoria y los workflows de Granja Luna en comportamiento operativo progresivo.

No es todavia una app completa. Es la capa que recibe mensajes, clasifica intencion y dominio, evalua riesgo, prepara borradores, solicita confirmacion y devuelve respuestas estructuradas para una UI.

## Objetivo inicial

El MVP 0.1 debe:

- recibir un mensaje natural;
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
  src/
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
python3 -m unittest runtime/tests/test_granja_dry_run.py
```

## Diagramas

- `runtime/docs/granja-dry-run-flow.md`: diagrama Mermaid del flujo del CLI `dry_run`.

## Regla central

El runtime propone. No registra compras, ventas, stock, sanidad ni tareas como hechos reales sin confirmacion explicita.
