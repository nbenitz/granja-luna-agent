# Prompt: recopilar casos reales desde conversaciones

Uso: pegar este prompt en ChatGPT, Gemini u otro asistente donde existan conversaciones previas sobre Granja Luna.

Objetivo: recopilar entradas reales o realistas para alimentar el dataset de aprendizaje del runtime de Granja Luna, sin convertir datos operativos en hechos confirmados.

---

Actua como curador de datos operativos para el proyecto **Granja Luna Agentic ERP**.

Necesito que revises conversaciones previas conmigo relacionadas con la operacion de Granja Luna y me ayudes a preparar **casos reales de entrada de texto** para un sistema de aprendizaje.

## Contexto del proyecto

Estoy construyendo un runtime agentico para gestionar Granja Luna desde lenguaje natural.

El sistema recibe entradas como mensajes escritos o notas de voz transcritas, y debe detectar:

- intencion;
- dominio principal;
- dominios secundarios;
- datos detectados;
- datos faltantes;
- nivel de riesgo;
- confirmacion requerida;
- borradores sugeridos;
- posibles modulos o workflows emergentes.

El sistema todavia opera en modo `dry_run`.

Regla central:

```text
analizar y proponer, no registrar hechos reales sin confirmacion humana
```

## Estados de informacion

Usa siempre estos estados:

- `confirmed`: dato confirmado y estable.
- `confirmed_by_user`: dato confirmado explicitamente por mi.
- `pending_review`: dato util pero pendiente de validar.
- `draft`: borrador.
- `legacy_reference`: referencia historica, no operativa.
- `inferred`: inferido por el asistente, debe tratarse con cuidado.

Si dudas, usa `pending_review` o `inferred`.

No inventes datos de la granja.

## Dominios actuales

Clasifica cada entrada en uno o mas de estos dominios:

- `compras`;
- `stock-insumos`;
- `alimentacion`;
- `sanidad`;
- `ventas`;
- `incubacion`;
- `infraestructura`;
- `tareas-mantenimiento`;
- `reportes`;
- `reproductores`;
- `finanzas`;
- `otro`.

## Intenciones candidatas

Usa estas intenciones cuando correspondan:

- `registrar_compra`;
- `registrar_movimiento_stock_borrador`;
- `analizar_existencias_reposicion`;
- `crear_tarea_borrador`;
- `registrar_evento_sanitario_borrador`;
- `registrar_venta_borrador`;
- `preparar_reporte`;
- `registrar_bitacora_borrador`;
- `analizar_decision_operativa`;
- `detectar_workflow_candidato`;
- `preguntar_datos_faltantes`.

Si una entrada no encaja, propon una intencion nueva como `candidate_intent`, pero marcala como `draft`.

## Niveles de riesgo

Usa:

- `bajo`: lectura, resumen, clasificacion, borrador.
- `medio`: puede afectar datos operativos, tareas, memoria, compras o stock.
- `alto`: puede afectar dinero, sanidad, inventario, ventas o decisiones importantes.
- `critico`: puede afectar vida animal, seguridad, dispositivos fisicos o datos sensibles.

Compras, ventas, sanidad y stock real normalmente requieren confirmacion.

## Ejemplos de entradas que ya tenemos

Ejemplo 1:

```text
Compre 2 bolsas de maiz a 95000 cada una
```

Lectura esperada:

- intencion: `registrar_compra`;
- dominio principal: `compras`;
- secundarios: `stock-insumos`, `alimentacion`;
- riesgo: `medio`;
- requiere confirmacion: `true`;
- datos detectados: producto maiz, cantidad 2, unidad bolsa, precio unitario 95000;
- datos faltantes: fecha real, proveedor, comprobante, confirmacion de impacto en stock.

Ejemplo 2:

```text
Hola, estoy en el deposito, te quiero comentar cuantos de balanceados tenemos. Tengo una bolsa de crecimiento abierto, mas o menos al setenta por ciento, 1 bolsa de maiz molido de 40 kilogramos tambien al 70 por ciento aproximadamente, una bolsa de iniciador a la mitad, 1 bolsa y un cuarto de ponedora, o sea, una bolsa entera y uno abierto, que queda un cuarto por ahi. Eso es todo, creo que ya me va a faltar el maiz. Hasta cuando me va a durar estas existencias? Que debo comprar minimamente la proxima que vaya al proveedor?
```

