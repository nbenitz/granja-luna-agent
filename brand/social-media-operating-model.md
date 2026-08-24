# Modelo operativo de redes sociales — Granja Luna

Estado: `draft_validated_by_use`

Fecha de corte: 2026-08-10

## Nombre y ubicación

Para mantener un vocabulario estable:

- **Dominio:** Marca, marketing y comunidad.
- **Función agéntica:** Agente de Marca y Comunidad.
- **Interfaz:** `Contenido` → `Estudio de contenido`, dentro de la app de Granja Luna.
- **Funciones internas:** Estratega, Creador/Community Manager, Guardián de marca y Analista.

Estas funciones son etapas lógicas de un mismo flujo. No justifican todavía cuatro procesos, cuatro
agentes autónomos ni otro repositorio. Granja Luna conserva los hechos, la identidad, los medios y
las reglas; el Agente Personal sólo enruta o presenta el resultado.

## Objetivo actual

La primera etapa busca construir una comunidad y una reputación auténtica antes de convertir la
página en un catálogo. Los objetivos conviven, pero no tienen el mismo peso:

1. atraer a familias, amantes de animales, aves y naturaleza;
2. mostrar cuidado cotidiano, trabajo real y aprendizaje;
3. construir confianza en Granja Luna y en sus futuros productos;
4. generar consultas y ventas verificables sin forzar una llamada comercial en cada pieza;
5. aprender qué formatos, temas y públicos justifican automatización.

La protagonista es Granja Luna como identidad propia. Animales, paisaje, procesos, planteles y
evolución del emprendimiento ocupan el centro; propietarios y colaboradores actúan como guías
discretos. Una cuenta personal puede ampliar distribución o atender una consulta, pero no debe
reemplazar a la página como fuente institucional ni convertir a su titular en rostro de la marca.

## Flujo canónico

```text
idea o hecho real
  → carga de fotos o videos con contexto
  → inventario y análisis técnico local
  → contexto humano y curaduría
  → brief con objetivo, audiencia, canal y evidencia
  → propuesta de guion, edición, copy y miniatura
  → revisión de marca, privacidad, bienestar y datos comerciales
  → aprobación explícita de la versión y del canal
  → publicación o programación
  → QA público de audio, texto, portada, visibilidad e historia
  → métricas a 24 h, 72 h y 7 días
  → hipótesis documentada para la siguiente pieza
```

El chat sirve para iniciar y explicar el trabajo. La fuente de verdad debe ser un caso trazable con
medios, artefactos versionados, aprobación, URL y métricas. Una aprobación de texto no autoriza a
publicar otra versión ni a responder desde la cuenta oficial.

### Puente de carga supervisada hacia Meta

Chrome DevTools no puede seleccionar archivos desde todas las carpetas internas del repositorio,
aunque Codex sí pueda leerlas. Para evitar repetir intentos fallidos, toda carga supervisada a Meta
desde el navegador sigue este procedimiento:

Antes de intervenir en Facebook o Meta Business Suite, verificar que Chrome use `Profile 1`, con
nombre visible `Nestor`, asociado a `yonestor87@gmail.com`. No continuar desde otro perfil aunque
la página de Facebook parezca accesible: cerrar esa sesión controlada y volver a abrir el perfil
correcto antes de cargar, editar o programar contenido.

1. conservar el MP4 aprobado como fuente maestra en `runtime/state/content-studio/social-drafts/`
   y su copia local en `media/selected/social-drafts/`;
2. calcular el SHA-256 de la fuente maestra;
3. copiar exactamente ese archivo a `/tmp/` con el mismo nombre y verificar que ambos hashes sean
   idénticos;
4. entregar a Chrome DevTools únicamente la ruta temporal `/tmp/<archivo>.mp4`;
5. esperar carga al 100 %, procesamiento, dimensiones y control de derechos de Meta;
6. eliminar sólo la copia temporal después de confirmar la carga; nunca borrar la fuente maestra;
7. no improvisar un servidor HTTP sin autenticación para exponer originales como alternativa.

La copia temporal es un transporte local, no una nueva versión editorial. La aprobación continúa
atada al hash, versión, canal, copy, miniatura y horario exactos.

