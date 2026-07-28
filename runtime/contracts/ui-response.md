# Contract: UI Response

Estado: `stable_v1` + `compatible_v1_1`

Respuesta estructurada compartida que un runtime de dominio entrega a una app host para renderizar
una interacción consistente. Granja Luna implementa la versión `1.0`; Personal Agent conserva el
contrato canónico y actúa como uno de sus hosts.

La versión `1.1` es una ampliación compatible para respuestas más expresivas. Agrega
`metric_grid`, `chart`, `bar_chart`, `timeline`, `link_group` y `notice`; `1.0` continúa estable y
los productores actuales de Granja Luna siguen emitiéndolo.

Schemas JSON:

- `runtime/contracts/ui-response.schema.json`: productor estable `1.0`;
- `runtime/contracts/ui-response.v1.1.schema.json`: extensión compatible y portable `1.1`.

## Principio

El runtime decide que necesita mostrar o pedir. La app decide como renderizarlo.

El contrato no debe contener HTML/CSS libre como forma principal. Debe contener datos, componentes y acciones.

## Ejemplo

```yaml
schema_version: "1.0"
response_type: "review"
title: "Revision de Granja Luna"
summary: "Compra detectada. Falta proveedor y confirmacion de stock."
risk_level: "medium"
requires_confirmation: true
rendering_mode: "host_native"
components:
  - component: "summary_card"
    props:
      title: "Compra detectada"
      body: "2 bolsas de maiz a 95000 cada una."
  - component: "data_table"
    props:
      title: "Items"
      rows:
        - producto: "maiz"
          cantidad: 2
          unidad: "bolsa"
          precio_unitario: 95000
  - component: "action_group"
    props:
      actions:
        - id: "confirm"
          label: "Validar interpretación"
        - id: "edit"
          label: "Corregir en Granja Luna"
        - id: "cancel"
          label: "Descartar propuesta"
information_status:
  detected_data: "inferred"
  missing_data: "pending_review"
  drafts: "draft"
```

## Modos de render

| Modo | Uso |
|---|---|
| `host_native` | El host renderiza componentes genericos desde el contrato. |
| `domain_component` | El host usa un componente especifico de Granja Luna si lo tiene disponible. |
| `external_view` | El host abre o embebe una vista propia de Granja Luna. Debe existir fallback estructurado. |

## Reglas

- Mantener `requires_confirmation: true` para riesgo `medium`, `high` o `critical`.
- No confirmar hechos operativos desde la UI sin accion explicita del usuario.
- La app del Asistente Personal puede renderizar componentes genericos.
- La app de Granja Luna puede renderizar componentes especificos del dominio.
- Si una vista rica falla, el host debe poder mostrar los datos estructurados.
- Los estados compartidos del contrato usan vocabulario estable en ingles; las etiquetas visibles
  pueden localizarse en cada host.
- Ninguna versión permite HTML, CSS o JavaScript arbitrario generado por el agente.
- `link_group` prefiere destinos tipados: `internal_route` para una sección del host,
  `domain_app` para `personal-agent://` o `granja-luna://`, y `external_url` para HTTP(S).
  Los hosts aplican además su propia lista segura y omiten destinos desconocidos.
- La salida de audio no se fija todavía dentro de `UIResponse`. El dictado de entrada utiliza el
  puente versionado `agent.voice.v1`; una futura salida hablada tendrá contrato propio después de
  decidir consentimiento, reproducción automática, voz, velocidad y privacidad.