Lectura esperada:

- intencion: `analizar_existencias_reposicion`;
- dominio principal: `stock-insumos`;
- secundarios: `reportes`, `compras`, `alimentacion`;
- riesgo: `medio`;
- requiere confirmacion: `true`;
- observaciones detectadas:
  - crecimiento: 0.7 bolsa estimada;
  - maiz molido: 0.7 bolsa, 40 kg por bolsa, 28 kg estimados;
  - iniciador: 0.5 bolsa;
  - ponedora: 1.25 bolsas;
- datos faltantes:
  - consumo diario aproximado;
  - cantidad de aves/lotes;
  - stock minimo deseado;
  - fecha de proxima visita al proveedor;
  - precios actuales si se quiere preparar compra.

## Tu tarea

Revisa conversaciones previas conmigo sobre Granja Luna y extrae casos de entrada.

Si no tienes acceso directo al historial, pedime que pegue fragmentos o exportaciones de conversaciones. Si si tienes acceso al historial, usa solo conversaciones relacionadas con operacion de Granja Luna.

Quiero casos variados, incluyendo:

- compras claras;
- compras incompletas;
- inventario observado;
- consumo de alimento;
- pedidos de reporte;
- tareas de mantenimiento;
- eventos sanitarios;
- incubacion;
- ventas;
- infraestructura;
- decisiones operativas;
- frases ambiguas;
- entradas largas de nota de voz;
- entradas mezcladas con varias intenciones;
- entradas con porcentajes, fracciones, unidades o precios;
- entradas que deberian pedir datos faltantes;
- entradas que podrian revelar un modulo o workflow candidato.

## Formato de salida

Primero dame un resumen breve:

```markdown
## Resumen

- Cantidad de casos encontrados:
- Dominios cubiertos:
- Intenciones cubiertas:
- Casos ambiguos:
- Workflows candidatos detectados:
```

Luego entrega una tabla:

```markdown
| ID | Entrada resumida | Intencion esperada | Dominio principal | Riesgo | Confirmacion | Estado |
|---|---|---|---|---|---|---|
```

Luego entrega los casos en JSON:

```json
[
  {
    "id": "caso-breve-y-estable",
    "source": "chatgpt|gemini|pegado_por_usuario|otro",
    "source_context": "breve descripcion del origen sin exponer datos sensibles",
    "input_text": "texto original o transcripcion",
    "information_status": "pending_review",
    "expected": {
      "intent": "registrar_compra",
      "candidate_intent": null,
      "primary_domain": "compras",
      "secondary_domains": ["stock-insumos"],
      "risk_level": "medio",
      "requires_confirmation": true,
      "detected_data": {
        "items": []
      },
      "missing_data": [],
      "suggested_drafts": [],
      "should_not_do": [
        "no registrar como hecho confirmado sin confirmacion"
      ]
    },
    "learning_notes": [
      "que deberia aprender el router de este caso"
    ],
    "module_or_workflow_candidate": {
      "is_candidate": false,
      "name": null,
      "reason": null
    }
  }
]
```

## Reglas importantes

- No inventes fechas, cantidades, precios, proveedores, tratamientos ni ventas.
- No conviertas datos conversacionales en `confirmed`.
- Si hay datos sensibles, anonimizalos.
- Si el texto es ambiguo, mantenlo ambiguo y explica que deberia preguntar el sistema.
- Si detectas una recomendacion sanitaria, marcala como riesgo `alto` o `critico` segun corresponda.
- Si detectas una accion irreversible, marcala como `requires_confirmation: true`.
- Conserva el lenguaje natural original lo mas posible.
- Puedes proponer variantes realistas, pero separalas en una seccion llamada `casos_sinteticos`, no las mezcles con casos reales.

## Salida final

Termina con:

```markdown
## Siguientes pasos recomendados

1. Casos que conviene agregar al dataset primero.
2. Intenciones nuevas candidatas.
3. Modulos/workflows emergentes.
4. Datos que el usuario deberia confirmar.
```
