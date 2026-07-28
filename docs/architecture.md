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
  Este repo. Caso piloto, memoria, reglas, workflows y runtime de Granja Luna.

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
- marca, marketing y comunidad.

### 4. Memoria Markdown

Guarda contexto, procedimientos, bitácoras, fichas, decisiones, ideas y reglas en evolución.

### 5. Datos estructurados

La primera API transaccional usa eventos JSONL append-only para recolección de huevos, compras,
gastos, ventas y el inventario derivado de movimientos confirmados. Este almacenamiento pertenece
a Granja Luna y valida el flujo antes de elegir una BD definitiva. Un segundo registro append-only
conserva galpones y planteles confirmados, con una referencia opcional del plantel a su galpón
actual. Un tercer registro append-only conserva incubadoras, lotes y eventos fechados, con validación de
capacidad, orden de dependencias y descartes acumulados. Un cuarto registro conserva zonas y lotes
de cría posteriores a la eclosión, vincula los pollitos recibidos con el cierre confirmado de
incubación y calcula bajas y traslados. Las cancelaciones de borradores son eventos auditables, no
borrados físicos. Tratamientos, tareas y sensores siguen pendientes.

### 6. Herramientas / MCP

Personal Agent expone la primera fachada MCP para estado, resumen diario, pendientes, inventario,
galpones, planteles, incubación, borradores y confirmación explícita. Granja Luna conserva la lógica
y los datos. Próximas herramientas posibles:

- leer bitácora;
- buscar fichas de medicamentos;
- preparar registro de compra;
- consultar stock;
- listar tareas;
- consultar sensores;
- crear borradores.

### 7. Runtime y UI response

El runtime de Granja Luna vive en `runtime/`.

Su salida debe poder ser usada por:

- la app propia de Granja Luna;
- la app del Asistente Personal;
- un CLI;
- futuras integraciones MCP/A2A.

Para eso, el runtime emite una `ui_response` estructurada. El runtime define la semantica de la interaccion: datos, riesgo, acciones y confirmacion. El host define como se renderiza.

La app de Granja Luna puede ofrecer una UI mas rica de dominio. La app del Asistente Personal puede renderizar componentes genericos o delegar/embeber una vista de Granja Luna cuando corresponda.

La primera distribución Android conserva esa separación: `mobile/` contiene un shell Expo/React
Native que carga la PWA mediante `WebView` y registra `granja-luna://open`. El APK no incorpora la
base operativa ni duplica reglas; el runtime y sus ledgers append-only siguen siendo la fuente de
verdad. Personal Agent puede abrir este cliente por enlace profundo o usar la URL web como fallback.

### 8. Modulos emergentes

Los modulos no deben definirse todos desde el inicio.

Una entrada real puede revelar una intencion nueva, un workflow candidato o un futuro subagente interno.

Ejemplo actual:

- entrada: inventario observado de balanceados y pregunta de reposicion;
- intencion detectada: `analizar_existencias_reposicion`;
- estado: workflow candidato;
- posible evolucion: modulo de existencias, duracion y reposicion.

La explicacion detallada vive en `runtime/docs/module-emergence.md`.

## Regla de diseño

El LLM decide, interpreta y propone. El código valida, persiste y audita.

## Regla de frameworks

El core inicial debe ser framework-agnostic.

Frameworks como Microsoft Agent Framework, LangGraph, OpenAI Agents SDK u otros pueden evaluarse mas adelante, pero no deben definir la arquitectura hasta demostrar valor real frente a necesidades de Granja Luna.

La estrategia detallada vive en `docs/framework-strategy.md`.

## Regla de extraccion

No crear abstracciones genericas hasta que existan flujos reales repetidos.

Una pieza puede moverse a un futuro core generico cuando:

- no dependa de vocabulario exclusivo de Granja Luna;
- tenga contrato estable;
- haya sido usada en mas de un flujo;
- tenga reglas de validacion claras;
- pueda funcionar para otro negocio sin copiar memoria interna de la granja.
