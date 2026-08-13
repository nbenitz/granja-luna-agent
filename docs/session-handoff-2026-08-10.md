# Continuidad de trabajo — 10 de agosto de 2026

Estado: `superseded_by_session-handoff-2026-08-11`

La continuidad vigente está en [`session-handoff-2026-08-11.md`](session-handoff-2026-08-11.md).
Este documento se conserva como referencia detallada del trabajo de Marca y Comunidad.

Este documento permite retomar el proyecto en una sesión nueva sin reconstruir la conversación
completa. Los documentos de dominio siguen siendo la fuente detallada; este archivo orienta.

## De dónde venimos

La idea comenzó en la carpeta histórica `agent/` como un sistema multiagente basado en archivos.
Después se descartó esa implementación como sistema activo y se separaron los dominios reales:

```text
personal-agent-platform/   entrada global y coordinación
granja-luna-agent/         operación, ERP agéntico piloto y Marca/Comunidad
nestor-career-repo/        carrera, perfil y oportunidades
revelo/                    proyectos y tareas Revelo
avicola-mbore/             legacy de consulta; no operativo
```

No deben fusionarse en un monorepo ni compartir una base de datos. El Agente Personal descubre
capacidades y delega; cada dominio interpreta sus conceptos, valida, persiste y ofrece su interfaz.
Esta separación corrigió el error inicial en el que el orquestador confundió una puesta de huevos
con una compra.

## Arquitectura vigente

- `personal-agent-platform` ya implementa un `CrewAI Flow` de intake, clasificador híbrido
  LLM/reglas, política determinista, registry de dominios, adapters, PostgreSQL, ChromaDB opcional,
  worker, PWA y fachada MCP.
- `granja-luna-agent` permanece framework-agnostic en su lógica: interpreta el dominio, crea
  borradores, exige confirmación y conserva eventos append-only.
- ChromaDB contiene conocimiento derivado y curado; no es fuente de verdad para operaciones,
  aprobaciones, stock, métricas, credenciales ni medios.
- El LLM interpreta y propone. El código valida riesgo, estado, permisos, persistencia e
  idempotencia.
- La app Personal Agent es la entrada global; la app Granja Luna ofrece la experiencia rica del
  dominio. El usuario puede pasar de una a otra mediante enlace profundo.

## Rol actual de Codex

Codex funciona hoy como laboratorio, agente de entrada y operador supervisado para:

- explorar flujos todavía inestables;
- modificar y probar los repositorios;
- analizar medios y producir derivados;
- operar herramientas o navegador cuando Néstor lo autoriza;
- documentar decisiones, incidentes y métricas.

No debe convertirse en fuente de verdad ni requisito permanente del producto. La integración
actual comprobada es `Codex → MCP del Agente Personal`. Una futura delegación
`Agente Personal → Codex` es técnicamente posible mediante Codex SDK, modo no interactivo o un
adaptador MCP, pero todavía no está implementada ni autorizada como ejecución automática. Debe
incorporarse como proveedor especializado, con sandbox, presupuesto, logs y aprobación según la
acción.

Referencia oficial: `https://learn.chatgpt.com/docs/codex-sdk`.

## Granja Luna y el ERP agéntico

`granja-luna-agent` es el caso piloto del futuro ERP agéntico. Ya existen flujos reales para
movimientos operativos, inventario derivado, galpones, planteles, incubación y cría. No se extraerá
un core genérico hasta que varios flujos repetidos demuestren contratos estables.

La regla continúa siendo:

```text
necesidad real → flujo usable → contrato estable → herramienta → runtime → posible abstracción
```

## Marca y redes sociales

Usar siempre estos nombres:

- dominio: **Marca, marketing y comunidad**;
- función: **Agente de Marca y Comunidad**;
- módulo de la app: **Contenido**;
- espacio de trabajo: **Estudio de contenido**.

