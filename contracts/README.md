# Contratos del Subagente Granja Luna

Este directorio define cómo se comunica el Orquestador Personal con `granja-luna-agent`.

## Decisión inicial

Usar contratos JSON versionados. Esto permite trabajar hoy con ChatGPT/Codex de forma manual y mañana migrar a APIs, MCP o A2A sin rehacer la lógica conceptual.

## Archivos

- `orchestrator-to-granja-luna.schema.json`: tarea enviada por el Orquestador.
- `granja-luna-to-orchestrator.schema.json`: respuesta estructurada del subagente.
- `examples/`: ejemplos de mensajes.

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
