# Diagrama: `granja_dry_run.py`

Estado: `draft`

Este documento explica el flujo del CLI `dry_run` de Granja Luna.

No es una especificacion completa del runtime. Es una ayuda visual para entender como el script transforma un mensaje natural en una respuesta JSON estructurada, sin usar LLM, sin framework agentico y sin modificar archivos.

Archivos relacionados:

- `runtime/src/cli/granja_dry_run.py`;
- `runtime/src/core/dry_run.py`;
- `runtime/src/core/classifier.py`;
- `runtime/src/core/parsing.py`;
- `runtime/src/core/builders.py`.

## Idea general

El CLI recibe un mensaje, aplica reglas locales, prepara borradores y devuelve una respuesta en modo `dry_run`.

La regla central es:

```text
analizar y proponer, no ejecutar ni registrar hechos reales
```

## Flujo principal

```mermaid
flowchart TD
    A[Usuario ejecuta CLI] --> B[main]
    B --> C[Leer message y today opcional]
    C --> D[core.dry_run build_dry_run]

    D --> E[classify]
    E --> E1[normalize]
    E1 --> E2[score_domains]
    E2 --> E3[detect_intent]
    E3 --> E4[evaluate_risk]
    E4 --> F[classification]

    F --> G{Intent es registrar_compra?}
    G -- Si --> H[parse_items]
    H --> I[purchase_missing_data]
    G -- No --> J[items vacios y missing_data vacio]

    I --> K[build_purchase_draft]
    J --> K
    K --> L[build_stock_movements]
    L --> M[build_log_entry]
    M --> N[build_suggested_tasks]
    N --> O[build_confirmation]
    O --> P[build_ui_response]
    P --> Q[build_next_actions]
    Q --> R[Armar respuesta JSON]
    R --> S[mode dry_run]
    S --> T[side_effects vacio]
    T --> U[Imprimir JSON]
```

## Secuencia de ejecucion

```mermaid
sequenceDiagram
    actor User as Usuario
    participant CLI as CLI main()
    participant Runtime as core.dry_run
    participant Classifier as core.classifier
    participant Parser as core.parsing
    participant Drafts as core.builders
    participant UI as core.builders.build_ui_response

    User->>CLI: python3 runtime/src/cli/granja_dry_run.py "Compre 2 bolsas de maiz..."
    CLI->>Runtime: build_dry_run(message, today)

    Runtime->>Classifier: classify(text)
    Classifier->>Classifier: normalize(text)
    Classifier->>Classifier: score_domains(normalized_text)
    Classifier->>Classifier: detect_intent(normalized_text, domains)
    Classifier->>Classifier: evaluate_risk(intent, domains, normalized_text)
    Classifier-->>Runtime: classification

    alt intent == registrar_compra
        Runtime->>Parser: parse_items(text)
        Parser->>Parser: regex cantidad + unidad + producto + precio
        Parser-->>Runtime: items detectados
        Runtime->>Drafts: purchase_missing_data(items)
        Runtime->>Drafts: build_purchase_draft(items, today)
        Runtime->>Drafts: build_stock_movements(items, primary_domain)
    else otro intent
        Runtime->>Runtime: items = []
        Runtime->>Runtime: missing_data = []
    end

    Runtime->>Drafts: build_log_entry(text, classification, today)
    Runtime->>Drafts: build_suggested_tasks(text, classification)
    Runtime->>Drafts: build_confirmation(classification, items)
    Runtime->>UI: build_ui_response(...)
    UI-->>Runtime: ui_response

    Runtime-->>CLI: respuesta dry_run
    CLI-->>User: JSON en stdout

    Note over Runtime,CLI: No escribe archivos. No confirma compras. No modifica stock.
```

## Mapa de salida

```mermaid
flowchart LR
    A[Respuesta dry_run] --> B[classification]
    A --> C[detected_data]
    A --> D[missing_data]
    A --> E[drafts]
    A --> F[suggested_tasks]
    A --> G[confirmation]
    A --> H[ui_response]
    A --> I[next_actions]
    A --> J[side_effects]

    B --> B1[intent]
    B --> B2[primary_domain]
    B --> B3[secondary_domains]
    B --> B4[risk_level]
    B --> B5[requires_confirmation]
    B --> B6[matched_signals]
    B --> B7[confidence]

    E --> E1[purchase]
    E --> E2[stock_movements]
    E --> E3[log_entry]

    H --> H1[components]
    H --> H2[rendering_mode]
    H --> H3[information_status]

    J --> J1[Siempre vacio en dry_run]
```

## Ejemplo mental

Entrada:

```text
Compre 2 bolsas de maiz a 95000 cada una
```

Lectura del flujo:

1. `classify` detecta senales de `compras`, `stock-insumos` y `alimentacion`.
2. Como aparece una compra, la intencion queda `registrar_compra`.
3. El riesgo queda `medio`, por impacto operativo/economico.
4. `parse_items` detecta:
   - cantidad: `2`;
   - unidad: `bolsa`;
   - producto: `maiz`;
   - precio unitario: `95000`.
5. Se infiere subtotal: `190000`.
6. Se prepara un borrador de compra.
7. Se propone un movimiento de stock de tipo `entrada`.
8. Se crea una `ui_response` con componentes para revisar datos, faltantes y acciones.
9. La salida mantiene `side_effects: []`.

La clasificacion tambien incluye:

- `matched_signals`: senales que explican por que se detectaron dominios;
- `domain_scores`: cantidad de senales por dominio;
- `confidence`: confianza inicial del router, por ahora `low` o `medium`.

## Funciones principales

| Funcion | Rol |
|---|---|
| `main` | Lee argumentos del CLI e imprime JSON. |
| `core.dry_run.build_dry_run` | Coordina todo el flujo. |
| `core.classifier.classify` | Define intencion, dominios, riesgo y confirmacion requerida. |
| `core.classifier.match_domain_signals` | Explica que palabras o frases activaron cada dominio. |
| `core.parsing.parse_items` | Extrae items de compra con reglas simples. |
| `core.builders.build_purchase_draft` | Prepara borrador de compra. |
| `core.builders.build_stock_movements` | Propone movimientos de stock derivados de compras. |
| `core.builders.build_log_entry` | Prepara entrada de bitacora en borrador. |
| `core.builders.build_suggested_tasks` | Propone tareas si detecta senales como revisar o limpiar. |
| `core.builders.build_confirmation` | Formula la pregunta de confirmacion. |
| `core.builders.build_ui_response` | Prepara componentes renderizables por una app host. |

## Limites actuales

- No usa LLM.
- No entiende frases complejas.
- No valida contra productos reales.
- No consulta stock real.
- No escribe en bitacora.
- No registra compras confirmadas.
- No modifica inventario.

Estos limites son intencionales para el MVP 0.1.