Si el conector no negocia ninguna raíz de archivos y rechaza incluso la copia temporal, no se debe
publicar un texto sin medio ni exponer el original por HTTP. Se puede usar, sólo para una acción ya
aprobada y con la sesión de Chrome autenticada, una conexión local directa para adjuntar el archivo.
El editor y el resultado público deben mostrar el adjunto exacto antes de declarar la acción completa.
No convierte ese recurso de recuperación en una automatización recurrente de publicaciones.

### Descripción en el editor de Meta

Para que la descripción de un reel quede guardada como copy de la publicación y no como texto
superpuesto en el video:

1. crear o programar primero el reel con el campo de descripción inicial vacío;
2. abrir el reel programado desde `Contenido > Programadas > Acciones > Editar publicación`;
3. enfocar el campo **Texto** y pegar o escribir allí el copy una sola vez, como entrada real de
   usuario;
4. no usar **Editar video** para introducir la descripción: esa ruta modifica el contenido visual,
   puede superponer texto y vuelve a involucrar el procesamiento del video;
5. esperar hasta que la descripción aparezca también en la vista previa del feed;
6. programar/guardar sin cambiar el archivo ni el horario aprobados;
7. volver a `Contenido > Programadas`, recargar la vista y confirmar que la fila muestra el copy
   completo; si dice
   `Tu reel`, la descripción no persistió y el preflight no está completo.

No basta con que una automatización asigne un valor al control: Meta puede mostrarlo temporalmente
sin registrarlo. La comprobación posterior a la reapertura es obligatoria.

### Reel compartido en Historia

Cuando la intención sea mostrar un fragmento reproducible del reel dentro de la historia:

1. usar la acción **Compartir > Tu historia** desde la app Android de Facebook;
2. revisar la vista previa nativa y no agregar música, texto, stickers o efectos salvo aprobación
   específica;
3. no usar para este propósito el flujo equivalente de Facebook web: en las pruebas del 6 y 11 de
   agosto creó una tarjeta estática enlazada al reel;
4. después de publicar, abrir `Meta Business Suite > Contenido > Historias > Activas` y exigir que
   Meta clasifique el resultado como **Video**, con duración visible;
5. una fila **Foto · 6 segundos**, una imagen JPG o el estado **Sin sonido** no confirma una historia
   de video, aunque la tarjeta abra el reel al tocarla;
6. si el resultado es foto, detener futuras distribuciones equivalentes y corregir sólo con
   autorización explícita para eliminar y volver a publicar.

La referencia validada es una vista previa nativa de **Video · 16 segundos**. La comprobación del
tipo de medio es parte del QA y debe ocurrir antes de declarar completa la distribución.

## Responsabilidades

### Néstor

- aporta el contexto que una imagen no puede revelar;
- confirma hechos, parentescos, razas, disponibilidad y objetivos;
- decide qué representa el espíritu de Granja Luna;
- aprueba publicación, edición posterior, respuesta oficial y cualquier uso de personas;
- corrige preferencias editoriales sin tener que justificar cada descarte técnico.

### Colaboradores humanos

- Limpia y Néstor trabajan directamente en el emprendimiento; Liz Michel participa con menor
  actividad mientras está de viaje;
- pueden aportar contexto, distribuir una pieza o atender consultas según el flujo acordado;
- no se los presenta automáticamente como propietarios ni como imagen principal de venta;
- su presencia pública se evalúa por pieza y queda subordinada al protagonismo de Granja Luna.

### Agente de Marca y Comunidad

- organiza la solicitud y detecta faltantes;
- propone objetivo, gancho, relato, copy, miniatura y distribución;
- compara variantes mediante criterios explícitos;
- controla coherencia, evidencia, privacidad, bienestar percibido y riesgo comercial;
- registra publicación, incidentes, métricas y aprendizajes;
- nunca inventa stock, salud, parentesco, desempeño genético o condiciones de entrega.

### Código y herramientas

- validan formatos, versiones, estados, hashes y permisos;
- generan derivados reproducibles y conservan auditoría;
- ejecutan sólo la acción exacta que fue aprobada;
- no delegan reglas críticas ni transiciones de estado a un LLM.

