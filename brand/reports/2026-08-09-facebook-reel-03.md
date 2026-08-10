# Reel 03 — cierre del día con pollitos

Estado: `published — verificado`

Canal propuesto: Facebook Reel

Solicitud: `content-90670e03da14423d`

Tanda de medios: `upload-a8cb17bcf4ee44ab`

## Objetivo editorial

- Continuar la historia del reel sobre la mañana fría y el criadero de dos niveles.
- Mostrar la revisión tranquila del final del día: pollitos alimentándose, acurrucándose y durmiendo.
- Conectar desde el cuidado cotidiano y la gratificación emocional, sin convertir la pieza en una
  venta explícita.

## Fuente y selección

- Original: `media/inbox/imports/2026/08/09/upload-a8cb17bcf4ee44ab/001-fb7bf7e6-302758.mp4`.
- Duración original: 73,2 segundos, 1920×1080 horizontal, HEVC y AAC.
- Fragmentos: `00:00–00:05`, `00:20–00:25.5`, `00:45–00:51` y `01:02.5–01:10`.
- Se excluyó el tramo donde la puerta y la malla obstruyen la escena.
- El encuadre se convirtió a 9:16 mediante recorte central, conservando comederos, grupo y primeros
  planos.

## Borrador

- Archivo: `media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v1.mp4`.
- Duración: 24,1 segundos.
- Formato: 1080×1920, H.264 High, 30 fps, AAC estéreo 48 kHz.
- Audio: ambiente original, normalizado sin música añadida.
- Texto ubicado dentro de una zona central segura para Reel e Historia.

Textos incorporados:

1. `Esta mañana te mostramos cómo pasan el frío.`
2. `Ahora, antes de terminar el día…`
3. `volvemos a mirar si está todo bien.`
4. `Algunos comen. Otros ya duermen.`
5. `Pequeñas cosas que llenan el alma.`

## Revisión pendiente

- Confirmar ritmo y duración de cada escena.
- Confirmar texto y tono emocional.
- Escuchar el audio ambiente completo desde el teléfono.
- Verificar que los cortes de audio resulten naturales.
- Aprobar el borrador antes de preparar descripción, portada o programación.

## Revisión V2

Néstor detectó que la transición cercana al segundo 10 exigía demasiado esfuerzo visual: el plano
entraba muy cerrado y antes de que pudiera reconocerse un pollito completo. La V2 aplica:

- entrada del tercer fragmento en `00:46`, con grupo y comedero reconocibles desde el primer cuadro;
- acercamiento final desde `01:08`, comenzando directamente sobre varias caritas;
- recorte central de 768 px sobre fondo desenfocado, 26 % más ancho que el recorte de la V1;
- disolvencias audiovisuales de 300 ms para preservar la dirección de la mirada;
- duración estimada de 21,4 segundos.

Archivo: `media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v2.mp4`.

## Texto final de la V2

Se reemplazó el inicio dependiente del reel anterior por un gancho híbrido: la pieza se entiende
por sí sola y, al mismo tiempo, conserva la continuidad para quienes vieron la publicación de la
mañana.

1. `¿Y cómo terminan el día estos pollitos?`
2. `Esta mañana te mostramos cómo pasan el frío.`
3. `Ahora volvemos a revisar que todo esté bien.`
4. `Algunos comen. Otros ya duermen.`
5. `Pequeñas cosas que llenan el alma.`

Validación técnica final:

- duración: 21,5 segundos;
- formato: 1080×1920, H.264, 30 fps, AAC estéreo a 48 kHz;
- audio: ambiente original normalizado, sin música externa;
- cinco textos comprobados visualmente dentro de la zona segura central.

## Publicación final

- Fecha y hora: 8 de agosto de 2026, 23:15 (America/Asuncion).
- URL pública: `https://www.facebook.com/reel/1933881598018640`.
- ID de contenido en Meta Business Suite: `122106854313420801`.
- Archivo publicado: `media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v2.mp4`.
- SHA-256: `f0c6dbc70a54df0ab2da25e861f39a9a324b314b80b7bfe365fe1098113046d7`.
- Miniatura: cuadro final cercano a `00:21`, con varias caras de pollitos reconocibles.
- Subtítulos automáticos: desactivados.
- Audio: ambiente original al 100 %, sin música añadida.
- Historia: compartida sólo para esta publicación; Meta creó una vista previa nativa de 6 segundos.
- ID de la historia: `1056021173568463`.

Descripción publicada:

> Esta mañana te mostramos cómo pasan el frío. 🐥❄️
>
> Antes de terminar el día hacemos una última recorrida. Algunos siguen comiendo, otros se
> acurrucan y ya empiezan a dormir.
>
> Uno viene a comprobar que esté todo bien… y termina quedándose un ratito mirando cada carita.
>
> Pequeñas cosas que llenan el alma. 🌙
>
> #GranjaLuna #Pollitos #VidaEnLaGranja #CrianzaResponsable #Paraguay

## Verificación posterior

- El reel se abrió desde su URL pública.
- La descripción completa quedó guardada en Meta Business Suite y la primera línea se mostró en la
  vista pública.
- El reproductor identificó el audio como `Audio original`.
- Néstor comprobó el audio público con auriculares JBL; no existe silenciamiento por copyright.
- No se detectaron avisos de error ni reclamos de derechos de autor.
- La historia asociada quedó activa.
- No se hicieron ediciones después de publicar.

## Incidente y aprendizaje operativo

Un primer intento quedó en un estado incorrecto después de editarlo y fue eliminado, incluso de la
papelera. URL descartada: `https://www.facebook.com/reel/1592691778874214`; ID de contenido:
`122106846465420801`.

La causa observable fue el comportamiento del campo `contenteditable` de Meta: el autocompletado
dejaba visible el texto de ayuda `Explica a los espectadores…` superpuesto a la primera línea, aunque
el texto pareciera existir en el DOM. Para evitarlo, la descripción final se copió al portapapeles y
se pegó con una acción real de `Ctrl+V`. Antes de continuar se confirmó que el texto de ayuda había
desaparecido y que la descripción se veía una sola vez, sin líneas encimadas.

La previsualización silenciosa del compositor tampoco debe interpretarse como ausencia de audio. Si
ocurre, se valida primero el archivo local y luego el reproductor público; no se edita una publicación
correcta sólo para intentar reparar la previsualización.
