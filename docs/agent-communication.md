# Comunicación entre agentes

## Estado de la decisión

El sistema usará inicialmente comunicación por **contratos Markdown/JSON versionados**, no comunicación autónoma compleja entre agentes.

## Principio

El Orquestador Personal no debe “chatear libremente” con subagentes sin estructura. Debe enviar una tarea con intención, contexto, nivel de riesgo y salida esperada. El subagente debe devolver una respuesta estructurada con interpretación, datos usados, propuesta, riesgos y confirmación requerida.

## Capas recomendadas

### Fase 1 — Contratos locales

- Archivos JSON Schema y ejemplos en `contracts/`.
- Uso manual con Codex/ChatGPT.
- Sin ejecución automática.

### Fase 2 — Herramientas locales

- Scripts o APIs locales para leer/escribir Markdown.
- Validación de JSON.
- Generación de borradores.

### Fase 3 — MCP para herramientas

MCP sirve para conectar el agente con herramientas y recursos: archivos, BD, APIs, buscadores, sensores o flujos.

### Fase 4 — A2A o protocolo similar

A2A puede servir si cada subagente se convierte en aplicación/servicio independiente con identidad, capacidades y tareas delegables.

## Decisión inicial

Para este repo:

- usar contratos versionados;
- mantener `agent-card.md`;
- separar tareas por dominio;
- registrar riesgos y confirmaciones;
- no implementar A2A todavía;
- diseñar pensando en futura compatibilidad con MCP/A2A.
