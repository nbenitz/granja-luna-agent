# Contratos del Subagente Granja Luna

Este directorio define cómo se comunica el Orquestador Personal con `granja-luna-agent`.

## Decisión inicial

Usar contratos JSON versionados. Esto permite trabajar hoy con ChatGPT/Codex de forma manual y mañana migrar a APIs, MCP o A2A sin rehacer la lógica conceptual.

## Archivos

- `orchestrator-to-granja-luna.schema.json`: tarea enviada por el Orquestador.
- `granja-luna-to-orchestrator.schema.json`: respuesta estructurada del subagente.
- `examples/`: ejemplos de mensajes.

Los contratos internos del runtime viven en `runtime/contracts/`.

La presentación portable mantiene `UIResponse 1.0` estable y documenta una extensión compatible
`1.1` para métricas, gráficas, cronologías, avisos y enlaces declarativos. Ninguna variante acepta
HTML o JavaScript arbitrario.

El primer flujo operativo confirmado se documenta en
`runtime/contracts/operational-movements.md`: Granja Luna valida y conserva los eventos; Personal
Agent solo los expone mediante su fachada MCP.

El catálogo confirmado de galpones y planteles se documenta en
`runtime/contracts/farm-structure.md`. Las altas siguen el mismo protocolo de borrador y
confirmación explícita; Personal Agent no copia estos datos maestros.

El seguimiento de incubadoras, lotes y eventos se documenta en
`runtime/contracts/incubation.md`. Granja Luna valida capacidad, dependencias y descartes; el lote
solo se cierra cuando el usuario confirma sus resultados finales.

El seguimiento de pollitos luego de la eclosión se define en `runtime/contracts/brooding.md`.
Vincula nacidos vivos con zonas y lotes de cría sin convertir animales en inventario de insumos.

El almacenamiento entre recolección e incubación se define en
`runtime/contracts/egg-storage.md`. Mantiene lotes físicos, observaciones de clasificación y
disponibilidad sin confundir una etiqueta con una separación real.

## Regla

Toda tarea debe declarar:

- intención;
- objetivo;
- contexto;
- datos detectados;
- datos faltantes;
- nivel de riesgo;
- acción solicitada;
- salida esperada;
- confirmación requerida.
