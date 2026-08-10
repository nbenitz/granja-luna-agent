# Granja Luna Agent

Sistema agéntico con supervisión humana para registrar y revisar la operación de una granja avícola. Convierte lenguaje natural en borradores estructurados, aplica reglas de riesgo y mantiene trazabilidad antes de modificar información operativa.

El proyecto combina un runtime Python/FastAPI, una interfaz web responsive y una aplicación móvil Expo/React Native. Su diseño prioriza confirmaciones explícitas para acciones relacionadas con dinero, inventario, sanidad o movimientos de animales.

> Estado: MVP local en evolución. No es un sistema productivo ni reemplaza criterio veterinario o administrativo.

Este repo nace como un subagente limpio, no como continuación directa del sistema tradicional `avicola-mbore`. El código legacy puede aportar vocabulario, entidades, flujos y aprendizajes, pero no debe ensuciar la memoria operativa ni forzar una arquitectura clásica de ERP.

## Propósito

Ayudar a gestionar Granja Luna de forma progresiva y agéntica:

- registrar actividades reales de la granja;
- convertir mensajes naturales en registros propuestos;
- mantener memoria viva en Markdown;
- distinguir conocimiento operativo, datos transaccionales y automatizaciones;
- coordinarse con un Orquestador Personal;
- decidir, con trazabilidad, qué debe vivir en Markdown, base de datos, API, MCP o código tradicional.

## Qué funciona actualmente

- Clasificación de mensajes operativos y extracción de datos.
- Bandeja de borradores con revisión y correcciones trazables.
- Movimientos de compras, gastos, ventas y recolección de huevos.
- Estructura de galpones, planteles y áreas de almacenamiento.
- Seguimiento de lotes de huevos, incubación y cría.
- Contratos JSON versionados para UI y coordinación con otros agentes.
- Interfaz web responsive y cliente móvil Android basado en Expo.
- Pruebas unitarias, pruebas de API y flujo E2E con Playwright.

## Arquitectura

```text
Mensaje natural / app móvil
            |
            v
     Runtime FastAPI
            |
   clasificación + validación
            |
            v
  borrador pendiente de revisión
            |
      confirmación humana
            |
            v
      eventos append-only
```

La regla central es simple: **el agente interpreta y propone; el código valida, persiste y audita**. Las decisiones detalladas se encuentran en [`docs/architecture.md`](docs/architecture.md) y los contratos operativos en [`runtime/contracts/`](runtime/contracts/).

## Tecnologías

- Python y FastAPI.
- React Native, Expo y TypeScript.
- JavaScript, HTML y CSS para la UI web local.
- JSON Schema para contratos versionados.
- `unittest`, HTTPX2 y Playwright para validación.
- Docker para ejecución reproducible.

## Qué NO es este repo

- No es el ERP tradicional de la granja.
- No es una copia de `avicola-mbore`.
- No es todavía una aplicación productiva.
- No reemplaza criterio humano ni veterinario.
- No debe confirmar acciones críticas sin aprobación explícita.

## Relación con otros repos

Este repo debería vivir junto a otros repos especializados:

```text
dev/
├── personal-agent-platform/       # Superorquestador y entrada móvil
├── granja-luna-agent/             # Este repo
├── nestor-career-repo/            # Dominio Carrera
└── revelo/                         # Dominio Revelo
```

`avicola-mbore` queda como **legacy descontinuado**. Puede ser usado como fuente inicial de aprendizaje, pero no como dependencia operativa.

## Flujo de trabajo recomendado

1. Registrar ideas, eventos y tareas en `tasks/inbox.md` o `memory/granja/bitacora/`.
2. Clasificar cada entrada por dominio: sanidad, stock, compras, ventas, incubación, infraestructura, etc.
3. Convertir observaciones en propuestas estructuradas.
4. Pedir confirmación humana si hay impacto económico, sanitario, inventario, ventas o automatización física.
5. Registrar decisiones en `memory/granja/decisiones.md`.
6. Cuando un flujo se repita y sea estable, evaluar si debe pasar a BD/API/MCP/código.

## Ejecución local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r runtime/requirements-dev.txt
uvicorn runtime.src.web.app:app --host 127.0.0.1 --port 8000
```

La API queda disponible en `http://127.0.0.1:8000/api/docs` y la interfaz local en `http://127.0.0.1:8000`.

### Validación

```bash
python3 -m unittest discover -s runtime/tests -p "test_*.py"
npm ci --prefix mobile
npm run typecheck --prefix mobile
npm ci
npm run test:e2e
```

## Desarrollo asistido por Codex

Este repositorio se desarrolla con apoyo de OpenAI Codex para inspección, planificación, implementación inicial, refactorización, documentación y pruebas. Las reglas de [`AGENTS.md`](AGENTS.md) limitan la autonomía del agente y exigen revisión humana para decisiones sensibles.

El proceso, las responsabilidades humanas y la evidencia técnica se explican en [`docs/codex-case-study.md`](docs/codex-case-study.md).

## Documentación destacada

- [`agent-card.md`](agent-card.md): rol, capacidades y límites del agente.
- [`config/risk-levels.md`](config/risk-levels.md): clasificación del riesgo.
- [`runtime/README.md`](runtime/README.md): comportamiento y comandos del runtime.
- [`runtime/contracts/`](runtime/contracts/): contratos y esquemas operativos.
- [`docs/codex-case-study.md`](docs/codex-case-study.md): ejemplo de colaboración con Codex.
- [`brand/social-media-operating-model.md`](brand/social-media-operating-model.md): flujo de Marca,
  Comunidad y redes sociales aprendido con publicaciones reales.
- [`docs/session-handoff-2026-08-10.md`](docs/session-handoff-2026-08-10.md): estado y punto exacto
  para continuar el trabajo entre sesiones.

## Estados de información

Usar siempre uno de estos estados:

- `confirmed`: confirmado y estable;
- `confirmed_by_user`: confirmado explícitamente por Néstor;
- `pending_review`: pendiente de validar;
- `draft`: borrador útil pero no definitivo;
- `legacy_reference`: aprendido de un sistema o informe legacy;
- `archived`: conservado por historia, no operativo.