No es otro repo ni otro orquestador. Sus roles internos son Estratega, Creador/Community Manager,
Guardián y Analista. El modelo operativo completo está en
`brand/social-media-operating-model.md`.

Estado público:

- Facebook `Granja Luna`, usuario `@GranjaLunaPy`, activo;
- logo provisional y portada configurados;
- publicación de bienvenida y tres reels documentados;
- Instagram y WhatsApp Business todavía pendientes;
- publicación y respuestas oficiales requieren aprobación humana.

Resultados consolidados al 10 de agosto:

- 3,4 mil visualizaciones y 2.332 espectadores;
- 47 seguidores, 468 visitas y 62 interacciones;
- 89,3 % de visualizaciones desde no seguidores;
- reel de la mañana fría: cerca de 1.342 visualizaciones y 11 compartidos;
- reel de cierre: 518 visualizaciones, 10 compartidos y mejor retención final.

Fuente: `brand/reports/2026-08-10-facebook-performance.md`.

Próximo contenido candidato: aves adultas, con el concepto
`Los pollitos no son el comienzo de la historia`. Néstor todavía debe explicar su propia idea y
mostrar o identificar el material. No producir ni publicar sin esa revisión.

## Contenido y biblioteca de medios

Implementado:

- inventario SQLite, miniaturas, ráfagas y curaduría humana;
- análisis Gemini sólo mediante acción explícita;
- carga múltiple JPG/MP4 por tandas desde `Contenido`;
- contexto, progreso, validación, deduplicación e inventario incremental;
- originales y estado persistentes en el host, fuera del contenedor y de Git;
- primer intake persistente del Estudio con referencia a la tanda de medios.

Límite importante: los videos y fotos aisladas necesitan una Biblioteca propia. El cargador no
ejecuta el escaneo global porque la identidad actual de ráfagas puede cambiar al añadir una foto y
eliminar curaduría humana por cascada. Primero debe implementarse reconciliación estable.

El Estudio registra solicitudes, pero todavía no genera briefs o piezas mediante LLM. Codex sigue
resolviendo la producción compleja mientras se observan otras 6–10 piezas.

## Incidentes que no deben repetirse

- Meta puede silenciar falsamente audio ambiente después de editar; verificar localmente, esperar
  el control de copyright y comprobar la URL pública antes de reaccionar.
- El `contenteditable` de Meta dejó el placeholder superpuesto al usar autocompletado. Pegar copy
  como texto plano con una acción real y comprobar que la primera línea se vea una sola vez.
- Los textos altos de Reel quedaron cubiertos en Historia. Revisar ambas vistas desde el teléfono.
- “Publicado” no equivale a entrega correcta: validar audio, copy, miniatura, visibilidad e historia.
- No automatizar publicación estable con una sesión de navegador y un temporizador local.

## Siguiente sesión recomendada

1. Leer este handoff y `brand/social-media-operating-model.md`.
2. Preguntar a Néstor cuál es su idea para el contenido de aves adultas.
3. Identificar los videos concretos y comparar su calidad, acción inicial y coherencia narrativa.
4. Preparar un solo brief antes de editar.
5. Publicar sólo después de preflight y aprobación.
6. Medir a 24 h, 72 h y 7 días y guardar la instantánea.
7. En paralelo, continuar la Biblioteca y los artefactos versionados del Estudio, sin crear todavía
   un crew autónomo.

## Decisiones todavía abiertas

- frecuencia y horarios sostenibles;
- modelo/proveedor por tipo de tarea y presupuesto;
- cuándo incorporar Codex SDK como especialista invocable;
- cuándo migrar el Estudio a un CrewAI Flow propio;
- API oficial de Meta, Instagram y WhatsApp Business;
- autenticación fuerte, notificaciones y acceso remoto estable;
- almacenamiento definitivo de los ledgers de Granja Luna;
- criterios para extraer un `agentic-erp-core` reutilizable.

Nada de esto se considera cerrado por este documento; representa la dirección exploratoria actual.
