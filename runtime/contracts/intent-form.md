# Intent forms

Estado: `draft`

Las fichas de intencion presentan datos detectados por el runtime en modo lectura. El formulario aparece solo al corregir o enriquecer una seccion.

## Principio

El lenguaje natural inicia el flujo. El formulario no reemplaza al agente: hace visibles los datos detectados, los datos faltantes y los campos obligatorios de una operacion.

## Primer esquema

`purchase.v2` corresponde a `registrar_compra` y separa datos generales de productos comprados.

Campos obligatorios antes de validar la interpretacion:

- fecha de compra;
- proveedor;
- moneda;
- al menos un item con producto, cantidad y unidad;

Campos opcionales:

- comprobante o referencia;
- precio unitario cuando no fue informado.
- descuento por monto o porcentaje;
- total declarado cuando fue mencionado en la entrada.

El descuento y el total declarado solo se muestran cuando fueron extraidos o agregados durante una correccion. Si el total declarado no coincide con subtotal menos descuento, la UI muestra la discrepancia y no decide automaticamente cual valor es correcto.

## Estados de informacion

Cada valor puede indicar procedencia: `extracted`, `calculated`, `suggested`, `corrected`, `enriched`, `clarified` o `missing`.

Validar la interpretacion no registra todavia la compra ni el movimiento de stock como hechos reales. La decision sobre impacto en stock pertenece al flujo operativo posterior.
