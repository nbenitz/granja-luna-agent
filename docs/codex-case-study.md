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

## Evidencia del proceso

Una revisión local de las sesiones de Codex permitió reconstruir esta línea de trabajo sin
publicar conversaciones ni datos privados:

| Periodo | Necesidad y decisión humana | Trabajo asistido por Codex | Evidencia verificable |
| --- | --- | --- | --- |
| 14 de junio de 2026 | Definir un MVP fiel a la operación y confirmar el nombre Granja Luna | Leyó las instrucciones del repo antes de editar, revisó dominios y niveles de riesgo, preparó contratos y comprobó JSON y diffs | Commit [`5bc31c7`](https://github.com/nbenitz/granja-luna-agent/commit/5bc31c7) y [`AGENTS.md`](../AGENTS.md) |
| 14–20 de junio de 2026 | Mantener un core independiente de frameworks y aprender de casos reales revisados por una persona | Implementó y refactorizó el dry-run, creó un flujo de revisión de casos, agregó contexto conversacional y un inbox operativo; ejecutó pruebas unitarias, compilación y recorridos CLI temporales | Commits [`9c57643`](https://github.com/nbenitz/granja-luna-agent/commit/9c57643), [`6fb1b20`](https://github.com/nbenitz/granja-luna-agent/commit/6fb1b20), [`76d7973`](https://github.com/nbenitz/granja-luna-agent/commit/76d7973) y [`dc301f0`](https://github.com/nbenitz/granja-luna-agent/commit/dc301f0) |
| 9–17 de julio de 2026 | Recuperar Granja Luna como dominio activo y delegarle la interpretación avícola | Preservó la revisión móvil, separó el enrutamiento global de la interpretación de dominio, agregó el flujo de postura y validó ambos repositorios en contenedores | Commits [`c640e41`](https://github.com/nbenitz/granja-luna-agent/commit/c640e41) y [`ffce2d9`](https://github.com/nbenitz/granja-luna-agent/commit/ffce2d9) |
| 21–22 de julio de 2026 | Operar desde el teléfono sin convertir una intención en un hecho por error | Diseñó el puente MCP, el ciclo borrador–confirmación, trazas append-only y pruebas de extremo a extremo con servicios aislados; los cambios quedaron sujetos a revisión antes de publicarse | [`runtime/src/core/operations.py`](../runtime/src/core/operations.py), [`runtime/tests/test_operations.py`](../runtime/tests/test_operations.py) y el historial del PR |

Los identificadores y archivos de las sesiones se conservan localmente solo para auditoría. La
evidencia pública es el código resultante, sus commits, las pruebas y las decisiones documentadas;
no una transcripción seleccionada fuera de contexto.

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
