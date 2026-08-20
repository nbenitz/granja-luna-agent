# Fuentes permitidas para estudiar el mercado avícola de Granja Luna

**Fecha de corte:** 19 de agosto de 2026  
**Estado:** informe de investigación y propuesta; no registra demanda ni ventas como hechos confirmados  
**Ámbito:** Paraguay, departamento de Caaguazú y zona Coronel Oviedo  
**Objetivo:** medir interés, oferta, cultura de compra y eficacia de publicaciones sin depender de una
recolección automatizada no autorizada en grupos de Facebook.

## Resumen ejecutivo

Sí es posible construir un estudio grande, económico y repetible con fuentes permitidas. Lo que no
existe hoy es una vía gratuita, autorizada y comercial para descargar miles de publicaciones
orgánicas de grupos cerrados de Facebook.

La mejor solución no es sustituir Playwright por Chrome DevTools, Ollama o un GPT económico. El
permiso depende de la fuente y del método de acceso, no del modelo que maneje el navegador. Meta
exige autorización expresa y escrita para la recolección automatizada; además, su propia explicación
sobre scraping menciona que algunos recolectores imitan el comportamiento normal de una persona.
Por ello, introducir pausas aleatorias, desplazamiento irregular o sesiones cortas no vuelve
permitida esa extracción.

El estudio recomendado combina seis clases de evidencia:

1. **Tamaño y estructura local:** Censo 2022 del INE y Censo Agropecuario Nacional 2022 del MAG.
2. **Demanda de búsqueda:** Planificador de Palabras Clave de Google Ads, segmentado por Coronel
   Oviedo, Caaguazú y Paraguay.
3. **Contexto productivo:** SENACSA, FAOSTAT y UN Comtrade.
4. **Competencia pública:** Biblioteca de Anuncios de Meta y, con sus condiciones, APIs o servicios
   autorizados para páginas y web pública.
5. **Comportamiento propio:** estadísticas de Granja Luna, enlaces atribuibles, una página simple y
   WhatsApp Business.
6. **Experimentos de oferta:** comparar publicaciones compartidas y nativas, textos elaborados y
   naturales, formatos visuales y familias de productos.

Esta combinación no contará todas las publicaciones del país. A cambio, permitirá responder mejor la
pregunta comercial: **qué producto, presentación, ubicación, precio y formato producen consultas
calificadas, reservas y ventas**.

## 1. Criterio de permiso

La clasificación es operativa y se basa en las condiciones publicadas al momento del corte; no es
asesoramiento jurídico. Las condiciones deben volver a comprobarse antes de implementar una
integración.

| Nivel | Significado | Uso propuesto |
|---|---|---|
| Verde | licencia abierta explícita, API oficial o datos propios | automatizar descarga, transformación y análisis respetando atribución y condiciones |
| Amarillo | API oficial con elegibilidad, retención, cuota, pago o finalidad limitada; o sitio que requiere permiso escrito | piloto después de verificar condiciones y acceso |
| Rojo | términos que prohíben la recolección automática, ausencia de licencia reutilizable o fuente privada ajena | no automatizar ni convertir en base masiva |

Una página visible en Internet puede consultarse en el navegador y, aun así, no otorgar permiso para
copiar miles de registros, conservarlos y analizarlos comercialmente.

## 2. Qué sabemos ya del mercado local

### Base demográfica

El resultado final del Censo Nacional 2022 del INE informa para Coronel Oviedo:

- 98.323 habitantes;
- 67.307 en área urbana;
- 31.016 en área rural, aproximadamente 31,5% del distrito.

Para todo Caaguazú informa 431.519 habitantes y 241.013 residentes rurales, aproximadamente 55,9%.
El departamento combina, por tanto, una capital mayormente urbana con un entorno departamental de
fuerte ruralidad. Para decisiones actuales se debe preferir este censo final y la revisión distrital
2025 del INE, no proyecciones antiguas.

