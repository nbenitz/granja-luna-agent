# Aprendizajes destilados del sistema legacy `avicola-mbore`

Estado: `legacy_reference`

Este archivo no es un audit ni una copia del repo legacy. Es una destilación operativa para iniciar el Subagente Granja Luna con aprendizajes útiles sin arrastrar la arquitectura tradicional.

## Qué se rescata

El sistema legacy mostró que los dominios con mayor valor inicial son:

- compras;
- proveedores;
- productos e insumos;
- movimientos de stock;
- ventas;
- dashboard financiero simple;
- lotes;
- postura de huevos;
- consumo de alimento;
- incubación;
- infraestructura/planner;
- sensores/IoT futuro.

## Entidades útiles como referencia

- Producto / insumo
- Proveedor
- Compra
- Línea de compra
- Historial de precio
- Movimiento de stock
- Venta
- Lote
- Recolección de huevos
- Consumo de alimento
- Tanda de incubación
- Lectura de sensor
- Layout / infraestructura

## Reglas útiles detectadas

- Una compra puede empezar como borrador y confirmarse luego.
- Confirmar una compra puede generar movimiento de stock.
- El stock debe calcularse desde movimientos, no editarse sin auditoría.
- Los productos pueden afectar o no afectar stock.
- Proveedores y productos pueden desactivarse en vez de eliminarse.
- Ventas y compras deben tener impacto financiero.

## Qué se evita traer al repo nuevo

- Código frontend/backend legacy.
- Estructura de app tradicional como eje principal.
- Defaults técnicos no validados.
- Supuestos de UI como verdad operativa.
- Dependencia directa del monorepo viejo.

## Uso futuro de este archivo

Este archivo sirve como referencia histórica para:

- diseñar contratos;
- priorizar dominios;
- decidir qué flujos pasar a BD/API;
- evitar repetir errores de sobrediseño;
- mantener claro que `avicola-mbore` es legacy, no fuente activa.
