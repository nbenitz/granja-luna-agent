# MVP 0.1: Operacion diaria

Estado: `draft`

## Objetivo

Crear un primer producto minimo usable para Granja Luna que convierta mensajes naturales en una respuesta estructurada de `dry-run`, sin modificar datos operativos reales.

El MVP debe ayudar a registrar compras, stock, tareas y bitacora diaria desde lenguaje natural, manteniendo confirmacion humana para cualquier accion con impacto operativo.

## Principios

- Resolver necesidades reales de la granja antes de generalizar.
- Mantener el core inicial framework-agnostic.
- Usar contratos y validaciones propias.
- Separar datos detectados, inferencias y datos faltantes.
- No registrar hechos definitivos sin confirmacion explicita.
- Mantener `side_effects: []` en el primer CLI.

## Flujo vertical inicial

Entrada ejemplo:

```text
Compre 2 bolsas de maiz a 95000 cada una
```

Salida esperada:

- intencion detectada: `registrar_compra`;
- dominio primario: `compras`;
- dominios secundarios: `stock-insumos`, `alimentacion`;
- riesgo: `medio`;
- confirmacion requerida: `true`;
- datos detectados: producto, cantidad, unidad, precio unitario y total inferido;
- datos faltantes: fecha real, proveedor, comprobante y confirmacion de impacto en stock;
- borrador de compra;
- movimiento de stock propuesto;
- pregunta clara de confirmacion.

## Alcance funcional

### Incluido

- CLI `dry-run` para texto natural.
- Clasificacion por dominio usando reglas locales.
- Extraccion basica de items de compra.
- Calculo simple de total inferido cuando haya cantidad y precio unitario.
- Propuesta de movimiento de stock para compras de insumos.
- Propuesta de tarea cuando la entrada parezca accion pendiente.
- Salida JSON estable.
- Respuesta de UI estructurada para renderizar revision y confirmacion.
- Pruebas unitarias basicas.

### Excluido

- Modificar archivos de memoria o tareas.
- Confirmar compras, ventas, tratamientos o stock.
- Base de datos.
- LLM obligatorio.
- Microsoft Agent Framework, LangGraph u otro framework agentico.
- MCP/A2A.
- App web o movil.
- Multiempresa.

## Arquitectura inicial

```text
mensaje natural
  -> runtime/src/cli
  -> runtime/src/core framework-agnostic
  -> reglas locales de clasificacion
  -> extraccion heuristica
  -> evaluacion de riesgo
  -> respuesta JSON dry-run + ui_response
```

## Criterios de aceptacion

- El CLI corre sin dependencias externas.
- La entrada de compra de maiz produce un borrador de compra y stock.
- La salida declara `mode: dry_run`.
- La salida declara `side_effects: []`.
- La salida incluye `ui_response` con componentes estructurados.
- Toda compra o movimiento de stock requiere confirmacion.
- Las pruebas unitarias pasan con `python3 -m unittest`.

## Comando objetivo

```bash
python3 runtime/src/cli/granja_dry_run.py "Compre 2 bolsas de maiz a 95000 cada una"
```

## Evolucion posterior

Cuando el flujo sea util, evaluar:

- escritura confirmada en bitacora;
- almacenamiento SQLite;
- API local;
- interfaz web;
- LLM como extractor asistido;
- MCP o A2A;
- framework agentico solo si aparece una necesidad clara.
