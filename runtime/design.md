# Runtime Design

Estado: `draft`

## Flujo minimo

1. Recibir mensaje natural.
2. Normalizar texto.
3. Clasificar intencion y dominios.
4. Evaluar riesgo.
5. Extraer datos detectados.
6. Separar datos faltantes.
7. Preparar borradores.
8. Preparar `ui_response`.
9. Pedir confirmacion si corresponde.
10. Mantener `side_effects: []` en modo `dry_run`.

## Runtime y UI

Granja Luna puede usarse desde dos superficies:

- app propia de Granja Luna;
- app del Asistente Personal.

El runtime no debe asumir una sola interfaz. Debe devolver una respuesta estructurada que cualquier host autorizado pueda renderizar.

```text
Granja Luna runtime
  -> dry_run / tool result / agent response
  -> ui_response estructurada
  -> host renderer
     -> app Granja Luna
     -> app Asistente Personal
```

## Responsabilidades

| Capa | Responsabilidad |
|---|---|
| Runtime Granja Luna | Decide intencion, riesgo, datos, borradores y confirmacion requerida. |
| `ui_response` | Describe la interaccion necesaria con componentes estructurados. |
| App Granja Luna | Renderiza UI rica y especifica del dominio avicola. |
| App Asistente Personal | Renderiza una UI generica o delega/embebe una vista de Granja Luna. |
| Usuario | Revisa, corrige, confirma o cancela. |

## Regla de UI

El contrato principal no debe ser HTML libre generado por el agente.

La respuesta principal debe ser estructurada:

- tipo de respuesta;
- riesgo;
- estado de informacion;
- componentes;
- acciones posibles;
- datos necesarios para renderizar.

Una vista HTML, iframe o componente remoto puede existir mas adelante como optimizacion o experiencia rica, pero debe tener fallback estructurado.

## Misma tarea, distintas superficies

Si el usuario inicia una tarea de Granja Luna desde el Asistente Personal, deberia ver la misma interaccion semantica:

- mismos campos;
- mismas preguntas;
- mismos riesgos;
- mismas acciones;
- misma confirmacion requerida.

La apariencia visual puede variar segun el host, pero no deben cambiar los datos ni las reglas de confirmacion.

## Escalamiento futuro

Patron recomendado:

1. `ui_response` host-native para componentes basicos.
2. Componentes de dominio reutilizables para Granja Luna.
3. Embedding seguro o iframe para vistas complejas.
4. A2A/MCP cuando existan agentes o herramientas reales.

## Relacion con protocolos existentes

- MCP Elicitation permite que un servidor pida datos estructurados al usuario a traves del cliente.
- MCP Apps / Apps SDK usa `structuredContent` y componentes embebidos para renderizar UI en el host.
- A2A apunta a comunicacion agente-a-agente y negociacion de modalidades como texto, formularios y media.

La estrategia local debe inspirarse en esos patrones, pero mantener contratos propios simples hasta que haya necesidad real de adoptar un protocolo.
