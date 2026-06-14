# Workflow: Enrutamiento de tareas

## Reglas de enrutamiento

| Señales en la entrada | Dominio |
|---|---|
| medicamento, enfermedad, síntomas, vacuna, aislamiento | sanidad |
| bolsa, alimento, depósito, stock, insumo, material | stock-insumos |
| compré, factura, proveedor, precio | compras |
| vendí, cliente, cobré, entrega | ventas |
| incubadora, huevos fértiles, nacimiento | incubación |
| galpón, corral, cerco, construcción | infraestructura |
| ración, consumo, balanceado, maíz | alimentación |
| gallo, gallina, raza, cruce, reproductor | reproductores |
| hacer, reparar, limpiar, pendiente | tareas-mantenimiento |
| resumen, informe, cuánto, comparar | reportes |

## Cuando hay múltiples dominios

El Orquestador debe elegir dominio primario y secundarios.

Ejemplo: “compré viruta para cambiar la cama del galpón” involucra compras, stock e infraestructura/mantenimiento.
