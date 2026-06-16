# Como emerge un modulo

Estado: `draft`

Este documento explica como una entrada real puede revelar un area, modulo, workflow o futuro subagente interno.

## Idea central

En Granja Luna no queremos definir todos los modulos antes de operar.

El sistema debe observar tareas reales y detectar cuando aparece una necesidad repetida o especializada.

```text
entrada real -> intencion detectada -> workflow candidato -> modulo candidato -> herramienta/API/subagente si se justifica
```

## Ejemplo: existencias y reposicion

Entrada real:

```text
Estoy en el deposito... tengo una bolsa de crecimiento al 70%,
maiz molido al 70%, iniciador a la mitad, ponedora...
hasta cuando me duran estas existencias?
que debo comprar minimamente?
```

El sistema detecta que no es solo una compra.

Tambien involucra:

- inventario observado;
- consumo o duracion estimada;
- reposicion minima;
- compra futura;
- reporte o recomendacion.

Por eso aparece una intencion nueva:

```text
analizar_existencias_reposicion
```

## Estados de madurez

| Estado | Significado | Ejemplo |
|---|---|---|
| `senal` | Aparece una necesidad en una entrada real. | "hasta cuando dura el maiz?" |
| `workflow_candidato` | Hay una secuencia clara de pasos. | inventario -> consumo -> duracion -> compra minima |
| `modulo_candidato` | El flujo toca datos y reglas propias. | existencias y reposicion |
| `herramienta` | El flujo necesita calculos confiables. | calcular_duracion_stock |
| `subagente_interno` | El area requiere memoria, reglas y herramientas propias. | agente de stock/reposicion |

## Criterio para crear modulo

Crear modulo cuando la necesidad:

- aparece en entradas reales mas de una vez;
- requiere datos propios;
- tiene calculos o reglas propias;
- afecta decisiones operativas;
- necesita reportes o UI especifica;
- puede beneficiarse de herramientas propias.

## Criterio para no crear modulo todavia

No crear modulo si:

- es solo una frase aislada;
- puede resolverse con el workflow existente;
- no hay datos suficientes;
- no sabemos si se repetira;
- separarlo agregaria complejidad sin valor inmediato.

## Aplicacion actual

`analizar_existencias_reposicion` queda como workflow candidato dentro del runtime.

No es todavia un subagente separado.

Para convertirse en modulo estable necesita:

- mas ejemplos reales;
- consumo diario aproximado por alimento;
- cantidad de aves o lotes;
- stock minimo deseado;
- reglas de compra minima;
- validacion humana de los calculos.

## Regla de seguridad

Las existencias detectadas desde conversacion deben quedar como `pending_review`.

No se deben convertir en stock real confirmado sin confirmacion explicita de Nestor.
