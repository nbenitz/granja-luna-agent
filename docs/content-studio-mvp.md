# Estudio de contenido: arquitectura incremental

Estado: `draft_validated_by_use`

Fecha: 2026-08-08

## Decisión

Marca, marketing y comunidad continúa como un dominio interno de `granja-luna-agent`. No se crea
otro repositorio ni un agente autónomo separado. La interfaz evoluciona hacia un **Estudio de
contenido**: conversación como entrada, casos y artefactos estructurados como fuente de verdad,
versiones revisables y aprobación humana por acción.

No conviene construir todavía un clon completo de Codex. Con tres reels existe evidencia suficiente
para codificar carga, solicitudes, preflight, revisión y métricas, pero no para automatizar
estrategia, edición o publicación. Codex seguirá como laboratorio creativo y supervisor durante al
menos otras 6–10 piezas mientras se estabilizan los patrones.

## Flujo real aprendido

```text
Ingreso de medios
  → inventario y señales técnicas
  → contexto humano
  → análisis local o Gemini explícito
  → selección humana
  → brief y producción iterativa
  → revisión y aprobación
  → publicación
  → verificación técnica pública
  → métricas
  → aprendizaje para la siguiente pieza
```

El chat puede iniciar o explicar el trabajo, pero no será fuente canónica ni autorización
implícita. Cada caso debe tener un identificador que conecte solicitud, medios, artefactos,
aprobación, publicación y resultados.

## Corte implementado

### Subir material

- selección múltiple JPG/MP4 desde navegador o WebView;
- contexto compartido por tanda;
- un archivo por petición, con progreso y continuidad ante errores parciales;
- validación de extensión, firma, integridad, tamaño y espacio libre;
- escritura temporal y movimiento atómico;
- detección de duplicados por SHA-256;
- inventario incremental sin reconstruir ni borrar curadurías existentes;
- recibo persistente por archivo: guardado, duplicado o error;
- originales locales, fuera de Git, ChromaDB y proveedores externos.

El inventario incremental es intencional. El escaneo global actual cambia el identificador de una
ráfaga cuando aparecen nuevos miembros y podría borrar por cascada curaduría humana. El cargador no
lo ejecuta hasta que exista reconciliación de grupos estable.

### Estudio de contenido

La primera superficie captura una solicitud `content-request.v1` con:

- instrucción natural;
- tipo de pieza y canal;
- objetivo, audiencia, estado de la información y llamada a la acción opcionales;
- referencia a una tanda de medios;
- preguntas todavía sin resolver;
- workflow visible desde `idea` hacia brief, borrador, revisión y aprobación.

Esta versión registra el caso; todavía no llama a un LLM ni genera una pieza. Evita crear una caja
negra antes de conocer los artefactos y revisiones que realmente aportan valor.

El primer uso real vinculó una tanda MP4 cargada desde la app con una solicitud y produjo el tercer
reel mediante trabajo supervisado. Esto valida intake y trazabilidad básica, no generación
autónoma.

## Arquitectura objetivo

Las funciones lógicas son Coordinador/Estratega, Creador/Community Manager, Guardián de marca y
Analista. En el MVP son etapas del mismo workflow, no cuatro procesos ni cuatro orquestadores.

Entidades previstas:

- `upload_batches` y `upload_items`;
- `content_requests` y `content_items`;
- `content_asset_links`;
- `content_artifact_versions` para brief, guion, copy, plan de edición y checklist;
- `content_reviews` y `content_approvals`;
- `agent_runs` con proveedor, modelo, entradas, latencia y uso;
- `publications` y `metric_snapshots`;
- `hypotheses`, `learnings` y eventos append-only.

Estados de pieza:

```text
idea → brief → draft ↔ needs_information → ready_for_review
     → approved → scheduled → published → measured
```

También puede terminar en `rejected` o `cancelled`. Una aprobación futura debe identificar versión,
canal y acción; aprobar un texto no autoriza publicar otra versión.

## Preflight obligatorio

Los incidentes del segundo reel demostraron que “Facebook aceptó la publicación” no equivale a
“la entrega quedó correcta”. Antes y después de publicar se debe verificar:

- archivo final y versión correctos;
- relación de aspecto, resolución y duración;
- audio presente y escuchado;
- textos dentro de zonas seguras tanto para reel como para historia;
- descripción persistida;
- privacidad, menores, GPS y afirmaciones públicas;
- bienestar animal y posibles interpretaciones visuales;
- disponibilidad, precio, edad y entrega cuando sea comercial;
- vista previa móvil;
- URL, visibilidad, audio, descripción, portada e historia después de publicar.

## Métricas mínimas

Guardar valores crudos, definición de Meta y fecha de captura. No mezclar visualizaciones, alcance
y espectadores únicos.

- alcance, vistas y espectadores;
- seguidores frente a no seguidores y origen del descubrimiento;
- vistas de 3 segundos, tiempo medio y porcentaje completado;
- reacciones, comentarios, compartidos, guardados y clics;
- visitas al perfil y nuevos seguidores;
- mensajes, consultas, leads y ventas atribuibles;
- ocultamientos, reportes e incidentes de copyright.

Cortes recomendados: QA a los 5–15 minutos; lectura a 24 horas; comparación a 72 horas; consolidado
a 7 días.

## Integración futura con ventas y clientes

Marketing sólo referenciará un `product_id` y una instantánea de oferta leída desde la fuente
canónica de Ventas/Cría. Debe revalidar disponibilidad, precio y condiciones antes de publicar; no
copiará ni descontará stock.

```text
publicación → consulta o mensaje → lead opcional → borrador de venta → aprobación
```

La atribución enlazará campaña/publicación con consulta y venta. Datos personales, conversaciones,
stock, aprobaciones y métricas no irán a ChromaDB. Chroma podrá indexar documentos de marca,
descripciones, transcripciones y aprendizajes previamente aprobados.

## Próximas iteraciones

1. Probar carga física desde el Samsung con fotos y un MP4 real.
2. Crear Biblioteca de activos que incluya videos y fotos aisladas, no sólo ráfagas.
3. Estabilizar identidad y reconciliación de grupos antes de reactivar escaneo global automático.
4. Agregar artefactos versionados y preflight Reel/Historia al Estudio.
5. Incorporar un adaptador de proveedor LLM y jobs persistentes; el código valida estados y riesgo.
6. Registrar publicación y métricas manualmente antes de integrar Meta API.
7. Añadir consultas/leads y atribución sin convertir Marketing en dueño de clientes o stock.
