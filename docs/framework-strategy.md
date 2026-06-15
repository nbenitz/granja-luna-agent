# Estrategia de frameworks

Estado: `draft`

## Principio

El proyecto debe resolver primero necesidades reales de Granja Luna.

Los frameworks agenticos pueden ser utiles, pero no deben definir la arquitectura central antes de demostrar valor concreto.

## Decision de trabajo

El core inicial debe ser framework-agnostic.

Esto significa:

- reglas de negocio propias;
- contratos propios;
- validaciones propias;
- modelos de datos propios;
- evaluacion de riesgo propia;
- confirmacion humana propia;
- herramientas internas simples antes de MCP/A2A;
- dependencia minima de librerias externas en el primer MVP.

Un framework como Microsoft Agent Framework, LangGraph, OpenAI Agents SDK u otro puede incorporarse despues como adaptador o runtime si resuelve un problema real mejor que el core propio.

## Criterios para adoptar un framework

Adoptar un framework solo si cumple al menos una de estas condiciones:

- simplifica de forma clara un workflow multiagente real;
- mejora persistencia, checkpoints, reintentos o auditoria;
- facilita human-in-the-loop sin esconder reglas de negocio;
- permite integrar herramientas o MCP con menos complejidad propia;
- mejora observabilidad y trazabilidad en produccion;
- reduce codigo propio sin perder control;
- puede reemplazarse sin reescribir contratos ni modelos de dominio.

## Criterios para no adoptarlo

No adoptar un framework si:

- obliga a modelar la granja segun abstracciones ajenas;
- vuelve opacos los flujos de confirmacion;
- mezcla razonamiento del LLM con reglas de negocio criticas;
- dificulta probar funciones simples;
- aumenta dependencias antes de tener operacion real;
- condiciona el futuro producto a un proveedor o ecosistema especifico.

## Enfoque recomendado para el MVP

1. Crear un core limpio con Python, contratos, Markdown y almacenamiento simple.
2. Implementar el primer flujo vertical: compras + stock + tareas + bitacora.
3. Mantener puntos de extension para agentes, herramientas y runtimes.
4. Evaluar frameworks solo despues de tener un flujo real que duela mantener manualmente.

## Regla practica

```text
Si una funcion simple, un contrato claro y una validacion explicita resuelven el problema,
no usar un framework agentico todavia.
```

## Horizonte

El proyecto puede crecer mucho, incluso hasta producir patrones reutilizables o un framework propio.

Pero ese horizonte debe emerger desde la operacion real:

```text
necesidad real -> flujo usable -> contrato estable -> herramienta -> runtime -> posible framework
```
