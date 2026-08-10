# AGENTS.md — Reglas para agentes y Codex

Estas reglas aplican a cualquier agente que trabaje en este repositorio.

## Principios

1. Este repo representa al **Subagente Granja Luna**, no al sistema legacy `avicola-mbore`.
2. El agente debe aprender desde la operación real, no imponer una estructura clásica de ERP.
3. Markdown es la memoria viva; BD/API/MCP/código deben aparecer solo cuando el flujo lo justifique.
4. No inventar datos de la granja, tratamientos, cantidades, precios, stock, fechas ni decisiones.
5. Distinguir siempre: confirmado, inferido, pendiente, borrador y referencia legacy.
6. Toda acción crítica requiere confirmación humana.

## Antes de modificar

Leer, como mínimo:

1. `README.md`
2. `AGENTS.md`
3. `agent-card.md`
4. `contracts/README.md`
5. `config/risk-levels.md`
6. El archivo de dominio relacionado con la tarea.

Si la tarea toca la arquitectura global o el trabajo actual de redes sociales, leer además
`docs/session-handoff-2026-08-10.md`, que enlaza las fuentes canónicas y el siguiente punto de
reanudación.

## Acciones permitidas sin confirmación especial

- Crear borradores Markdown.
- Clasificar entradas de inbox.
- Proponer cambios.
- Resumir bitácoras.
- Crear templates.
- Mejorar documentación.
- Detectar inconsistencias.

## Acciones que requieren confirmación explícita

- Marcar información como `confirmed`.
- Registrar compra, venta, tratamiento, baja, mortalidad o ajuste de stock como hecho real.
- Modificar procedimientos sanitarios estables.
- Recomendar medicación, dosis o diagnóstico como certeza.
- Diseñar automatizaciones que controlen dispositivos físicos.
- Borrar, archivar o renombrar archivos importantes.
- Cambiar contratos entre agentes.

## Seguridad y privacidad

- No imprimir, registrar, versionar ni exponer secretos.
- Néstor puede mantener credenciales reales en un `.env` local ignorado por Git.
- Los agentes pueden cargar una credencial local únicamente para una integración solicitada
  explícitamente, sin mostrar su valor ni copiarlo a documentación, resultados o logs.
- `.env.example` solo contiene nombres de variables y valores vacíos o ficticios.
- No guardar datos sensibles innecesarios.
- No publicar información de ventas, proveedores o sanidad sin aprobación.
- Las fichas sanitarias son apoyo operativo, no sustituyen asesoramiento veterinario.

## Estilo de trabajo

- Cambios pequeños y trazables.
- Preferir Markdown claro antes que abstracciones complejas.
- Usar listas y tablas solo cuando aporten claridad.
- Registrar decisiones relevantes en `memory/granja/decisiones.md`.
- Revisar `git diff` antes de finalizar.

## Criterio para pasar de Markdown a BD/API/código

Un dato o flujo debería pasar a BD/API/código cuando:

- se repite con frecuencia;
- requiere cálculos confiables;
- tiene impacto económico, sanitario o de inventario;
- necesita auditoría;
- debe ser consultado por fecha, lote, proveedor, producto o estado;
- varias herramientas o agentes deben leerlo/escribirlo.

Mientras sea exploratorio, narrativo o cambiante, debe permanecer en Markdown.
