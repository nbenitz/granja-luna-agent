# Vision ampliada: ERP agentico

Estado: `draft`

## Idea central

Granja Luna puede funcionar como el primer caso real para construir una plataforma de gestion empresarial agentica: un sistema tipo ERP, pero disenado desde el inicio para trabajar con lenguaje natural, agentes especializados, memoria operativa, datos estructurados, herramientas y confirmacion humana.

La vision no es agregar IA encima de un ERP tradicional. La vision es invertir el orden:

```text
ERP clasico:
modulos -> formularios -> datos -> reportes -> usuario se adapta

ERP agentico:
usuario conversa -> agente entiende -> sistema estructura -> modulos emergen -> datos y reportes se generan
```

## Rol de Granja Luna

Granja Luna es el caso piloto inicial.

Esto significa:

- la prioridad es resolver necesidades reales de la granja;
- los aprendizajes pueden alimentar una arquitectura reutilizable;
- el sistema no debe sobregeneralizar antes de validar flujos reales;
- las abstracciones genericas deben extraerse solo cuando existan patrones repetidos;
- el nombre `Granja Luna` puede mantenerse como identidad del caso piloto aunque la vision superior sea mas amplia.

## Plataforma futura

La plataforma generica, si se valida, podria servir para pequenos negocios y productores como:

- granjas avicolas;
- productores agropecuarios;
- comercios pequenos;
- talleres;
- despensas;
- ventas por redes;
- servicios independientes.

Cada negocio podria tener:

- memoria propia;
- agentes o dominios propios;
- reglas de negocio;
- herramientas;
- datos estructurados;
- flujos de confirmacion;
- reportes y tareas.

## Capas conceptuales

### 1. Interaccion natural

El usuario puede iniciar tareas con texto, voz, formularios simples o tarjetas de confirmacion.

Ejemplos:

- "Anotame esta compra."
- "Registra este tratamiento."
- "Necesito saber si falta alimento."
- "Genera una tarea para revisar el galpon."
- "Calcula cuanto me cuesta producir estos pollitos."

### 2. Orquestador de dominio

El orquestador interpreta la intencion, identifica dominios involucrados, evalua riesgo y decide si debe responder, pedir datos, preparar registros o activar agentes especializados.

### 3. Agentes especializados

Los agentes o dominios pueden empezar como archivos y workflows Markdown. Solo deben convertirse en agentes tecnicos separados cuando tengan memoria, herramientas, riesgos o procesos propios.

Dominios candidatos para Granja Luna:

- compras;
- stock;
- alimentacion;
- sanidad;
- ventas;
- incubacion;
- reproductores;
- infraestructura;
- mantenimiento;
- clima;
- finanzas;
- tareas;
- reportes.

### 4. Memoria Markdown

Markdown conserva conocimiento narrativo, procedimientos, decisiones, ideas, criterios de manejo, instrucciones y reglas en evolucion.

### 5. Base de datos

La base de datos debe guardar hechos estructurados cuando el flujo ya lo justifique:

- compras;
- ventas;
- movimientos de stock;
- tratamientos;
- tareas;
- incubaciones;
- pagos;
- productos;
- proveedores;
- clientes;
- lotes;
- costos.

### 6. Herramientas, API y MCP

Los agentes no deben limitarse a conversar. Con el tiempo deben poder usar herramientas controladas, por ejemplo:

- `preparar_compra_borrador`;
- `confirmar_compra`;
- `consultar_stock`;
- `crear_tarea`;
- `registrar_evento_sanitario_borrador`;
- `generar_reporte`;
- `consultar_ficha_medicamento`;
- `consultar_clima`.

Las acciones con impacto economico, sanitario, de stock o fisico requieren confirmacion humana.

### 7. Interfaz dinamica gobernada

La interfaz puede adaptarse a la tarea, pero no debe generar pantallas arbitrarias sin control. El agente debe pedir componentes estructurados como:

- formulario;
- tabla;
- tarjeta de confirmacion;
- alerta;
- reporte;
- calendario;
- resumen financiero;
- lista de tareas.

La aplicacion decide como se renderizan esos componentes usando un diseno consistente.

## Relacion con el asistente personal

El Asistente Personal no deberia absorber la logica interna de Granja Luna.

El modelo deseado es:

```text
Asistente Personal
  -> decide dominio, prioridad y riesgo
  -> envia solicitud estructurada
  -> Granja Luna / ERP agentico responde con propuesta
  -> Asistente Personal sintetiza y pide confirmacion si corresponde
```

Un futuro agente de ideas podria vivir en el Asistente Personal. Ese agente escucharia ideas, las resumiria y las compartiria como tarjetas con los agentes de dominio que correspondan.

## Criterio de extraccion

No crear un repo generico de ERP agentico hasta que Granja Luna haya validado al menos algunos flujos reales.

Candidatos minimos antes de extraer un core generico:

- un flujo de compras funcionando como borrador y confirmacion;
- un flujo de stock basado en movimientos;
- una bitacora operativa consultable;
- un sistema de tareas;
- reglas claras de riesgo y confirmacion;
- modelos de datos iniciales probados con casos reales;
- herramientas o APIs internas que demuestren repeticion.

## Riesgo principal

El riesgo principal es intentar construir una plataforma generica antes de resolver una operacion concreta.

La regla de trabajo debe ser:

```text
Granja Luna primero como producto usable.
ERP agentico despues como extraccion de patrones reales.
```
