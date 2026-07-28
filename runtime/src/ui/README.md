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

El APK ofrece captura directa por micrófono mediante `agent.voice.v1`; el navegador puede usar Web Speech como respaldo cuando el contexto sea seguro. La transcripción queda editable y no se envía automáticamente. La app no guarda audio, aunque el reconocedor del sistema puede procesarlo mediante su proveedor.

La respuesta por audio queda deliberadamente fuera de `UIResponse`: una fase posterior puede definir `agent.audio.v1` con reproducción iniciada por el usuario y coordinación explícita con el micrófono.
