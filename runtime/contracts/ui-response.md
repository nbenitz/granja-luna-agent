# Contract: UI Response

Estado: `draft`

Respuesta estructurada que el runtime de Granja Luna entrega a una app host para renderizar una interaccion consistente.

Schema JSON inicial: `runtime/contracts/ui-response.schema.json`.

## Principio

El runtime decide que necesita mostrar o pedir. La app decide como renderizarlo.

El contrato no debe contener HTML/CSS libre como forma principal. Debe contener datos, componentes y acciones.

## Ejemplo

```yaml
schema_version: "0.1"
response_type: "review"
title: "Revision de Granja Luna"
summary: "Compra detectada. Falta proveedor y confirmacion de stock."
risk_level: "medio"
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
          label: "Confirmar borrador"
        - id: "edit"
          label: "Corregir datos"
        - id: "cancel"
          label: "Cancelar"
information_status:
  detected_data: "inferido"
  missing_data: "pendiente_validar"
  drafts: "borrador"
```

## Modos de render

| Modo | Uso |
|---|---|
| `host_native` | El host renderiza componentes genericos desde el contrato. |
| `domain_component` | El host usa un componente especifico de Granja Luna si lo tiene disponible. |
| `external_view` | El host abre o embebe una vista propia de Granja Luna. Debe existir fallback estructurado. |

## Reglas

- Mantener `requires_confirmation: true` para riesgo medio, alto o critico.
- No confirmar hechos operativos desde la UI sin accion explicita del usuario.
- La app del Asistente Personal puede renderizar componentes genericos.
- La app de Granja Luna puede renderizar componentes especificos del dominio.
- Si una vista rica falla, el host debe poder mostrar los datos estructurados.
