# Vision del Subagente Granja Luna

Estado: `draft`

Granja Luna no debe gestionarse desde el inicio como un ERP rígido. La intención es que el sistema agéntico aprenda en tiempo real cómo Néstor gestiona la granja.

El agente debe observar, registrar, ordenar, preguntar y proponer. Con el tiempo, cuando ciertos flujos se repitan, se podrán convertir en herramientas programáticas, APIs, esquemas de BD o servidores MCP.

Este repo representa hoy el caso piloto Granja Luna. La vision superior puede evolucionar hacia un ERP agentico configurable para otros negocios, pero esa abstraccion debe salir de flujos reales validados, no de una generalizacion prematura.

## Idea central

La operación real enseña al agente.

No se diseña todo antes de operar. Se empieza registrando actividades y decisiones, y luego se estabilizan los procesos.

## Vision ampliada

Granja Luna puede ser el primer laboratorio real de una plataforma tipo "ERP agentico": un sistema donde el usuario conversa, el agente interpreta, los modulos emergen desde tareas reales y los datos estructurados se crean cuando el flujo lo justifica.

La vision ampliada vive en `docs/agentic-erp-vision.md`.

## Objetivos

- Reducir pérdida de información operativa.
- Ayudar a Néstor a pensar y decidir.
- Registrar sanidad, stock, compras, ventas, incubación e infraestructura.
- Crear memoria reutilizable en Markdown.
- Identificar flujos que justifican automatización.
- Mantener control humano en decisiones críticas.
- Validar patrones que puedan convertirse mas adelante en un core generico de ERP agentico.

## Filosofía

- Primero memoria y trazabilidad.
- Luego contratos entre agentes.
- Luego herramientas.
- Luego BD/API/código.
- Finalmente automatización controlada.

## Regla de producto

Construir primero un producto usable para Granja Luna.

Extraer despues una plataforma generica solo cuando existan patrones repetidos, contratos estables y herramientas probadas con operacion real.
