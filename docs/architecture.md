# Arquitectura conceptual

## Repositorios

```text
personal-agent-orchestrator/
  Coordina dominios, decide a qué subagente llamar y mantiene contratos globales.

granja-luna-agent/
  Este repo. Memoria y reglas del subagente de la granja.

career-agent/
  Subagente profesional/carrera, basado en el actual repo de carrera.
```

## Capas del sistema

### 1. Orquestador Personal

Recibe pedidos generales y decide si corresponden a Granja Luna, Carrera u otro dominio.

### 2. Subagente Granja Luna

Interpreta tareas de la granja, consulta memoria y propone acciones.

### 3. Subagentes internos

No necesariamente serán procesos separados al inicio. Pueden comenzar como archivos de dominio y evolucionar a agentes reales si el contexto o herramientas lo justifican.

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
