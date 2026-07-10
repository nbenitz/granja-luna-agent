# Review events

Estado: `draft`

El historial `review-events.jsonl` registra feedback humano append-only sin duplicar el texto original de la entrada.

## Eventos

- `correction_saved`: conserva seccion, motivo y diff antes/despues.
- `review_completed`: conserva decision, resultado y transicion de estado.
- `feedback_curated`: agrega una interpretacion curada sobre un evento anterior sin reescribirlo.

## Estados separados

`review_status` describe la calidad o avance de la interpretacion:

- `pending`;
- `validated`;
- `needs_information`;
- `needs_correction`;
- `rejected`.

`operation_status` describe una operacion futura y empieza siempre en `draft`. Revisar o corregir no cambia este estado.

## Motivos de correccion

- `system_error`: el dato estaba en la entrada, pero el sistema no lo detecto o lo interpreto mal;
- `new_information`: el usuario agrego informacion que no estaba mencionada en la entrada;
- `ambiguous_input`: el usuario aclaro una entrada ambigua.

Una limitacion de producto se registra como `system_limitation`, no como informacion faltante del usuario.

Los diffs estructurados son la fuente principal para evaluacion futura. Las notas libres son contexto opcional, no la etiqueta primaria.

La curaduria puede marcar cada feedback como `eligible`, `not_for_extraction`, `needs_review` o `exclude`. La curaduria tampoco modifica el evento original.
