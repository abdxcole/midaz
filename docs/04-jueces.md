# Jueces del Open Agent Hackathon 2026 (investigación 2026-10-21)

> Hecho por ARGOS. Solo web, solo lectura. No se contactó a nadie. Lo que no está verificado está marcado **[NO VERIFICADO]** o **[INFERENCIA]**.

## 1. Lo que es oficial (página del evento)

Fuente: https://hackathon.genai.works/event/open-agent-hackathon-2026 (leída 2026-10-21)

- Fechas: build 22–27 oct 2026 (UTC). **Entrega cierra 27 oct 23:45 UTC = 27 oct 17:45 hora Costa Rica.** Resultados 6 nov 16:00 UTC (10:00 Costa Rica).
- Panel publicado ("Meet the judges"): 5 personas (lista abajo).
- **Cada entrega la revisan al menos 3 jueces.** El track que eliges define el panel. La página **no dice qué juez va a qué track**.
- Puntaje (100): **Impacto 30**, Técnico 20, Innovación 15, Demo 15, Producto y UX 10, Tecnología de sponsors 10. Empate: gana mayor Impacto, luego quien entregó antes.
- Track 02 "The Agent That Can Explain Why": agentes que investigan preguntas complejas en varias fuentes de datos, conectan hallazgos y dan respuestas o recomendaciones **respaldadas por evidencia**. Premio 1.600 / 1.200 / 900 USD.
- Premio aparte NVIDIA: DGX Spark (4.699 USD) a "mejor uso de Nemotron". Criterio sugerido en la guía: profundidad técnica, utilidad y pulido; mostrar lo que Nemotron **hace de verdad** dentro del producto.
- Obligatorio: Zetaris + Meterless integrados (al menos un Meterless Engine dentro de una función real, con test que pase o demo en vivo). Herramienta de código libre: Cursor es opcional y no da créditos (anuncio 2026-10-22). NVIDIA "donde aporte".
- Entregables: video de 1–4 min, slide deck, repo GitHub con README, y explicación de cómo se usó Zetaris, Meterless y NVIDIA y **qué fue único** en ese uso.

## 2. Jueces publicados

### Michael Hay — CTO, Zetaris
- Experiencia: 20+ años en datos, analítica, IA y almacenamiento. Antes CTO de Tecnologías Emergentes / Chief Technology Strategy Officer en Hitachi Vantara; VP de Producto en Teradata; VP y Chief Engineer en Hitachi Data Systems. Entró a Zetaris (anuncio 13 abr 2026).
- Enlaces:
  - LinkedIn: https://www.linkedin.com/in/mihay42 (handle visto en sus posts)
  - Nombramiento: https://www.zetaris.com/company/media-and-press/zetaris-appoints-michael-hay-chief-technology-officer
  - Post "compute de IA ociosa por falta de datos": https://www.linkedin.com/posts/mihay42_in-the-past-week-ive-continued-to-hear-the-activity-7500289574854856704-Y7Fc
  - Post sobre preparar el hackathon (repo getting-started, AWS/local): https://www.linkedin.com/posts/mihay42_the-zetaris-team-put-in-a-ton-of-work-to-activity-7514061052720914433-a7Kl
  - Artículo "Three Principles for Successful and Strategic AI Implementation" (AI Journal, jul 2025): https://aijourn.com/three-principles-for-successful-and-strategic-ai-implementation/
  - Charlas Hitachi Vantara (ciber-resiliencia, nube híbrida en banca, VeeamON25).
- Qué le importa (de sus propias palabras):
  - "Datos + contexto son obligatorios". Un modelo con solo contexto produce tokens que "ojalá sirvan, **y la esperanza no es estrategia**". → Odia respuestas sin datos reales detrás.
  - Federación inteligente: consultar datos donde viven, sin copiar ni ETL; **capa semántica** para reglas de negocio; acceso por SQL/JDBC, SQL/REST y MCP.
  - Evitar "IA por la IA". Metas de negocio claras, resultados medibles, retorno de la inversión.
  - Gobernanza: permisos, auditoría, protección de datos (viene de storage y ciber-resiliencia).
- Cómo puntuará probablemente **[INFERENCIA]**: Técnico y Sponsor tech mirando si Zetaris es el centro de verdad (no un adorno), si se usa federación de varias fuentes, la capa semántica (USL) y Lightning SQL. Impacto: problema de negocio concreto con número medible. Le restará a "chatbot que inventa".
- Ojo: el usuario dijo "un juez del Track 02 es el CTO de Zetaris". La página no asigna jueces a tracks; es lógico (Zetaris es protagonista de los tracks 01 y 02 en la guía) pero **[NO VERIFICADO]**.

