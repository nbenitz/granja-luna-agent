# Arquitectura conceptual

Estado: `draft`

## Enfoque actual

Este repo debe avanzar como caso piloto de Granja Luna y, al mismo tiempo, cuidar que las piezas reutilizables puedan extraerse en el futuro hacia un ERP agentico generico.

La prioridad inmediata no es construir una plataforma universal, sino lograr un MVP usable para la granja sin cerrar la puerta a una arquitectura mas amplia.

## Repositorios

```text
personal-agent-orchestrator/
  Coordina dominios, decide a qué subagente llamar y mantiene contratos globales.

granja-luna-agent/
  Este repo. Caso piloto, memoria, reglas, workflows y futuro runtime de Granja Luna.

career-agent/
  Subagente profesional/carrera, basado en el actual repo de carrera.

agentic-erp-core/
  Futuro posible. Core generico extraido solo despues de validar patrones reales en Granja Luna.
```

## Capas del sistema

### 1. Orquestador Personal

Recibe pedidos generales y decide si corresponden a Granja Luna, Carrera u otro dominio.

### 2. Orquestador de Granja Luna

Interpreta tareas de la granja, consulta memoria, evalua riesgo, propone acciones y coordina dominios internos.

### 3. Dominios o subagentes internos

No necesariamente serán procesos separados al inicio. Pueden comenzar como archivos de dominio y evolucionar a agentes reales si el contexto o herramientas lo justifican.

Dominios iniciales candidatos:

- compras;
- stock e insumos;
- alimentacion;
- sanidad;
- ventas;
- incubacion;
- infraestructura;
- mantenimiento;
- tareas;
- reportes;
- finanzas simples;
- clima futuro.

### 4. Memoria Markdown

Guarda contexto, procedimientos, bitácoras, fichas, decisiones, ideas y reglas en evolución.

### 5. Datos estructurados futuros

BD/API para datos transaccionales: compras, ventas, stock, tratamientos, lotes, incubaciones, tareas y sensores.

### 6. Herramientas / MCP futuro

MCP puede exponer herramientas como:

- leer bitácora;
- buscar fichas de medicamentos;
- preparar registro de compra;
- consultar stock;
- listar tareas;
- consultar sensores;
- crear borradores.

## Regla de diseño

El LLM decide, interpreta y propone. El código valida, persiste y audita.

## Regla de extraccion

No crear abstracciones genericas hasta que existan flujos reales repetidos.

Una pieza puede moverse a un futuro core generico cuando:

- no dependa de vocabulario exclusivo de Granja Luna;
- tenga contrato estable;
- haya sido usada en mas de un flujo;
- tenga reglas de validacion claras;
- pueda funcionar para otro negocio sin copiar memoria interna de la granja.
