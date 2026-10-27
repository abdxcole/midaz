# CRONOS · Jueces vistos por LinkedIn (2026-10-21)

> Complementa `17-JUECES-HACKATHON-2026-10-21.md` (no repite su contenido: rol, puntaje, tracks). Aquí: **qué publican, qué les molesta y cómo MIDAZ los convence**. Solo web pública, sin iniciar sesión. **[NO VERIFICADO]** = no confirmado; **[INFERENCIA]** = deducción nuestra.

## Michael Hay — CTO, Zetaris
**Lo nuevo encontrado**
- Serie "ZETARIS Data Harness for AI (ep.2) — Unified Semantic Layer" (16 jul 2026): pregunta "¿Qué descuento reciben los clientes leales?". La IA no responde "porque nadie le dijo qué significa *leal*". Dice que el LLM "ve tablas, columnas, nulls; no ve tu negocio". Los agentes de Zetaris crean entidades, **términos de negocio rastreados a la columna exacta**, **KPIs derivados con fórmula real (net profit margin)** y **105 reglas de calidad de datos** ejecutables; luego el agente "carga el contexto, **cada línea citada a su fuente**, escribe el SQL correcto y lo corre en sitio. Sin mover datos". https://www.linkedin.com/feed/update/urn:li:activity:7483418586783326223 (autoría directa de Hay sobre ese post **[NO VERIFICADO]**: el resultado no muestra el autor).
- Post 2024 sobre alucinación: la llama "error de interpolación", producto del decodificado estocástico; los LLM "no razonan", solo recombinan. https://www.linkedin.com/posts/mihay42_worth-five-minutes-activity-7242690886566846464-OtoR
- Post "compute ociosa": "datos + contexto son obligatorios… **hope is not a strategy**"; federación, capa semántica, acceso SQL/JDBC, SQL/REST y MCP. https://www.linkedin.com/posts/mihay42_in-the-past-week-ive-continued-to-hear-the-activity-7500289574854856704-Y7Fc
- Web de Zetaris: "tu agente alucina porque el dato estaba en un sistema que no alcanzaba. **No es un problema del modelo, es de acceso a datos**". https://www.zetaris.com/cloud

**Le molesta [INFERENCIA de sus posts]:** respuestas sin dato real detrás; tratar la alucinación como "detalle"; definiciones de negocio ambiguas; copiar datos (ETL) sin necesidad; Zetaris de adorno.

**Cómo ganarlo**
- Producto: definir en la capa semántica (USL) de Zetaris **"margen", "costo operativo", "producto estrella"** con fórmula y columna origen; el recibo muestra la definición usada, no solo el SQL.
- Producto: 3–5 reglas de calidad de datos (costo nulo, precio < costo, ventas negativas) y que MIDAZ diga "no sé: 3 productos no tienen costo cargado".
- Demo: mostrar la consulta corriendo **en sitio** en Zetaris (sin copiar a otra base).
- Pitch: usar su lenguaje: "MIDAZ doesn't hope. Every number is governed Zetaris SQL." / "Data + context, never context alone."

## Michael Armentano — Head of Technical Partnerships, SpaceXAI APJ (Singapur)
**Lo nuevo encontrado**
- LinkedIn Live con Vinay Samuel (Zetaris), anunciado por Steve Nouri (14 oct 2026): "La IA construye una app en minutos; ¿por qué tarda meses en funcionar dentro de una empresa? **Generar código era solo la mitad del problema**"; data harness; agentes **seguros con datos vivos**. https://www.linkedin.com/posts/stevenouri_ai-can-build-an-application-in-minutes-so-activity-7514166547641274369-p4IN
- Comunicado Zetaris + SpaceXAI: "Zetaris es el data harness para el coding harness (Grok Build)". https://www.linkedin.com/posts/vinaysamuel_zetaris-launches-cloud-ai-data-harness-for-activity-7513255293137379330-nGuX ; nota de prensa (20 oct 2026), con cita de SpaceXAI: "coding harness + acceso instantáneo a datos gobernados". https://securitybrief.news/story/zetaris-launches-ai-data-harness-with-spacexai-tie-up
- Perfil: "Senior GTM Executive | Data Intelligence & Agentic AI". https://linkedin.com/in/michaelarmentano
- No encontré posts propios de él con opiniones sobre demos **[NO VERIFICADO]**.

**Le molesta [INFERENCIA]:** prototipos que no salen del laboratorio; demos sin usuario ni camino a adopción.

**Cómo ganarlo**
- Pitch: una diapositiva "Coding harness (Cursor/Grok Build) + Data harness (Zetaris) = MIDAZ en 6 días".
- Producto/pitch: camino real de adopción: cargar export del POS (CSV/Excel) → Zetaris → respuestas; costo por pregunta (Meterless).
- Demo: datos "vivos": cambiar un costo en la fuente y que la respuesta cambie al instante.