### Michael Armentano — Head of Technical Partnerships, SpaceXAI (APJ, Singapur)
- Enlaces: LinkedIn https://linkedin.com/in/michaelarmentano ("Building Tech Partnerships at SpaceXAI"; "Data Intelligence & Agentic AI"). Antes: WW Principal GTM para Amazon Q y Agentic AI en AWS (APJ).
- LinkedIn Live con Vinay Samuel (CEO Zetaris), organizado por Steve Nouri (CEO GenAI Works): https://www.linkedin.com/posts/stevenouri_ai-can-build-an-application-in-minutes-so-activity-7514166547641274369-p4IN — temas: por qué los proyectos de IA empresarial no pasan de prototipo; qué es un "Data Harness"; agentes trabajando **seguros con datos vivos**; "coding harness + data harness".
- Contexto: SpaceXAI patrocina junto con Cursor (el hackathon menciona "SpaceXAI's Coding Harness" = Cursor/Grok). **[INFERENCIA]** es el juez más cercano a "Cursor/Grok".
- Qué le importa: salir del prototipo a algo que un negocio usaría; arquitectura empresarial, nube, alianzas; historia go-to-market.
- Cómo puntuará **[INFERENCIA]**: Impacto y Demo; si el producto tiene un usuario claro y camino a adopción; si se ve el flujo Cursor (coding harness) + Zetaris (data harness).

### Sam Cummings (Samuel J. Cummings III) — "Director of Education, GenAI Works" según la página
- Su LinkedIn dice que hoy es **VP of AI Engineering** en GenAI Works (desde oct 2025): https://linkedin.com/in/samuelj314
- Dice haber construido "motores agénticos de razonamiento, memoria, world modeling, enrutamiento de tareas, verificación de salidas y reducción de llamadas al modelo". Esos coinciden con los Meterless Engines (Markovian, H-MEM, World Model, Scout Intent). **[INFERENCIA fuerte, no confirmado oficialmente que sea autor de Meterless]**. Una búsqueda lo describe promoviendo los motores Meterless.
- Ex Head of Data Science en Gainsight; cofundó Dataplant (agente de customer success, adquirido 2026).
- Su frase clave: "Los agentes no suelen fallar porque el modelo sea débil. Fallan porque el sistema no entiende al usuario, el trabajo, el historial o las restricciones." → Le importa **el contexto y la memoria**.
- Cómo puntuará **[INFERENCIA]**: será el más exigente con Meterless: quiere un motor **integrado de verdad** con prueba (conformance suite pasando, evals), no un README. La guía lo dice explícito: "mencionar un motor o dejar una dependencia sin usar no cumple".

### Vladyslav Shestakov — Head of Engineering, GenAI Works
- LinkedIn: https://linkedin.com/in/shestakov-vladyslav. "Creador del sitio genai.works". Full-stack (React/Next.js, Node/Nest, Python/FastAPI, Cypress, A/B tests, PostHog). Kharkiv/Poltava, Ucrania.
- No se hallaron charlas ni posts públicos sobre criterios de jueceo.
- Cómo puntuará **[INFERENCIA]**: Técnico y UX: que el repo corra con el README, código limpio, tests, que la app no se caiga, interfaz clara.

### Remus Ranca — "Education Operations Lead, GenAI Works" según la página
- LinkedIn: https://linkedin.com/in/remus-ranca — hoy se presenta como **Director of Education** de GenAI.Works (Cluj-Napoca, Rumania); dirige GenAI Academy.
- Aparece en "Meet the judges" arriba, pero en la sección grande "Judges" solo salen 4 (Hay, Armentano, Cummings, Shestakov). Su rol exacto como juez **[NO VERIFICADO]**.
- Valores que declara: disciplina, claridad, resultados medibles, procesos repetibles.
- Cómo puntuará **[INFERENCIA]**: Demo y Producto/UX: que se entienda en el video sin explicación extra, que siga el formato pedido (video 1–4 min, deck con todas las secciones).

## 3. Sponsors sin juez publicado
- **NVIDIA**: no hay juez de NVIDIA en la página. Quién decide el premio DGX Spark **no es público**.
- **Meterless**: ningún juez listado bajo "Meterless"; posible vínculo vía Sam Cummings (ver arriba).
- **Cursor**: no hay juez de Cursor; Cursor llega vía SpaceXAI (Armentano).
- **Zetaris**: Michael Hay. El CEO Vinay Samuel aparece en eventos pero **no** como juez.

## 4. Quién prueba las demos
- Público: "cada entrega es revisada por al menos 3 jueces" y se juzga sobre video, deck, repo y explicación escrita. **No se publica que alguien ejecute el repo** ni que haya un equipo de testers. Hay una lista larga de **mentores** (no jueces) en la página (p. ej. Fabian Teres, Luca Berton, Victor Romanov, Dalibor Jovic, Saurabh Sagar…); que alguno haga pre-evaluación **[NO VERIFICADO]**.
- Conclusión práctica: el **video** es lo que seguro ven los 3 jueces. Debe probar todo por sí solo.