### Presencia avícola

La capa distrital oficial del CAN 2022 del MAG registra **817.538** cabezas en la variable combinada
`gallos, gallinas, pollos/as y pollitos` para Coronel Oviedo. Al consultar los 245 distritos con dato,
Coronel Oviedo queda octavo por esa variable.

Esto confirma una presencia avícola importante, pero **no equivale a 817.538 aves disponibles para
venta ni a demanda de compradores**. La cifra puede mezclar producción familiar e industrial y no
identifica edades, razas, compradores, transacciones ni precios.

### Uso de Internet y canales

La EPHC 2025 del INE informa que 85,4% de las personas de 10 años o más utilizó Internet; el valor fue
88,2% en áreas urbanas y 77,8% en rurales. Entre los usos informados aparecen mensajería instantánea
con 97,8%, redes sociales con 86,4% y comprar o vender productos o servicios con 29,5%.

La inferencia comercial razonable es usar redes sociales para descubrimiento y confianza, y
WhatsApp para la conversación y el cierre. Esas cifras no demuestran por sí solas preferencia por
Facebook ni interés en pollitos.

## 3. Matriz de fuentes permitidas y condicionadas

### 3.1 Datos oficiales y abiertos

| Fuente | Nivel | Escala | Qué permite medir | Limitación principal |
|---|---|---:|---|---|
| [Datos Abiertos Paraguay](https://www.paraguay.gov.py/datos-abiertos/licencias) | Verde | miles/millones de filas | datasets estatales reutilizables con atribución | cada conjunto debe comprobarse y documentarse |
| [CAN 2022 del MAG](https://www.datos.gov.py/dataset/censo-agropecuario-nacional-can-2022) | Verde | todos los distritos y rubros disponibles | establecimientos, producción y existencia animal | fotografía estructural de 2022; no demanda minorista |
| [Servicio geográfico distrital del MAG](https://server.gis.mag.gov.py/arcgis/rest/services/GEOPORTAL/Distritos_Py/FeatureServer/0) | Verde | 245 distritos con dato avícola | consultas JSON/GeoJSON, comparaciones y mapas | la variable avícola está agregada |
| [Resultados finales del Censo 2022](https://www.datos.gov.py/dataset/resultados-finales-del-censo-nacional-de-poblaci%C3%B3n-y-viviendas-2022) | Verde | población nacional a nivel distrital | tamaño, urbanidad, ruralidad y estructura de población | no mide compradores ni consumo |
| [Proyecciones distritales 2000–2035, revisión 2025](https://www.ine.gov.py/resumen/284/estimaciones-y-proyecciones-de-la-poblacion-distrital-2000-2035-revision-2025) | Verde | 263 distritos y serie anual | denominadores actuales y proyecciones | depende de supuestos demográficos |
| [TIC EPHC 2024 en datos.gov.py](https://www.datos.gov.py/dataset/tecnolog%C3%ADa-de-la-informaci%C3%B3n-y-comunicaci%C3%B3n-en-el-paraguay-tic-ephc-2024) y [EPHC 2025](https://www.ine.gov.py/ende/contenido.php?c=2930&title=El_acceso_a_internet_alcanza_a_m%C3%A1s_de_4%2C4_millones_de_personas_en_Paraguay) | Verde | microdatos/tablas nacionales según recurso | acceso digital, mensajería, redes y comercio en línea | no identifica una red o producto concreto |
| [Estadísticas abiertas de SENACSA](https://senacsa.gov.py/servicios/servicios-tecnicos/estadisticas/estadisticas-con-datos-abiertos/) | Verde | archivos por tema y periodo | población, movimiento, sanidad, comercio y sacrificio cuando exista el rubro | cobertura avícola/local a comprobar en cada archivo |
| [DNCP Datos Abiertos](https://contrataciones.gov.py/datos/api/v3/doc/) | Verde | hasta 10.000 resultados por consulta; CSV masivo | compras institucionales de pollitos, aves, alimentos o equipos | demanda pública, no hogares; requiere OAuth para API |
| [FAOSTAT](https://www.fao.org/faostat/en/) | Verde/condicionado a atribución | décadas y países | stock, producción, comercio y tendencias nacionales | escala país y rezago; no mercado local |
| [UN Comtrade API](https://unstats.un.org/unsd/api/) | Verde/condicionado a términos | comercio internacional | importación/exportación formal de aves vivas, por ejemplo HS 0105 | no refleja intercambios informales ni demanda distrital |

La licencia nacional permite copiar, extraer, reproducir, adaptar y distribuir los datos para usos
lícitos, con atribución, fecha de actualización cuando se conozca y sin insinuar aval oficial. Cada
archivo guardado deberá registrar fuente, fecha de descarga y licencia.

### 3.2 Señales de demanda y datos propios

| Fuente | Nivel | Escala | Valor para Granja Luna | Requisito o restricción |
|---|---|---:|---|---|
| [Google Ads: métricas históricas de palabras clave](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-historical-metrics) | Verde mediante producto oficial | decenas o cientos de términos por estudio | búsquedas mensuales, estacionalidad, competencia e intervalos de puja | cuenta de Google Ads; API requiere OAuth y token de desarrollador |
| [Google Ads: ideas de palabras clave](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas) | Verde mediante producto oficial | miles de ideas potenciales | descubre vocabulario real de búsqueda | los volúmenes pequeños pueden agruparse o ser imprecisos |
| [Google Trends API](https://developers.google.com/search/apis/trends) | Amarillo | cinco años y regiones admitidas | tendencia relativa y estacionalidad | API en acceso alfa limitado; no depender de ella al inicio |
| [Google Business Profile Performance API](https://developers.google.com/my-business/reference/performance/rest) | Verde para perfil propio | crecimiento continuo | consultas que muestran la ficha, llamadas, clics y solicitudes de dirección | perfil verificado y acceso aprobado |
| [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/basics) | Verde para propiedad propia | todas las visitas propias | campañas, ubicación aproximada, visitas y conversiones | requiere página propia e instrumentación |
| [Search Console API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) | Verde para propiedad propia | consultas de búsqueda del sitio | impresiones, clics, CTR y posición | solo sitio verificado; devuelve filas principales, no todo el universo |
| [Estadísticas de página de Facebook](https://www.facebook.com/help/268680253165747) y [exportación](https://www.facebook.com/help/www/972879969525875) | Verde para activos propios | todos los contenidos de Granja Luna disponibles en Meta | alcance, respuesta, audiencia y evolución | Meta limita periodos y dimensiones; no atribuye grupos ajenos |
| [Estadísticas de video de Facebook](https://www.facebook.com/help/1443647412620316/) | Verde para activos propios | todos los videos propios | reproducciones, retención disponible, reacciones, comentarios y compartidos | métricas definidas por Meta y sujetas a cambios |
| [Meta Marketing API: Ads Insights](https://www.postman.com/meta/facebook-marketing-api/request/u07tack/get-ad-insights-l1) | Verde para publicidad autorizada | campañas y anuncios propios | impresiones, alcance, clics, gasto y acciones | permisos, cuenta publicitaria y, si se pauta, presupuesto |
| [WhatsApp Business Platform: webhooks](https://www.postman.com/meta/whatsapp-business-platform/folder/tduohwq/webhook-payload-reference) | Verde para número empresarial propio | todas las conversaciones consentidas que entren por la plataforma | consultas, respuesta, calificación y estado del contacto | configuración oficial, privacidad y consentimiento; no leer chats ajenos |

La descarga oficial de objetivos geográficos de Google identifica actualmente:

- Coronel Oviedo, ciudad: `9250036`;
- Caaguazú, departamento: `9069964`;
- Paraguay, país: `2600`.

Eso permite comparar una misma familia de búsquedas a tres niveles geográficos. Si el volumen de la
ciudad es demasiado pequeño, la ausencia de dato no se debe interpretar automáticamente como cero
interés: Google puede redondear, agrupar u omitir búsquedas de baja frecuencia.

### 3.3 Redes y contenido público de terceros

| Fuente | Nivel | Utilidad | Condición decisiva |
|---|---|---|---|
| [Biblioteca de Anuncios de Meta](https://www.facebook.com/help/259468828226154/) | Verde para consulta pública; automatización a verificar | creatividades, promesas, duración y anunciantes con anuncios activos | no muestra ventas ni desempeño de anuncios comerciales ajenos; no reemplaza grupos |
| [Meta Content Library](https://about.fb.com/news/2023/11/new-tools-to-support-independent-research/) | Amarillo, normalmente no elegible | publicaciones públicas y métricas de páginas, grupos, eventos y posts | dirigida a investigación académica/no lucrativa de interés público; Granja Luna comercial probablemente no califica |
| [Group Insights](https://www.facebook.com/help/312362745877176) | Amarillo por rol | crecimiento, actividad, mejores posts, días, horas, ciudades y países | solo administradores de grupos; varias métricas exigen al menos 250 miembros |
| [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) | Amarillo | lenguaje, temas, formatos y métricas públicas de videos | cuota y políticas; muchos datos no autorizados deben borrarse o actualizarse a los 30 días |
| [Bluesky API pública](https://docs.bsky.app/docs/advanced-guides/api-directory) | Verde | texto público y tendencias experimentales | relevancia muy baja para el comprador rural paraguayo esperado |
| TikTok Research API | Amarillo/no elegible hoy | gran escala si se aprobara | excluye investigación comercial; elegibilidad académica/no lucrativa limitada |
| TikTok Commercial Content API | Amarillo/no útil hoy | anuncios comerciales | fase documentada limitada a anuncios de la Unión Europea, no Paraguay |
| Sprout Social, Brandwatch o Talkwalker | Amarillo/comercial | páginas públicas, web y comparación competitiva según proveedor | pago y cobertura exacta por validar; no resuelven grupos cerrados de Facebook |

YouTube puede aportar una muestra grande de lenguaje y formatos, pero no una muestra representativa de
ofertas ni compradores en Coronel Oviedo. Su política limita la conservación de ciertos datos
públicos no autorizados a 30 días, salvo excepciones aprobadas. Si se usa, la base debe refrescar o
eliminar esas columnas según el plazo.

### 3.4 Clasificados y directorios

| Fuente | Nivel | Uso permitido o razonable | Qué no hacer |
|---|---|---|---|
| [Consignatario](https://www.consignatario.com.py/) | Verde para publicar y consultar; Amarillo para cosecha masiva | probar un anuncio propio de aves y solicitar permiso para un estudio agregado | no extraer automáticamente todo el sitio sin autorización escrita |
| [Clasipar](https://clasipar.paraguay.com/reglas-de-uso) | Rojo para base automatizada | observación puntual o publicación conforme a sus reglas | sus condiciones no conceden explotación/reproducción masiva de contenido |
| Hendyla | Rojo hasta aclarar | evaluar como canal si permite el rubro | no automatizar sin API, licencia o permiso expreso |
| [Google Places Text Search](https://developers.google.com/maps/documentation/places/web-service/text-search) | Amarillo | localizar agropecuarias, veterinarias y comercios en consultas en vivo | no formar un archivo permanente con contenido restringido; los `place_id` sí tienen trato especial |

Al momento de revisar Consignatario se observaron 17 anuncios activos totales, dos vendedores y cero
anuncios avícolas. Esto puede significar poca adopción del portal, no ausencia de mercado. Su mejor
uso inmediato sería publicar un anuncio propio y medir consultas, no usarlo como estimador nacional.

## 4. Lo que no podemos automatizar sin permiso

### Grupos cerrados de Facebook

Los [Términos de Meta](https://www.facebook.com/terms) prohíben acceder o recolectar datos de sus
productos por medios automatizados sin permiso previo. Los
[Términos de recolección automatizada](https://www.facebook.com/legal/automated_data_collection_terms)
exigen autorización expresa y escrita; aceptar los términos no constituye esa autorización.

Por tanto, ninguna de estas variantes cambia el estado de permiso:

- Chrome DevTools MCP o protocolo CDP;
- Playwright, Puppeteer, Selenium o scripts del navegador;
- un modelo local de Ollama, un GPT económico o un agente de Codex;
- pausas aleatorias, horarios irregulares o desplazamiento que imite a una persona;
- usar una cuenta que sea miembro legítimo del grupo.

La automatización puede parecer menos repetitiva, pero sigue siendo recolección automatizada. No se
debe diseñar para ocultarse o eludir detección.

### Qué sí se puede obtener de los grupos

1. **Datos propios de Granja Luna:** métricas visibles de sus publicaciones, consultas recibidas y
   resultados confirmados.
2. **Exportes agregados de administradores:** si un administrador coopera, puede compartir Group
   Insights permitidos para su rol. Esto no autoriza a raspar el contenido de todos los miembros.
3. **Estudio puntual necesario para operar:** revisar manualmente reglas, moderación y respuesta de
   una publicación propia, sin convertir el grupo en una base masiva.
4. **Permiso formal:** pedir a Meta o al titular de una fuente una vía documentada. El permiso del
   administrador del grupo, por sí solo, no sustituye las condiciones de Meta para automatización.

## 5. Diseño del estudio de mercado permitido

### Preguntas a responder

1. ¿Qué volumen de interés de búsqueda existe para cada producto en ciudad, departamento y país?
2. ¿Qué productos generan consultas calificadas, reservas y ventas para Granja Luna?
3. ¿Qué combinación de texto, material visual y distribución convierte mejor?
4. ¿Qué edades, cantidades, precios, localidades y modalidades de entrega producen o impiden el
   contacto?
5. ¿Qué proporción del interés corresponde a caseros, razas, postura, reproducción o conjuntos?

### Familias iniciales de producto

La lista se expande con las ideas que devuelva Google, sin inventar nombres o sinónimos:

- pollitos caseros y criollos;
- pollitos por edad y por lote;
- gallinas caseras y ponedoras;
- Plymouth Rock barrado;
- Rhode Island Red;
- Black Star;
- Brahma;
- gallos adultos y reproductores;
- casal, pareja, trío y plantel;
- huevos fértiles.

Conviene registrar variantes ortográficas reales, pero mantener una columna normalizada para no
contarlas como productos distintos.

### Fase 1 — Línea base oficial y búsqueda, 2 a 3 días

1. Descargar CAN 2022, Censo 2022, proyecciones 2025 y recursos útiles de SENACSA.
2. Crear una tabla por distrito con población, ruralidad y existencia avícola disponible.
3. Preparar entre 40 y 80 términos de búsqueda y obtener métricas para ciudad, departamento y país.
4. Clasificar los términos por producto, edad, cantidad, intención y ubicación.
5. Registrar la fecha y las condiciones de cada fuente.

El resultado será un mapa estructural y de búsqueda. Todavía no será una estimación de unidades que
Granja Luna puede vender.

### Fase 2 — Medición propia y experimento, 4 semanas

Crear una página simple de disponibilidad o, como mínimo, enlaces de WhatsApp diferentes y naturales
por campaña. El texto prellenado puede decir “Hola, vi los pollitos en [grupo]. ¿Qué edades quedan?”,
sin exigir una palabra clave artificial.

Separar dos experimentos:

#### Experimento de distribución

- A: reel publicado por Granja Luna y compartido por Limpia;
- B: el mismo material subido nativamente por Limpia;
- conservar, en lo posible, producto, texto, precio, día y franja horaria.

#### Experimento de redacción

- A: texto informativo de marca más elaborado;
- B: texto breve, personal y sencillo;
- utilizar el mismo material nativo, precio, inventario y grupo comparable.

No conviene enfrentar simultáneamente `compartido + elaborado` contra `nativo + natural` si el
objetivo es identificar la causa. Esa comparación puede servir para vender, pero no dirá qué variable
produjo la diferencia.

Usar un diseño cruzado por grupos y semanas: cada variante debe pasar por grupos comparables en
momentos distintos. No publicar duplicados cercanos en el mismo grupo ni superar sus reglas de
frecuencia.

### Fase 3 — Ampliación de canales

- verificar y medir la ficha de Google Business Profile;
- probar un anuncio propio en un clasificado que acepte el rubro;
- publicar contenido educativo en Instagram, YouTube o TikTok y medirlo desde cuentas propias;
- solicitar a Consignatario permiso escrito si se desea analizar anuncios agregados;
- explorar colaboración con administradores de grupos para recibir estadísticas agregadas;
- considerar publicidad pagada pequeña solo después de instrumentar consultas y ventas.

## 6. Métricas que importan

Las reacciones sirven como señal de atención, pero no deben ser el resultado principal.

| Nivel | Métrica | Prioridad |
|---|---|---:|
| Exposición | alcance, impresiones, reproducciones y retención cuando estén disponibles | secundaria |
| Atención | reacciones, comentarios y compartidos | secundaria |
| Intención | clic a WhatsApp, mensaje privado y pregunta concreta | alta |
| Calidad | producto, cantidad y localidad definidos | muy alta |
| Operación | tiempo de respuesta, posibilidad de entrega y stock compatible | alta |
| Negocio | reserva, unidades reservadas, venta, ingreso y motivo de pérdida | principal |
| Riesgo | rechazo, moderación, eliminación o advertencia | principal para continuidad del canal |

Indicador preferido si existe alcance:

`consultas calificadas / 100 personas alcanzadas`

Si no existe alcance, usar:

`consultas calificadas / publicación` y `ventas confirmadas / consulta calificada`

Comparar también mediana y distribución, no solo promedio: una publicación extraordinaria puede
distorsionar una muestra pequeña.

## 7. Tamaño de muestra realista

Se pueden obtener miles o millones de filas permitidas de censos, compras públicas, comercio y
búsqueda. Sin embargo, esas filas no son miles de ofertas comparables de pollitos.

Para los experimentos propios:

- 8 a 12 publicaciones comparables por variante dan una primera señal direccional;
- 20 o más por variante, repartidas entre al menos cuatro grupos y varias semanas, son más estables;
- el número exacto debe depender de cuántas consultas se produzcan, no de alcanzar una cifra estética;
- no se debe aumentar la muestra repitiendo o saturando grupos.

Para estimar demanda real, cien consultas bien atribuidas valen más que diez mil publicaciones
ajenas con reacciones, porque las consultas permiten medir producto, cantidad, zona, objeción y
conversión.

## 8. Arquitectura económica

No hace falta LangGraph para la primera versión. Un proceso simple en Python, tareas programadas y
SQLite es más barato, fácil de auditar y suficiente mientras cada fuente tenga un flujo estable.

```text
APIs/CSV/exportes propios
          |
          v
 archivos crudos con fuente, fecha, licencia y retención
          |
          v
 normalización y reglas locales -> SQLite
          |
          +--> métricas y tablero
          |
          +--> solo casos ambiguos -> modelo local o API económica
```

### Tablas mínimas

- `sources`: fuente, URL, nivel de permiso, licencia, fecha y política de retención;
- `market_observations`: geografía, periodo, indicador, unidad y fuente;
- `keywords`: término, familia, ubicación, mes, búsquedas y competencia;
- `campaign_posts`: canal, grupo, variante, producto, material, horario y métricas;
- `leads`: origen, producto, cantidad, localidad, etapa y motivo de pérdida;
- `sales`: solo después de confirmación humana, con referencia al contacto y campaña.

### Reparto del trabajo

Las tareas deterministas no necesitan IA:

- descargar APIs y CSV;
- eliminar duplicados;
- extraer precios, edades, cantidades y localidades con reglas;
- calcular longitud, presencia de emojis y campos informativos;
- producir tablas, medianas y gráficos.

Ollama o un modelo económico puede clasificar únicamente textos ambiguos como `personal`,
`comercial`, `educativo` o `grandilocuente`, con salida estructurada y nivel de confianza. El modelo
potente debe revisar el esquema, las excepciones y la interpretación final, no leer cada fila.

LangGraph empieza a ser útil si aparecen muchos pasos con reintentos, varias APIs, aprobaciones
humanas y estados largos. Usarlo desde el principio añadiría mantenimiento sin resolver el problema
de permiso de Facebook.

### Datos que no se deben guardar

- nombres, teléfonos o perfiles de terceros sin necesidad operativa;
- conversaciones privadas ajenas;
- imágenes personales de vendedores o miembros;
- texto masivo de una fuente cuya licencia no permita conservarlo;
- credenciales, cookies o tokens en informes o repositorio.

## 9. Sesgos que deben quedar visibles

- **Google Search:** mide búsquedas, no conversaciones que nacen directamente en Facebook o WhatsApp.
- **Datos censales:** describen estructura y oferta potencial, no intención actual.
- **Reacciones:** mezclan interés social, entretenimiento, etiquetas y posibles compradores.
- **Clasificados:** representan a quienes usan esa plataforma, no a todo Paraguay.
- **Datos propios:** son la evidencia comercial más fuerte, pero dependen del alcance y reputación de
  Granja Luna.
- **Grupos:** el algoritmo, la moderación, el tamaño y la antigüedad afectan visibilidad; los grupos
  observados no son una muestra aleatoria del país.
- **Localidad declarada:** que alguien pertenezca a un grupo nacional no demuestra dónde vive o dónde
  comprará.

## 10. Prioridad, esfuerzo y costo esperado

| Fuente o acción | Cercanía a demanda real | Esfuerzo inicial | Costo monetario/tokens | Prioridad |
|---|---:|---:|---:|---:|
| Consultas, reservas y ventas propias bien atribuidas | muy alta | bajo/medio | muy bajo | 1 |
| Google Ads Keyword Planner por las tres geografías | alta como intención de búsqueda | medio | bajo; no requiere clasificar con IA | 2 |
| Experimentos propios en Facebook y WhatsApp | muy alta para Granja Luna | medio | bajo, salvo pauta opcional | 3 |
| MAG + INE | media como contexto de mercado | bajo | cero y sin tokens después de importar | 4 |
| Google Business Profile y página propia | alta cuando acumulen tráfico | medio | bajo | 5 |
| SENACSA + FAOSTAT + Comtrade + DNCP | baja/media, según pregunta | bajo/medio | bajo | 6 |
| YouTube API | media para lenguaje, baja para compra local | medio | cuota gratuita limitada y retención operativa | 7 |
| Servicios comerciales de escucha social | variable | bajo/medio | alto | 8 |
| Extracción automatizada de grupos cerrados | potencialmente alta, pero no autorizada | alto | riesgo de cuenta y cumplimiento | descartada |

La opción de menor costo no es el modelo más barato navegando Facebook. Es **no enviar al modelo los
datos que una API, una regla o SQL pueden procesar**. Los tokens se reservan para clasificar la
minoría ambigua y redactar la interpretación final.

## 11. Hipótesis culturales para validar, no conclusiones

Fuentes históricas sobre avicultura familiar paraguaya describen una larga tradición de gallinas de
traspatio para carne, huevos e ingreso de emergencia, especialmente en áreas rurales. Estudios
locales antiguos también señalan sabor, frescura, confianza o parentesco con el vendedor e
información sobre alimentación y manejo como criterios posibles.

Estas referencias son útiles para formular hipótesis, pero son antiguas o geográficamente limitadas.
El experimento actual debe comprobar si siguen vigentes. Las hipótesis iniciales son:

- una publicación personal, concreta y con material real puede generar más acercamiento que una
  pieza institucional compartida;
- precio, edad, ubicación y entrega reducen fricción;
- mostrar aves reales y el plantel de origen puede aumentar confianza en razas y reproductores;
- WhatsApp puede convertir mejor que Messenger cuando el contacto es claro y responde rápido;
- escribir sencillo puede ayudar; escribir mal deliberadamente no debería ser una estrategia.

## 12. Decisión recomendada

Adoptar una **estrategia híbrida y permitida**:

1. Ejecutar inmediatamente la línea base con MAG, INE y palabras clave de Google.
2. Instrumentar las publicaciones y WhatsApp antes de lanzar más variantes.
3. Probar la publicación directa y sencilla de Limpia, pero mediante un diseño cruzado que separe
   contenido nativo, estilo de redacción y formato visual.
4. Mantener Facebook Groups como canal de distribución y observación de nuestras piezas, no como
   fuente automatizada masiva.
5. Escalar con datos propios, búsquedas y fuentes abiertas; solicitar permisos específicos donde
   una fuente comercial aporte valor.
6. Evaluar el mercado por consultas, reservas y ventas, no por la cantidad de datos recolectados.

## 13. Próximos entregables posibles

- un inventario versionado de fuentes, licencias y fechas de actualización;
- el esquema SQLite y los importadores de MAG/INE;
- una lista normalizada de palabras clave y su exportación por tres geografías;
- enlaces de WhatsApp atribuibles por campaña, sin palabras clave artificiales;
- una ficha de registro de consultas y motivos de pérdida;
- el calendario del ensayo A/B cruzado y sus reglas de parada;
- un tablero semanal de consultas calificadas, reservas y ventas.

## Fuentes complementarias

- [MAG — volumen III del CAN 2022](https://www.mag.gov.py/Censo/Book%20Vol3.pdf)
- [INE — estructura de la población por edad y sexo, Censo 2022](https://www.ine.gov.py/censo2022/documentos/Censo%202022%20-%20Estructura%20de%20la%20poblacion%20por%20edad%20y%20sexo.pdf)
- [INE — presentación TIC EPHC 2025](https://www.ine.gov.py/Publicaciones/Biblioteca/documento/319/Presentaci%C3%B3n%20TICs%20EPHC_2025_INE.pdf)
- [Open Contracting — Paraguay](https://data.open-contracting.org/es/publication/63)
- [FAO — nueva API de FAOSTAT](https://www.fao.org/statistics/highlights-archive/highlights-detail/faostat-launches-a-new-api-developer-portal-to-make-data-access-easier/en)
- [Google Ads — objetivos geográficos](https://developers.google.com/ad-manager/api/geotargets)
- [Google Ads — acceso y primera llamada](https://developers.google.com/google-ads/api/docs/get-started/make-first-call)
- [Google Business Profile — métricas](https://developers.google.com/my-business/reference/performance/rest)
- [Meta — explicación de scraping](https://www.facebook.com/help/463983701520800)
- [Facebook — estadísticas de grupos](https://www.facebook.com/help/312362745877176)
- [YouTube — costo de cuota](https://developers.google.com/youtube/v3/determine_quota_cost)
- [YouTube — políticas para desarrolladores](https://developers.google.com/youtube/terms/developer-policies)
- [YouTube — métricas derivadas](https://developers.google.com/youtube/terms/derived-metrics-policy)
- [Bluesky — límites de uso](https://docs.bsky.app/docs/advanced-guides/rate-limits)
- [Consignatario — términos](https://www.consignatario.com.py/terminos)
- [Google Places — políticas](https://developers.google.com/maps/documentation/places/web-service/policies)
