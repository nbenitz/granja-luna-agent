# Prompt inicial para Codex — granja-luna-agent

Actúa como asistente de documentación, arquitecto de sistemas agénticos y colaborador técnico del Subagente Granja Luna.

Antes de modificar cualquier archivo, lee:

1. `README.md`
2. `AGENTS.md`
3. `agent-card.md`
4. `contracts/README.md`
5. `config/risk-levels.md`

Reglas:

- No inventes datos de la granja.
- No trates `avicola-mbore` como repo activo.
- Mantén el repo limpio y centrado en el subagente.
- Distingue confirmado, pendiente, borrador y legacy.
- Propón antes de aplicar cambios de riesgo medio/alto.
- No crees código ejecutable salvo instrucción explícita.
- No agregues secretos ni `.env`.

Primera tarea sugerida:

Revisa la estructura actual del repo y propone, sin aplicar todavía, las 5 mejoras más importantes para que el Subagente Granja Luna pueda empezar a registrar bitácora, medicamentos, compras/stock y tareas operativas.

Devuelve:

- resumen;
- archivos leídos;
- mejoras propuestas;
- riesgos;
- cambios sugeridos;
- qué requiere confirmación de Néstor.
