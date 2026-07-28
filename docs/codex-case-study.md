# Caso de estudio: desarrollo asistido por OpenAI Codex

## Objetivo

Granja Luna Agent transforma mensajes cotidianos de una operación avícola en borradores estructurados que una persona puede revisar antes de convertirlos en hechos operativos. El reto no consiste solo en extraer datos: una interpretación incorrecta puede afectar inventario, dinero, sanidad o trazabilidad.

Codex se utiliza como colaborador técnico para acelerar el análisis del repositorio, proponer planes, generar implementaciones iniciales, ampliar pruebas y mantener documentación consistente. Néstor conserva la responsabilidad sobre las reglas de negocio, las decisiones arquitectónicas y la aceptación final de cada cambio.

## Contexto entregado al agente

El archivo [`AGENTS.md`](../AGENTS.md) define el contrato de trabajo para cualquier agente que participe en el repositorio. Antes de modificar código, el agente debe consultar:

1. El propósito y estado del proyecto.
2. La tarjeta del agente.
3. Los contratos afectados.
4. Los niveles de riesgo.
5. La documentación del dominio correspondiente.

Las restricciones más importantes son:

- no inventar datos operativos;
- separar borradores de hechos confirmados;
- solicitar confirmación explícita ante acciones sensibles;
- evitar secretos y datos privados;
- realizar cambios pequeños y revisar el diff antes de finalizar.

## Flujo de colaboración

```text
Necesidad operativa
       |
       v
Inspección de contexto y contratos
       |
       v
Plan propuesto por Codex
       |
       v
Implementación y pruebas iniciales
       |
       v
Revisión humana de reglas y riesgos
       |
       v
Correcciones, regresión y diff final
```

## Ejemplo técnico

La evolución más reciente agregó una capa operativa basada en eventos para:

- movimientos económicos y de inventario;
- estructura de galpones y planteles;
- almacenamiento físico de huevos;
- lotes y eventos de incubación;
- seguimiento de pollitos después de la eclosión;
- presentación consistente en web y móvil mediante contratos versionados.

Codex ayudó a inspeccionar las piezas existentes, detectar dependencias entre dominios, preparar código y pruebas, y mantener sincronizada la documentación. La revisión humana definió qué acciones requieren confirmación, cuáles relaciones representan la operación real y qué información no debe darse por confirmada.

La evidencia se puede recorrer desde:

- [`runtime/src/core/operations.py`](../runtime/src/core/operations.py), para movimientos append-only;
- [`runtime/src/core/incubation.py`](../runtime/src/core/incubation.py), para el ciclo de incubación;
- [`runtime/src/core/brooding.py`](../runtime/src/core/brooding.py), para cría posterior a la eclosión;
- [`runtime/src/web/app.py`](../runtime/src/web/app.py), para la API;
- [`runtime/tests/`](../runtime/tests/), para reglas y regresiones;
- [`runtime/contracts/`](../runtime/contracts/), para contratos legibles y versionados.

## Validación

Los cambios deben superar:

```bash
python3 -m unittest discover -s runtime/tests -p "test_*.py"
npm run typecheck --prefix mobile
npm run test:e2e
```

GitHub Actions ejecuta las pruebas de Python y el typecheck móvil en un entorno limpio. El PR asociado conserva el diff, la explicación técnica y los resultados de CI como evidencia pública del proceso.

## Criterio profesional

El uso de Codex no sustituye la comprensión del sistema. Las propuestas del agente se comparan con los contratos, se prueban y se corrigen antes de integrarse. Si una sugerencia contradice una regla operativa, introduce complejidad innecesaria o no puede validarse, se descarta o se reformula.

El resultado buscado es un ciclo de desarrollo más rápido sin renunciar a trazabilidad, pruebas ni responsabilidad humana.
