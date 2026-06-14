# granja-luna-agent

Repositorio inicial del **Subagente Granja Luna**, parte del futuro ecosistema de agente personal de Néstor Benítez.

Este repo nace como un subagente limpio, no como continuación directa del sistema tradicional `avicola-mbore`. El código legacy puede aportar vocabulario, entidades, flujos y aprendizajes, pero no debe ensuciar la memoria operativa ni forzar una arquitectura clásica de ERP.

## Propósito

Ayudar a gestionar Granja Luna de forma progresiva y agéntica:

- registrar actividades reales de la granja;
- convertir mensajes naturales en registros propuestos;
- mantener memoria viva en Markdown;
- distinguir conocimiento operativo, datos transaccionales y automatizaciones;
- coordinarse con un Orquestador Personal;
- decidir, con trazabilidad, qué debe vivir en Markdown, base de datos, API, MCP o código tradicional.

## Qué es este repo

- Un repositorio de **subagente especializado**.
- Una base de conocimiento operativa y evolutiva.
- Un contrato de comunicación con el Orquestador Personal.
- Un espacio para workflows, prompts, procedimientos, decisiones y memoria.
- Una futura capa de diseño para herramientas, APIs y MCP.

## Qué NO es este repo

- No es el ERP tradicional de la granja.
- No es una copia de `avicola-mbore`.
- No es todavía una aplicación productiva.
- No reemplaza criterio humano ni veterinario.
- No debe confirmar acciones críticas sin aprobación explícita.

## Relación con otros repos

Este repo debería vivir junto a otros repos especializados:

```text
workspace-nestor/
├── personal-agent-orchestrator/   # Orquestador principal
├── granja-luna-agent/             # Este repo
└── career-agent/                  # Subagente Carrera, futuro nombre recomendado
```

`avicola-mbore` queda como **legacy descontinuado**. Puede ser usado como fuente inicial de aprendizaje, pero no como dependencia operativa.

## Flujo de trabajo recomendado

1. Registrar ideas, eventos y tareas en `tasks/inbox.md` o `memory/granja/bitacora/`.
2. Clasificar cada entrada por dominio: sanidad, stock, compras, ventas, incubación, infraestructura, etc.
3. Convertir observaciones en propuestas estructuradas.
4. Pedir confirmación humana si hay impacto económico, sanitario, inventario, ventas o automatización física.
5. Registrar decisiones en `memory/granja/decisiones.md`.
6. Cuando un flujo se repita y sea estable, evaluar si debe pasar a BD/API/MCP/código.

## Primer MVP

El primer MVP no debe ser una app completa. Debe ser una operación simple pero real:

- bitácora diaria en Markdown;
- fichas de medicamentos e insumos;
- registro de tareas;
- contrato Orquestador → Subagente;
- propuesta de registros estructurados para compras, ventas, stock y sanidad;
- niveles de riesgo y confirmación humana.

## Estados de información

Usar siempre uno de estos estados:

- `confirmed`: confirmado y estable;
- `confirmed_by_user`: confirmado explícitamente por Néstor;
- `pending_review`: pendiente de validar;
- `draft`: borrador útil pero no definitivo;
- `legacy_reference`: aprendido de un sistema o informe legacy;
- `archived`: conservado por historia, no operativo.
