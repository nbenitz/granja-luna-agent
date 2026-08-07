# Plan del modulo Contenido y biblioteca de medios

Estado: `confirmed_by_user`

Fecha de decision: 2026-08-01

Implementacion: inventario SQLite y rafagas temporales disponibles desde 2026-08-01; desde
2026-08-02 tambien existen API y pantalla movil de curaduria, miniaturas y vistas ampliadas sin
EXIF, hash perceptual, contexto editorial, selección principal/secundaria o ninguna, motivos rápidos
y análisis explícito con Gemini. La carga movil, video y la agrupación por distancia perceptual
siguen pendientes.

## Objetivo

Incorporar en la aplicacion existente de Granja Luna una forma simple de tomar o seleccionar fotos
y videos desde el telefono, conservar su contexto y convertirlos en candidatos trazables para
contenido de redes sociales. No se crea otra aplicacion ni otro repositorio.

## Alcance funcional

La navegacion de Granja Luna incorporara una seccion `Contenido` con cuatro superficies iniciales:

- `Subir`: camara, galeria y carga multiple;
- `Biblioteca`: inventario, busqueda, filtros y contexto;
- `Seleccionadas`: material elegido para una campaña o publicacion;
- `Publicaciones`: relacion entre recursos, borradores y publicaciones aprobadas.

La primera superficie implementada es `Contenido > Curaduria`. Revisa toda la biblioteca por su
valor editorial presente o futuro. Dentro de ella se mide la cobertura del lanzamiento de Facebook:
portada, bienvenida, pollitos caseros, Brahma, proyecto Black Star, vida natural y conversación. La
foto de perfil o logo se gestiona como pieza de identidad separada.

Cada lote de carga podra recibir contexto compartido y cada recurso conservara, como minimo:

- tipo de medio y nombre original;
- fecha capturada y fecha importada;
- procedencia y autoria;
- descripcion y notas del usuario;
- animales, raza, plantel, lugar o actividad, cuando se conozcan;
- caracter actual, historico, aspiracional o desconocido;
- presencia de personas, menores o informacion privada;
- estado de curaduria y usos sugeridos;
- campaña o publicacion asociada;
- huella para detectar duplicados y grupo de tomas similares.

## Estados de curaduria

`new` -> `needs_context` -> `reviewed` -> `selected` -> `prepared` -> `published`

Desde la revision un recurso tambien puede pasar a `private`, `quality_reject` o `archived`. Estos
estados no eliminan el original.

## Almacenamiento

- Los binarios no se guardan en Git ni en ChromaDB.
- Los originales viven en un volumen persistente separado de la imagen Docker.
- El MVP usa SQLite para metadatos, estados, campañas y auditoria.
- La interfaz usa miniaturas y derivados optimizados, sin modificar el original.
- Todo derivado destinado a publicacion elimina GPS y metadatos privados.
- ChromaDB puede indexar descripciones, etiquetas o transcripciones para busqueda semantica; no es
  el almacen principal de fotos o videos.
- Debe existir una estrategia de respaldo independiente del repositorio antes de considerar el
  modulo como productivo.

## Analisis y seleccion asistida

El pipeline propuesto separa tareas deterministas de tareas de IA:

1. inventario tecnico: formato, bytes, dimensiones, duracion, orientacion y metadatos;
2. huella exacta para duplicados binarios;
3. huella perceptual y cercania temporal para agrupar rafagas o angulos parecidos;
4. extraccion de fotogramas representativos en videos;
5. analisis visual contextualizado para describir contenido, calidad y riesgos;
6. puntuacion explicable por uso: portada, feed, historia, reel, educacion, venta o archivo;
7. comparacion dentro de cada grupo similar y recomendacion de las mejores opciones;
8. seleccion o descarte siempre revisable por Nestor.

La IA puede recomendar, etiquetar y preparar borradores. No puede borrar originales, afirmar una
raza o condicion sanitaria como certeza, publicar ni usar imagenes identificables de personas sin
la aprobacion exigida por las politicas de marca.

## Experiencia movil

La primera implementacion probara carga multiple mediante el selector de archivos de la web que ya
vive dentro del cliente Expo/WebView. Si la experiencia de camara, galeria, permisos o cargas en
segundo plano no resulta confiable en Android, se incorporara un selector nativo de Expo y un
puente versionado hacia la web.

## Iteraciones

### 1. Inventario y carga

- carga multiple desde telefono;
- volumen persistente;
- metadatos SQLite y miniaturas;
- biblioteca con estados basicos;
- limites, validacion de formatos y progreso de carga.

### 2. Curaduria

- contexto por lote y por recurso;
- filtros, privacidad y trazabilidad;
- duplicados exactos y grupos de fotos similares;
- asociacion con las primeras campañas.

### 3. Asistencia agentica

- descripciones y etiquetas sugeridas;
- evaluacion de calidad y riesgos;
- puntuaciones por posible uso;
- fotogramas y resumen de videos;
- borradores de contenido y pedidos de nuevas tomas.

### 4. Publicacion asistida

- derivados aprobados por canal;
- vista previa y aprobacion humana;
- integracion futura con Meta sin compartir credenciales en el repositorio;
- registro de URL, version, fecha y metricas.

## Fuera del MVP inicial

- publicacion automatica;
- borrado automatico de originales;
- diagnosticos veterinarios desde imagenes;
- reconocimiento de personas;
- presentacion de material generado por IA como evidencia real de la granja;
- dependencia obligatoria de un proveedor externo de IA.
