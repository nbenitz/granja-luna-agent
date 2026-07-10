# UI Runtime

Estado: `mvp_local`

La primera UI de Granja Luna es una web responsive servida por FastAPI desde `runtime/src/web/`.

## Superficies actuales

- captura de texto o dictado mediante el teclado del celular;
- inbox de propuestas pendientes;
- revision en modo lectura con acciones contextuales;
- compra detectada separada en datos generales y productos;
- edicion por seccion en modal independiente con procedencia de valores y feedback estructurado;
- descuento opcional visible solo cuando fue detectado o agregado;
- historial de correcciones y curaduria sin precargar notas antiguas;
- descarte logico disponible sin borrar la trazabilidad;
- actividad de uso local.

## Regla

La UI consume el mismo core que el CLI. Guardar o revisar una entrada no confirma compras, stock, sanidad ni tareas como hechos operativos.

La grabacion directa con microfono y transcripcion local se agregara despues de habilitar HTTPS en la red local.