## Sam Cummings (Samuel J. Cummings III) — VP of AI Engineering, GenAI Works
**Lo nuevo encontrado**
- Post "RAG, CAG o H-MEM?" (24 jun 2026): RAG = "leer de un CD", CAG = "VRAM", H-MEM = "cerebro con memoria a largo plazo"; "**9 de cada 10 veces quieres H-MEM**"; "si usas RAG, puede ser por qué no rinde en producción". https://www.linkedin.com/posts/samuelj314_rag-cag-or-h-mem-as-someone-who-has-been-activity-7475670929335926784-6AFf
- Post de aprendizajes tras entrevistar 90+ ejecutivos: memoria "se parece al diseño de bases de datos de los 90: working, episodic, semantic; promoción, **detección de contradicciones**"; "la mayoría de 'memoria IA' es **un vector store y una plegaria**". https://www.linkedin.com/posts/samuelj314_agenticai-localfirst-aiinfrastructure-activity-7477837277327421442-CLOS
- Su perfil dice que construyó motores de razonamiento, memoria, world model, **verificación de salidas** y reducción de llamadas, y "lideró hackathons con nuestros motores". https://linkedin.com/in/samuelj314 . El README de Meterless: cada motor tiene suite de conformidad; "tu agente termina cuando pasa la conformance suite". https://github.com/Meterless/Meterless . Que él sea autor directo de Meterless sigue **[NO VERIFICADO]** (muy probable).
- H-MEM exige `source` y `provenance` en cada recuerdo (un registro sin fuente se rechaza). https://github.com/Meterless/Meterless/tree/main/engines/hmem

**Le molesta [INFERENCIA de sus posts]:** "vector store y una plegaria"; RAG presentado como memoria; motores mencionados pero no integrados; agentes sin contexto del usuario.

**Cómo ganarlo**
- Producto: H-MEM guardando hechos del negocio **con provenance = id del recibo Zetaris**; así el recibo y la memoria son la misma idea. Mostrar detección de contradicción: "en marzo dijiste que el pan era tu estrella; hoy el margen dice lo contrario (recibo #12)".
- Demo: 5 segundos de `conformance` en verde.
- Pitch: "No RAG. Memory with provenance." El verificador Nemotron = "output checking", tema que él menciona.

## Vladyslav Shestakov — Head of Engineering, GenAI Works
**Lo nuevo encontrado**
- Único post relevante: lanzamiento de GenAI Academy (7 abr 2026): "mucho de lo que construimos se moldeó por cómo usamos IA en el desarrollo, como parte del flujo de trabajo". https://www.linkedin.com/posts/shestakov-vladyslav_we-just-launched-genai-academy-from-an-activity-7447296165626331136-tzBi
- Perfil: full-stack, Cypress (tests), A/B tests, PostHog (analítica). https://linkedin.com/in/shestakov-vladyslav . El encabezado público aún dice "IT Teacher en IT STEP Academy" (perfil mixto).
- No hay posts sobre jueceo **[NO VERIFICADO]**.

**Cómo ganarlo [INFERENCIA]**
- Repo que corre con 1 comando (`docker compose up` o `npm run demo`) y datos demo incluidos; tests visibles (un test que falle si una frase sale sin recibo).
- Mostrar cómo Cursor fue parte del flujo (reglas, AGENTS.md), no solo "lo usamos".
- UI limpia, rápida, sin pantallas rotas en el video.

## Remus Ranca — Director of Education, GenAI Works
**Lo nuevo encontrado**
- Encabezado: "Diseñando motores de cursos repetibles que convierten experiencia en IA en resultados reales". Valores: disciplina, claridad, crecimiento, ritmo, servicio; KPIs y QA. https://linkedin.com/in/remus-ranca
- Instructor del curso "Claude Practitioner's Guide to AI Agents": construir un agente y luego "**hacerlo confiable con datos reales y desordenados** — la parte que la mayoría de tutoriales se salta". https://academy.genai.works/courses/claude-practitioner-s-guide-to-ai-agents/details
- Otro perfil suyo menciona "vender hackathons de IA". https://www.collective.work/profile/remus-ranca

**Le molesta [INFERENCIA]:** demos confusas, sin resultado medible; datos de juguete perfectos.

**Cómo ganarlo**
- Datos demo **desordenados a propósito** (costos faltantes, nombres duplicados) y MIDAZ los maneja o dice "no sé".
- Video con estructura clara: problema → pregunta → respuesta con recibo → resultado en ₡ → qué sigue. Cumplir formato exacto (1–4 min, deck completo).
- Un resultado medible: "₡X/mes recuperables".

## Patrones comunes del panel
1. Alucinación = problema de datos/contexto, no del modelo (Hay, Zetaris, Cummings). MIDAZ ya lo resuelve: recibo + verificador + "no sé". Decirlo con esas palabras.
2. Del prototipo al uso real (Armentano, Cummings, Ranca).
3. Pruebas verificables: conformance, tests, recibos (Cummings, Shestakov).
4. Datos reales y desordenados (Ranca, Hay con reglas de calidad).

## Top 5 cambios para MIDAZ / pitch
1. **Capa semántica Zetaris con definiciones de "margen", "costo operativo", "estrella"** y que cada recibo muestre definición + SQL + columna origen (Hay).
2. **Reglas de calidad de datos + datos demo desordenados**: MIDAZ dice "no sé" por dato faltante y lo explica (Hay, Ranca).
3. **H-MEM con provenance = id del recibo Zetaris** y una contradicción detectada en la demo; conformance en verde en el video (Cummings).
4. **Escena "dato vivo"**: cambiar un costo en la fuente y la respuesta cambia; diapositiva coding harness + data harness (Armentano).
5. **Repo de un comando + test "ninguna frase sin recibo"** y frase de pitch: "Hallucination is a data problem. MIDAZ answers with receipts or says 'I don't know'." (Shestakov, Hay).

## Huecos
- Ningún juez tiene posts públicos sobre "demos falsas" específicamente; la exigencia de demo real viene de las reglas (ver doc 17) **[NO VERIFICADO]** como opinión personal.
- Autor del post ep.2 del semantic layer y autoría de Meterless por Cummings: sin confirmar.