## Ciclo editorial exploratorio

Todavía no existe evidencia para fijar un calendario definitivo. Durante las próximas 6–10 piezas
se trabajará con una cadencia orientativa de 2 o 3 reels por semana, historias vinculadas cuando
aporten contexto y publicaciones estáticas sólo cuando el material lo justifique. La frecuencia se
reduce si no hay una pieza suficientemente buena o si la operación de la granja no permite revisar.

El equilibrio inicial debe rotar entre:

- animales y personalidad;
- crianza responsable y mejoras reales;
- vida libre, pastoreo y naturaleza;
- razas, reproductores y genética explicada sin promesas;
- trabajo, infraestructura y profesionalismo;
- humor y comportamiento natural;
- educación y curiosidades respaldadas;
- producto y disponibilidad confirmada.

No se considera saturación mostrar pollitos varias veces si cada pieza cuenta algo distinto. Sí se
considera repetición cuando se reutilizan el mismo plano, emoción, estructura y llamada a la acción
sin una nueva observación.

## Aprendizajes de las primeras piezas

Los criterios detallados para montaje audiovisual se mantienen en
[`video-editing-guidance.md`](video-editing-guidance.md). Son heurísticas vivas: orientan la primera
versión y hacen explícitos los compromisos, pero no sustituyen la revisión de cada historia.

- El primer fotograma debe mostrar un sujeto o una acción reconocible.
- El principal abandono ocurre alrededor del segundo 3; el gancho debe estar activo antes.
- El reel de la mañana fría funcionó como descubrimiento y logró 11 compartidos.
- El reel del cierre del día tuvo menos distribución, pero mejor retención y otros 10 compartidos.
- Los primeros planos y el cuidado emocional equilibraron la audiencia: el reel nocturno terminó
  cerca de 46 % mujeres y 54 % hombres, con Paraguay como país principal.
- El audio ambiente aporta identidad, pero debe escucharse localmente y verificarse de nuevo en la
  URL pública.
- El editor `contenteditable` de Meta no es confiable con autocompletado ni asignación directa del
  control; el copy se pega o escribe como entrada real, se espera su aparición en la vista previa y
  se comprueba de nuevo en `Contenido > Programadas` después de guardar.
- Reel e Historia requieren una zona segura común y una revisión real desde el teléfono.
- La edición debe permitir tres acciones sin hacerlas competir: entender la historia, leer el texto
  y observar a los animales. En general, la escena se estabiliza, el texto se lee y luego queda una
  respiración visual antes del siguiente corte.
- La limpieza del fondo no debe eliminar una acción emocional claramente superior; las
  imperfecciones menores se evalúan contra la función narrativa, la privacidad y el protagonismo.
- No se ralentizan ni repiten tomas sólo para alcanzar una duración. Un reel más corto es válido si
  cuenta mejor la historia.

Las cifras completas y sus límites están en `brand/reports/`.

## Proyección de crecimiento

Con tres reels no es responsable prometer una cantidad mensual de seguidores o ventas. La primera
proyección es un plan de aprendizaje con umbrales de decisión:

### Próximas 4 semanas

- alcanzar una muestra de 8–12 reels revisados;
- probar 3–5 series editoriales distintas;
- sostener descubrimiento mayoritariamente orgánico y medir cuánto público es local;
- elevar el promedio de reproducción desde la línea base de 6 segundos;
- mejorar la retención final de piezas de 15–22 segundos hacia 25 % cuando el material lo permita;
- conservar los compartidos externos verificables como señal principal de afinidad;
- separar compartidos propios o impulsados por Néstor, Limpia u otras cuentas vinculadas antes de
  interpretar el contador agregado como respuesta orgánica;
- introducir una primera llamada comercial suave con disponibilidad real;
- atribuir consultas manualmente a una publicación concreta.

### Semanas 5–8

- conservar sólo las series que repitan buenos resultados;
- probar Facebook e Instagram sin duplicar trabajo manual innecesario;
- definir WhatsApp Business y un flujo de respuesta/aprobación;
- comparar contenido de descubrimiento, confianza y conversión;
- comenzar un catálogo mínimo leído desde Ventas, sin copiar stock dentro de Marketing.