## 5. Recomendaciones para MIDAZ 

### Top 5
1. **Cada número con su recibo SQL de Zetaris visible.** En pantalla, al lado de cada afirmación ("el producto X vende mucho pero deja 4% de margen"), un botón "ver evidencia" que muestra la consulta Lightning SQL exacta, la fuente (tabla/vista Zetaris), filas devueltas y hora. Esto es literalmente el Track 02 y la frase de Hay "la esperanza no es estrategia".
2. **Federar 2–3 fuentes en Zetaris, no un CSV.** Ventas (POS), costos de producto e inventario, y gastos operativos (alquiler, planilla) en fuentes distintas, unidas en Zetaris (idealmente con una vista semántica "margen_neto_por_producto"). Así sumas Track 01/Data Harness y le hablas a Hay y a Armentano.
3. **Nemotron con trabajo real y visible, por Nightshift.** Mostrar el carril Nemotron en Nightshift (log/receipt del modelo) mientras el agente: (a) decide qué SQL correr (tool calling), (b) conecta hallazgos 80/20 con costos operativos, (c) un segundo carril Nemotron "verificador" que revisa que cada frase de la respuesta tenga evidencia y si no, la quita. Fijar el modelo, no dejar `meterless/auto` ambiguo. Esto apunta al DGX Spark.
4. **Un motor Meterless integrado y probado, en pantalla.** Lo más natural: **H-MEM** (recuerda el negocio: "la semana pasada dijiste que el pan dulce era tu estrella; hoy bajó su margen") y/o **Markovian** para el análisis largo en pasos. Mostrar la conformance suite pasando en el video y en el README. Sam Cummings lo va a buscar.
5. **Historia de impacto con un dueño real y un número.** Abrir con una persona concreta (ej. dueña de una panadería/pulpería) y cerrar con "encontró ₡X al mes que estaba perdiendo en productos que se venden mucho y no dejan" (con datos demo claramente marcados como demo). Impacto pesa 30 y desempata.

### Énfasis de la demo (video 3–4 min)
- 0:00–0:20 problema en palabras simples: "vendes mucho y no sabes qué te deja plata".
- 0:20–2:30 una pregunta en lenguaje natural → el agente investiga (se ven los pasos y las SQL) → respuesta con 3 hallazgos: 20% de productos que dan 80% de la ganancia; los más vendidos con margen bajo; margen vs costos operativos (punto de equilibrio). Cada uno con "ver evidencia".
- 2:30–3:15 "por qué": el agente explica su recomendación ("sube ₡100 el producto X o bájale costo, porque…") citando filas.
- 3:15–3:45 arquitectura en 1 diagrama: Cursor (build) → Zetaris (data) → Meterless Nightshift + Nemotron (power) + motor H-MEM/Markovian. Mostrar Nightshift Console/receipt con el modelo Nemotron (ocultar llaves).
- Cierre: número de impacto + qué sigue.

### Palabras que conviene usar (en inglés en el deck/video)
- "Every claim is backed by governed Zetaris SQL evidence" / "evidence-backed", "traceable", "no guessing".
- "Data harness + coding harness" (lenguaje de Zetaris y SpaceXAI).
- "Federated, no ETL, data stays where it lives", "semantic layer".
- "Nemotron decides and verifies; it doesn't just chat."
- "Context and memory" (para Sam).
- Evitar: "chatbot", "IA mágica", cifras sin fuente, "powered by X" sin mostrarlo.

### Qué tecnología mostrar (y cómo)
- Zetaris: SQL Editor/vista semántica + llamadas REST `/sql-editor/sqls/run` en el log del agente.
- Meterless: proveedor primario en la app, motor integrado con test pasando.
- Nemotron: carril fijo en Nightshift; mostrar el receipt.
- Herramienta de código: opcional (Cursor ya no es requisito, anuncio 2026-10-22).
- Repo: README que corra en pasos (Shestakov). Declarar código previo si lo hay (regla 5).

## 6. No verificado / huecos
- Qué jueces van al Track 02 (no publicado). Que Hay juzgue Track 02 es probable, no confirmado.
- Si NVIDIA, Meterless o Cursor tendrán jueces propios (no aparecen).
- Rol exacto de Remus Ranca como juez (aparece en una lista y no en otra).
- Que Sam Cummings sea autor de los motores Meterless (inferido de su LinkedIn).
- Si alguien ejecuta los repos o solo ven el video.
- Cargos en la página vs LinkedIn no coinciden (Cummings, Ranca): la página puede estar desactualizada.
- No se pudo abrir el post de Hay sobre el hackathon (timeout); su contenido viene de un resumen de búsqueda.
