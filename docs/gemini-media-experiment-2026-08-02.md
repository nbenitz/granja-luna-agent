# Experimento de análisis multimedia con Gemini 3.5 Flash

Estado: `evaluated_with_user_feedback`

Fecha: 2026-08-02

## Objetivo

Comparar `gemini-3.5-flash` con Qwen3-VL 4B sobre los mismos medios reales de Granja Luna y medir
calidad, latencia, uso de cuota, comprensión de video y coincidencia con las primeras etiquetas de
Néstor.

Gemini se evaluó como analista. Ninguna respuesta publicó contenido ni confirmó salud, bienestar,
raza, edad, manejo, disponibilidad o cumplimiento operativo.

## Privacidad aplicada

- la API key vive únicamente en el `.env` local ignorado por Git;
- las fotos analizadas son copias a 1024 px generadas por Pillow, sin EXIF ni coordenadas;
- se revisaron doce fotogramas distribuidos de cada video antes de autorizar su carga;
- no se observaron personas, menores, documentos ni datos sensibles en los tres clips;
- los videos se remuxaron con FFmpeg eliminando metadatos y capítulos;
- cada video se eliminó de Files API en un bloque de limpieza después del análisis;
- una consulta final confirmó `remote_files_remaining=0`.

El nivel gratuito de Gemini puede usar entradas y respuestas para mejorar productos de Google y
puede involucrar revisión humana. Por ello, esta ruta solo debe recibir material clasificado como
apto para procesamiento externo.

## Muestra

- diez fotografías individuales de dos ráfagas;
- dos comparaciones de cinco fotos cada una;
- una comparación adicional de pollitos con intención editorial explícita;
- tres videos completos de 11,8 s, 29,1 s y 72,0 s.

## Rendimiento

### Fotografías

| Prueba | Resultado |
|---|---:|
| Diez fotos, primera pasada | promedio 9,16 s; rango 7,12–14,56 s |
| Tokens totales, primera pasada | 32.457 |
| JSON estricto con solo MIME JSON | 8/10 |
| Dos respuestas defectuosas | contenido correcto con una llave `}` extra |
| Reintento con JSON Schema oficial | 2/2 válidas |
| Configuración final combinada | 10/10 respuestas parseables |

El esquema explícito queda como requisito del cliente. Garantiza sintaxis, no veracidad semántica.

### Comparación de ráfagas

| Ráfaga | Latencia | Tokens | Elección Gemini | Etiqueta humana |
|---|---:|---:|---|---|
| Pollitos, criterio general | 9,92 s | 7.683 | foto 4 | foto 4 panorámica principal; foto 2 detalle secundario |
| Pollitos, intención de detalle explícita | 14,37 s | 8.465 | foto 4 | foto 2 sigue siendo válida como ángulo secundario |
| Pollitos, esquema de hasta dos favoritas | 27,74 s | 8.420 | foto 4 principal + foto 1 secundaria | foto 4 principal + foto 2 secundaria |
| Arcoíris | 10,60 s | 8.081 | foto 1 | foto 1 |

La intención original de la ráfaga de pollitos era panorámica, por lo que Gemini acertó al elegir la
foto 4 como favorita principal. La foto 2 se aparta de ese objetivo, pero merece conservarse como
favorita secundaria porque aporta detalle de caras e interacción. El resultado confirma que la
biblioteca debe admitir hasta dos selecciones por intención, no un único campo universal
`mejor_foto`. Una validación adicional confirmó que Gemini puede producir correctamente la
estructura principal/secundaria, aunque eligió la foto 1 para el detalle en vez de la foto 2; por
eso la selección humana continúa siendo la etiqueta editorial definitiva.

### Videos completos

| Video | Tamaño sanitizado | Latencia total | Tokens | Hallazgo principal |
|---|---:|---:|---:|---|
| `20260719_132833.mp4` | 21,9 MB | 25,0 s | 2.983 | detectó gallo, secuencia y rotación incorrecta de 90° |
| `20260801_180118.mp4` | 54,0 MB | 54,0 s | 4.988 | detectó paneo, flores, viento y canto de gallo |
| `20260523_125447.mp4` | 132,3 MB | 98,3 s | 9.413 | produjo línea temporal, momentos útiles y portada |

Los tres resultados fueron JSON válido y los tres archivos remotos se eliminaron. Gemini superó
claramente al experimento local de fotogramas: utilizó secuencia y audio, detectó problemas globales
y propuso segmentos con marcas de tiempo.

## Fortalezas observadas

- latencia de fotos aproximadamente dos veces menor que Qwen local en la configuración probada;
- cinco imágenes separadas se compararon directamente sin crear lámina;
- mejor identificación literal de viruta, calefacción, audio y secuencia;
- análisis completo de videos con momentos y portadas sugeridas;
- coincidencia con Néstor en la ráfaga del arcoíris;
- capacidad de reconocer el valor panorámico de la foto 4 de pollitos;
- uso de cuota visible por modalidad y respuesta.

## Límites observados

- marcó bienestar para revisión en las cinco fotos individuales de pollitos con argumentos genéricos
  sobre agrupamiento o temperatura;
- propuso contenido educativo sobre temperatura, cama seca o bienestar que necesita evidencia y
  revisión antes de publicarse;
- el esquema inicial forzaba una sola ganadora y no representaba una toma secundaria válida con otro
  ángulo;
- evaluó individualmente `20260801_181046.jpg` como publicable y no vio la obstrucción rosada; al
  compararla dentro de la ráfaga sí detectó el posible dedo y la colocó última;
- asignó confianza alta a juicios discutibles; la confianza del modelo no se toma como probabilidad
  calibrada;
- sigue necesitando métricas deterministas de desenfoque, exposición, similitud y orientación;
- depende de internet, cuota externa, términos de servicio y disponibilidad del proveedor.

## Decisión propuesta

Usar Gemini 3.5 Flash como **analista principal de contenido apto para procesamiento externo** y
Qwen3-VL/Ollama como respaldo privado, local y sin conexión.

```text
original local
    -> inventario, pHash y métricas técnicas
    -> copia sanitizada sin EXIF
    -> filtro local de privacidad
       -> sensible/privado: Qwen local
       -> apto para nube: Gemini Flash
    -> guardián de afirmaciones y bienestar
    -> selección por intención editorial
    -> aprobación de Néstor
```

Gemini no debe descartar automáticamente una foto ni publicar. Su salida es una propuesta versionada
con proveedor, modelo, prompt, tokens y evidencia revisable.

## Siguiente validación

La API y la primera pantalla de fotos quedaron implementadas el 2026-08-02 con miniaturas
sanitizadas, ráfagas temporales, pHash, métricas locales, intenciones múltiples, elección humana
principal/secundaria y la acción explícita `Analizar con Gemini`. La pantalla añade cobertura
concreta para el lanzamiento de Facebook.

El próximo paso es revisar unas veinte ráfagas reales y convertir los espacios sin cubrir en una
lista de nuevas tomas. Siguen pendientes la agrupación automática por distancia perceptual, la
pantalla de video con marcas de tiempo y la carga múltiple desde teléfono.