### Semanas 9–12

- decidir una cadencia sostenible con datos propios;
- automatizar captura de métricas y artefactos repetitivos;
- conectar consulta → lead → borrador de venta con aprobación;
- evaluar anuncios pagos únicamente después de identificar una pieza y una oferta orgánicamente
  válidas.

La previsión numérica de crecimiento se hará recién después de 8–12 reels, separando seguidores
orgánicos, invitaciones, alcance local, consultas y ventas. Las visualizaciones por sí solas no son
una proyección comercial.

## Métricas y cortes

- **5–15 minutos:** QA de entrega; no evaluación editorial.
- **24 horas:** distribución inicial, audio, retención temprana e interacción.
- **72 horas:** comparación principal entre piezas.
- **7 días:** consolidado, audiencia, visitas, seguidores, consultas y aprendizaje.

Conservar valores crudos y fecha de captura para: visualizaciones, espectadores, alcance cuando
Meta lo muestre, 3 segundos, 15 segundos, promedio, curva de retención, reacciones, comentarios,
compartidos, guardados, visitas, seguidores, países/regiones, mensajes e incidentes.

Para cada distribución realizada por la propia granja registrar además: cuenta que compartió,
fecha, destino —perfil, historia o grupo— y enlace cuando exista. El contador de Meta debe separarse
en `compartidos_totales_observados`, `compartidos_propios_confirmados` y
`compartidos_externos_estimados`. Si Meta no revela las identidades o faltan registros propios, el
origen queda `pending_attribution` y el total no se usa por sí solo como señal de afinidad orgánica.

### Prueba recomendada desde una cuenta personal

Para evaluar el antecedente favorable observado con Liz sin confundir alcance personal con
distribución de grupos:

1. preparar una pieza comercial nativa y pública para la biografía de Limpia, con Granja Luna como
   sujeto y sin convertir el perfil en catálogo ni destacar la propiedad;
2. compartir esa publicación en un grupo prioritario;
3. subir una variante equivalente de forma nativa en otro grupo comparable;
4. medir durante 48–72 horas reacciones, comentarios, consultas, procedencia y ventas confirmadas;
5. registrar cada compartido propio antes de interpretar el contador agregado.

Es un experimento recomendado, no una autorización permanente ni una publicación ya aprobada.

## Próxima hipótesis editorial

Después de dos piezas consecutivas de pollitos, conviene cambiar el sujeto visual a aves adultas
sin abandonar la historia:

> Los pollitos no son el comienzo de la historia.

El material debe abrir con un gallo o una gallina completamente reconocible, mostrar conducta o
personalidad y cerrar con el cuidado de los reproductores o del plantel. Sólo se afirmará que son
progenitores de determinados pollitos si está confirmado. La alternativa humorística se elegirá si
el video contiene una conducta suficientemente clara.

## Automatización gradual

1. **Actual:** Codex ayuda a analizar, editar, operar el navegador y documentar; Néstor aprueba.
2. **Siguiente:** el Estudio conserva briefs, artefactos, revisiones, preflight y métricas.
3. **Luego:** un router asigna tareas acotadas a modelos locales o remotos y registra costo,
   proveedor, versión y resultado.
4. **Después:** integración oficial con Meta para programar y leer métricas; publicar sigue
   requiriendo aprobación.
5. **Más adelante:** respuestas y campañas semiautomáticas vinculadas con clientes y ventas.

No se automatizará la publicación mediante control frágil del navegador como mecanismo de
producción. Las pruebas de navegador seguirán siendo una herramienta supervisada hasta contar con
API oficial, idempotencia, autenticación y auditoría.

## Decisiones abiertas

- frecuencia definitiva y horario por tipo de pieza;
- criterios de apertura de Instagram y WhatsApp Business;
- identidad visual definitiva y eslogan;
- tratamiento de menores y familiares en contenido;
- catálogo, reserva, entrega y atención posventa;
- métricas objetivo después de completar la primera muestra;
- proveedor o modelo por tarea y presupuesto mensual;
- alcance exacto de la futura automatización de Meta.
