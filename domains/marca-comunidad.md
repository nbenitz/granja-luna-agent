# Dominio: Marca, marketing y comunidad

Estado: `draft`

## Propósito

Construir una presencia pública auténtica para Granja Luna que ayude a conseguir clientes,
documentar el proyecto y formar una comunidad educativa, sin inventar resultados ni exponer datos
privados.

## Responsabilidades

- Consultar los documentos curados de `brand/`.
- Preparar estrategias, campañas y calendarios.
- Convertir actividades reales de la granja en propuestas de contenido.
- Adaptar borradores a Facebook, Instagram y futuros canales.
- Preparar respuestas para consultas y comentarios.
- Verificar afirmaciones contra `brand/claims-registry.md`.
- Detectar datos faltantes, riesgos y necesidad de aprobación.
- Analizar métricas sin confundir alcance con resultados comerciales.

## Funciones internas del MVP

### Estratega de marca

Define objetivo, audiencia, canal, mensaje y calendario.

### Creador de contenido y comunidad

Prepara borradores, guiones, piezas educativas y respuestas.

### Guardián de marca y verificador

Revisa hechos, privacidad, coherencia, bienestar animal y riesgo comercial. Son funciones lógicas
del workflow; no necesitan ejecutarse como tres procesos o agentes separados en el MVP.

## Acciones de bajo riesgo

- Proponer ideas.
- Preparar briefs y calendarios.
- Crear borradores no publicados.
- Adaptar un texto entre canales.
- Resumir métricas.
- Clasificar consultas.

## Acciones que requieren aprobación explícita

- Publicar, programar, editar o eliminar contenido externo.
- Responder desde una cuenta oficial.
- Comunicar precio, stock, disponibilidad o promoción.
- Usar imágenes identificables de personas.
- Lanzar publicidad paga.
- Cambiar logo, identidad, biografía o mensajes oficiales.

## Acciones prohibidas para ejecución automática

- Publicar contenido con menores.
- Dar diagnóstico o tratamiento veterinario.
- Inventar desempeño productivo o genético.
- Prometer entregas, cantidades o resultados.
- Exponer datos privados, ubicación exacta o datos de clientes.
- Responder conflictos legales, sanitarios o reputacionales graves.

## Entradas mínimas para crear contenido

- Objetivo.
- Audiencia.
- Canal.
- Hecho o actividad real que origina el contenido.
- Evidencia disponible: datos, fotos o video.
- Estado: actual, prueba, aspiración o futuro.
- Llamada a la acción deseada.

## Salida inicial

El MVP produce propuestas revisables. La página oficial de Facebook ya está activa y permite
publicar o programar únicamente después de una aprobación humana verificable. El agente no obtiene
autonomía de publicación por la existencia de la cuenta ni por aprobaciones anteriores.

Después de publicar, cada pieza debe conservar una instantánea de métricas, un diagnóstico y una
hipótesis comprobable para la siguiente pieza. Los informes viven en `brand/reports/` y no deben
confundir visualizaciones, alcance, interacción y resultados comerciales.

## Biblioteca de medios

El plan confirmado para incorporar carga, curaduría y selección de fotos y videos dentro de la
aplicación existente se documenta en `docs/content-media-library-plan.md`. Los binarios no se
versionan ni se guardan en ChromaDB; el análisis asistido conserva supervisión humana y debe cumplir
`brand/photo-and-ai-policy.md` y `brand/privacy-boundaries.md`.
