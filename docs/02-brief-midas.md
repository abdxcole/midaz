# 02 - Brief final: MIDAZ (2026-10-21)

> **MIDAZ — Turn your data into gold.**

Lo preparó ARGOS para Abdiel y Josué. Open Agent Hackathon 2026, **Track 02 "The Agent That Can Explain Why"**.
Este es el **brief final** para generar el plan de ejecución. Ya incorpora la crítica de VERA (`docs/05-critica-vera-plan.md`).
Regla de este documento: cada número trae su fuente. Si algo no está verificado, dice **(sin verificar)**. Las cifras del demo (colones, cantidad de productos) son **de ejemplo** y se reemplazan por lo que devuelva Zetaris el día de la grabación.

---

## 0. Instrucciones para quien haga el plan

1. Antes de escribir el plan, leer completos: `README.md`, `docs/04-jueces.md` (rúbrica y jueces) y `docs/05-critica-vera-plan.md` (crítica de VERA). Este brief ya aplica lo de 05, pero 05 trae el detalle y las fuentes.
2. **Nombre público: MIDAZ.** Lema: **"Turn your data into gold."** No usar "Jarvis" en nada público (repo, video, deck, código): es marca registrada de Marvel para asistentes de voz (ver 05, sección 5).
3. **Recortar alcance.** La meta que manda: **la pregunta del 80/20 de ganancia funcionando de punta a punta** (CSV → Zetaris → SQL → Nemotron por Nightshift → respuesta con recibo) **antes del jueves 22 al mediodía (hora CR)**. Si no corre a esa hora, se decide el plan B ese mismo día.
4. **Federación de Zetaris (fuentes, vistas, REST) es de Josué.** Abdiel instala Docker/Zetaris el miércoles; después se queda con datos, conversación, front, marca, video y deck.
5. **Verificador Nemotron: una llamada por respuesta**, no por frase. El chequeo determinístico de números (en código) corre siempre.
6. **Video objetivo ~2:30** (máximo 3:00). Lo que sobre va al deck.
7. **No inventar números.** Solo usar cifras con fuente en este documento o en 05. Si se necesita otra, buscarla y poner la URL o marcarla **(sin verificar)**.

## 1. La idea en una línea

**MIDAZ es la mano derecha del dueño de un pequeño negocio: le habla claro sobre sus márgenes para que deje de decidir a ciegas. Convierte sus datos en oro. Cada respuesta trae su prueba (la consulta SQL, las filas y un sello de verificado). Si no tiene prueba, dice "no sé".**

Nota de marca: el nombre de trabajo anterior ("Jarvis") se descartó porque "JARVIS" es marca registrada de Marvel justo para asistentes de voz (precedente: Jarvis.ai tuvo que cambiarse a Jasper). Pendiente: revisar que "MIDAZ" no esté registrado en software (USPTO y Registro Nacional de Costa Rica, 5 minutos) **(sin verificar)**.

## 2. El problema: decidir a ciegas

El dueño de una pyme decide todos los días: qué precio poner, qué pedir al proveedor, qué promocionar, si le alcanza para pagar. Casi siempre lo decide **sin información**, a puro instinto. No sabe cuál es su margen real, no sabe qué productos le dan la plata y cuáles solo le dan trabajo, y no sabe si lo que gana cubre la planilla, el alquiler y la luz.

El ejemplo del amigo dueño de negocio: en un súper, el arroz y los frijoles se venden muchísimo pero dejan poco margen. El helado o la Coca-Cola se venden menos pero dejan más. El dueño ve la caja llena de arroz vendido y cree que eso lo sostiene. Puede que no. La regla 80/20 casi nadie la aplica **a la ganancia** (si acaso, por volumen).

### 2.1 Datos reales del dolor (con fuente)

**Decidir sin datos / no saber el margen**
- **47 %** de los dueños de pequeños negocios en EE. UU. dice que maneja su negocio "casi exclusivamente" o "mayormente" por intuición. H&R Block, n=1.110, <50 empleados, sept. 2020 (clientes de H&R Block, en plena pandemia: decirlo en letra pequeña). https://www.hrblock.com/tax-center/newsroom/small-business/small-business-financial-risks/
- **72 %** de los emprendedores se guía por intuición en decisiones de crecimiento (vs 49 % de ejecutivos corporativos). Capital One Business + Inc., nov. 2024. https://www.capitalone.com/learn-grow/business-resources/risk-reward-leaders-make-decisions/
- En Australia, las decisiones más comunes por instinto son **cambios de precio (30 %)**, estrategia (30 %) e inversiones (28 %). GoDaddy / Antenna. https://www.businessnewsaustralia.com/articles/basic-instinct--study-reveals-australian-entrepreneurs-make-decisions-based-on-gut-feelings.html
- **41 %** de líderes australianos decide mucho por corazonada y **81 %** de ellos reporta consecuencias. YouGov, 2022. https://yougov.com/articles/44758-AU-evidence-based-decision-making-quality
- **33 %** de los dueños de microempresas en Reino Unido no sabe su margen (25 % no lo sabe, 8 % no sabe qué es). YouGov para FreeAgent, n=505, 2015 (dato viejo: mostrar el año). https://d3nkl3psvxxpe9.cloudfront.net/documents/Results-for_Free-Agent-Micro-Business-150623.pdf
- **47 %** de emprendedores no sabe la definición de ganancia bruta y **19 %** no sabe qué significa margen. Intuit, Reino Unido (fecha no indicada). https://bmmagazine.co.uk/finance/entrepreneurs-fail-basic-financial-fitness-test/
- **No usar:** las estadísticas de fracaso atribuidas a Jessie Hagen / U.S. Bank (no hay estudio original verificable) ni las cifras sin metodología que circulan en LinkedIn.

**Costos, plata apretada y márgenes**
- Reserva Federal de EE. UU., Small Business Credit Survey 2025 (publicado mar. 2026): **el aumento de costos fue el reto financiero más común**; **77 %** reportó ese reto o el de costos por aranceles; entre quienes pidieron financiamiento, **56 %** lo hizo para cubrir gastos operativos. https://www.fedsmallbusiness.org/reports/survey/2026/2026-report-on-employer-firms
- Mismo reporte: **46 %** de las pymes ya usa IA y, entre ellas, **la precisión (46 %) es el reto número uno**. Es el mejor dato para justificar el recibo. (Misma URL.)
- La ganancia neta promedio de los minoristas de alimentos fue **2,1 % en 2025** (FMI). https://www.fmi.org/our-research/food-industry-facts — y **~11 %** reportó pérdidas operativas. https://www.supermarketnews.com/grocery-trends-data/fmi-report-grocers-double-down-on-technology-health-and-value-as-economic-pressures-persist
- Márgenes por producto en Noruega 2025: chocolate y snacks **51-56 %**, bebidas sin alcohol **29-36 %**, huevos **3-17 %**, carne **-4 a 5 %** (Konkurransetilsynet). https://konkurransetilsynet.no/significant-differences-in-income-between-various-grocery-products/?lang=en

**Supervivencia (Costa Rica y LATAM)**
- **Costa Rica:** de las empresas formales nacidas en 2017, solo **50,3 %** seguía viva a los 5 años (BCCR, vía La Nación). https://www.nacion.com/economia/negocios/mitad-de-las-empresas-en-costa-rica-desaparecen-en/GHOT2VGWGZAT3OJPXT7GLBSRNQ/story/
- **Costa Rica:** microempresas **53 %** de probabilidad de llegar a 5 años; grandes, 95 % (Estado de la Nación 2023). https://repositorio.conare.ac.cr/server/api/core/bitstreams/685631b9-a29d-477a-85c9-61fd7a2a9464/content
- **Costa Rica:** 97,4 % de las empresas son pyme y 80,84 % micro (MEIC 2021). https://taxescr.com/wp-content/uploads/2022/07/DIGEPYME-INF-038-2021.pdf
- **América Latina y el Caribe:** pymes = **99,5 %** de las empresas y cerca del **60 %** del empleo formal (OCDE/CAF/SELA 2024). https://www.oecd.org/es/publications/indice-de-politicas-para-pymes-america-latina-y-el-caribe-2024_807e9eaf-es.html
- **América Latina:** **61 %** del empleo está en microempresas, con productividad de solo **17 %** de la de las grandes (CEPAL). https://www.cepal.org/en/notas/cepal-presenta-un-panorama-actual-mipymes-america-latina-caribe-foro-economia-cuba
- No existe (en lo revisado) un estudio de CR/LATAM sobre qué % de dueños conoce su margen. Oportunidad: entrevistas propias (ver 2.3).

**Tiempo perdido en papeleo**
- Dueños en EE. UU. dedican **~20 h/semana** a tareas contables (Cornerstone Advisors, 750 dueños, Q4 2023, vía Tight). https://www.tight.com/blog/accounting-insights-from-750-small-business-owners
- Microempresas en Reino Unido: **15 de 79 h semanales** en administración financiera (Starling Bank). https://www.starlingbank.com/docs/reports-research/MakeBusinessSimpleReport.pdf

### 2.2 El dolor emocional
- **81 %** de dueños de pequeños negocios vivió burnout en 2025 (Enji, n=245; muestra pequeña, decirlo). https://www.enji.co/state-of-small-business-report-2025
- **72 %** de los solopreneurs que pensó en dejar su negocio citó estrés financiero (Simply Business 2025). https://www.simplybusiness.com/wp-content/uploads/sites/2/2025/08/Simply_Business_2025_Solopreneur_Report.pdf

**Frase emocional:** "Trabaja 12 horas al día y no sabe cuál de sus productos le está pagando el salario."

### 2.3 Validación humana (agregar, vale para Impacto)
Conseguir una cita o audio de 10 s del amigo dueño de negocio (con permiso), o entrevistar a 3-5 dueños de pulpería/soda el jueves o viernes, con una frase textual. Impacto vale 30 y desempata.

### 2.4 Las cifras más fuertes para el pitch
1. **"En Costa Rica, la mitad de las empresas formales no llega a 5 años."** (BCCR, 50,3 %.)
2. **"Para las pymes que ya usan IA, el problema número uno es la precisión (46 %)."** (Reserva Federal 2025.) Une "deciden a ciegas" con "la IA inventa": MIDAZ resuelve los dos.
3. Apoyo: **47 %** decide por intuición (H&R Block 2020, con el año visible).

## 3. Persona

**Doña Marta, 52 años, dueña de "Súper La Esquina"** (minisúper de barrio, ejemplo inventado para el demo).
- 4 empleados, ~1.200 productos, POS que exporta Excel, facturas de proveedores en papel y correo.
- Sabe cuánto vendió hoy. **No sabe** cuánto ganó por producto ni si cubre planilla + alquiler + luz.
- Pone precios copiando a la competencia o "un 20 % a ojo". Contador una vez al año. Vive en WhatsApp; no quiere otro sistema ni gráficos.

## 4. La solución

**Casi sin interfaz:** hablar y recibir información (chat; voz solo si sobra tiempo). La "pantalla" es una conversación. **Modo dueño** (2-3 frases + sello) y **modo juez** ("bajo el capó": SQL, filas, receipts) en la misma pantalla; explicarlo en el deck como decisión de UX.

Cómo funciona:
1. El dueño pregunta en lenguaje normal: "¿Qué productos me dan la plata?".
2. El agente consulta los datos del negocio en **Zetaris** (ventas, costos/inventario, gastos), corre SQL y lee resultados.
3. Responde corto: 2-3 frases + una recomendación.
4. **Cada respuesta trae su prueba:** SQL exacta, filas, fuente y sello **"verificado"**. El chequeo de números se hace en código siempre; un segundo Nemotron (verificador) revisa **la respuesta completa en una sola llamada** y quita lo que no tenga evidencia.
5. **Si no hay evidencia, dice "no sé"** y qué dato falta ("No tengo los costos de la carne").
6. **Recuerda** con H-MEM (Meterless) hallazgos y decisiones del dueño.

### 4.1 Preguntas del MVP (en orden de prioridad)
1. **80/20 de GANANCIA (obligatoria, de punta a punta antes del jueves 12:00 CR):** qué 20 % de productos hace el 80 % de la ganancia bruta, con contraste por volumen (arroz vs helado).
2. **"¿Me alcanza?" + "no sé":** ganancia bruta del mes vs gastos operativos; si falta, cuánto y sugerencias de precio con cálculo visible (siempre sugerencia; decide el dueño). Pregunta sin datos (carne) → "no sé".
3. **Memoria:** "¿Cómo me fue con lo de la Coca?" vía H-MEM.
El "por qué" con hipótesis múltiples entra solo si ya está listo el domingo.

### 4.2 Fórmulas
- Ganancia bruta por producto = Σ (precio de venta − costo unitario) × unidades (con descuentos).
- Margen % = ganancia bruta / ventas netas.
- 80/20: ordenar por ganancia bruta, acumular, cortar en 80 %.
- Punto de equilibrio: gastos operativos del mes / margen % promedio.
- Simulación de precio: (precio nuevo − costo) × unidades estimadas; la caída de unidades es un supuesto que elige el dueño, nunca un hecho.
- **Precios en colones con IVA incluido; el IVA queda fuera del cálculo y se dice en pantalla** en la escena de precios.

## 5. Alcance

### MVP (entrega 27-oct)
- Datos de ejemplo de minisúper (**rotulados "Sample data"**) en **3 fuentes separadas federadas en Zetaris** (ventas POS / costos+inventario / gastos operativos). Frase honesta en video y README: "patrones de margen inspirados en datos públicos de precios" + estructura validada por el amigo dueño (si se consigue), para que no parezca arreglado.
- Las 3 preguntas de 4.1 con prueba o "no sé".
- Chat web mínimo. Voz: primero en recortarse.
- H-MEM con pruebas pasando.
- Nightshift como proveedor, lane Nemotron fijo (nunca `meterless/auto`), receipt con nombre del modelo.
- **Métrica de confianza:** correr el set de 15 preguntas (`golden.yaml`) y reportar "X/15 correctas, 0 números inventados, N/N 'no sé' correctos" (cifras reales del día, no inventadas).
- **`DEMO.md` de 60 s** para jueces: un comando con `MODO=replay`.

### Después (solo como visión en el pitch)
Recordatorios de recompra, clientes fieles, actuar dentro del ERP/POS con aprobación, WhatsApp, alertas proactivas, otros rubros.

## 6. Historia del demo (~2:30, en inglés con subtítulos en español; 3 escenas fuertes)
Las cifras en ₡ son de ejemplo: se usan las que devuelva Zetaris el día de la grabación, siempre con "Sample data".
1. **0:00-0:25 — El dolor.** Doña Marta cierra la caja; vendió mucho y no le alcanza. En pantalla: "50 % of Costa Rican businesses don't survive 5 years — BCCR".
2. **0:25-1:05 — Escena A: 80/20 de ganancia.** "Which products actually make me money?" → respuesta corta + sello → recibo SQL + filas. Arroz: #1 en ventas, muy abajo en ganancia. El verificador tacha en rojo una frase sin prueba.
3. **1:05-1:45 — Escena B: "¿Me alcanza?" + "no sé".** Faltante del mes y sugerencia de precio con supuestos (IVA fuera) en una caja. Luego "¿Cuánto gano con la carne?" → "No sé: no tengo el costo de la carne."
4. **1:45-2:20 — Escena C: memoria + bajo el capó.** H-MEM recuerda la decisión. 3 fuentes → Zetaris → Nightshift con lane Nemotron → pruebas en verde. Métrica de `golden.yaml`.
5. **2:20-2:30 — Cierre.** Cifra en ₡ de Zetaris. "MIDAZ. Turn your data into gold. Stop deciding blind."

## 7. Pitch

### 20 segundos
"Los dueños de pequeños negocios deciden a ciegas: por intuición, sin saber su margen. MIDAZ es su mano derecha: usted le habla y le dice qué productos le dan la plata, cuáles solo le dan trabajo y si lo que gana cubre los gastos. Cada respuesta trae su prueba. Y si no tiene prueba, le dice 'no sé'. MIDAZ: convierta sus datos en oro."

(Inglés para el video: "Small business owners run on gut feeling, without knowing their margins. MIDAZ is their right hand: just talk to it, and it tells you which products actually pay your bills, which ones just keep you busy, and whether your margin covers your costs. Every answer comes with its proof. No proof? It says 'I don't know.' MIDAZ — turn your data into gold.")

### 3 minutos (guion hablado; el video real se recorta a ~2:30)
1. **El problema (40 s).** Doña Marta trabaja 12 horas, vende mucho y no sabe por qué no le alcanza. En Costa Rica, la mitad de las empresas formales no llega a 5 años (BCCR). 47 % de los dueños maneja su negocio por intuición (H&R Block 2020). Un súper gana en promedio 2,1 % neto (FMI): un error de precio se come el mes.
2. **Por qué lo de hoy no sirve (20 s).** Los dashboards dicen qué pasó, no por qué. Los chatbots inventan números: para las pymes que ya usan IA, la precisión es el reto número uno (46 %, Reserva Federal). Ya hay asistentes en LATAM (SocIA, Margen/Margo): el mercado quiere hablar con sus números; lo que nadie resuelve es la confianza.
3. **La solución (60 s).** Demo: 80/20 de ganancia con recibo, "¿me alcanza?", sugerencia de precio, "no sé" cuando falta el dato, memoria. Cada respuesta trae su prueba.
4. **Cómo está hecho (40 s).** 3 fuentes federadas en Zetaris; Nemotron vía Meterless Nightshift; un segundo Nemotron verifica cada respuesta; H-MEM dentro de la función de memoria, con prueba en verde.
5. **Visión (20 s).** Hoy márgenes; mañana recompra, clientes fieles y acciones en el ERP con permiso. "Deje de decidir a ciegas. MIDAZ: Turn your data into gold."

## 8. Encaje con el Track 02 y la rúbrica
Fuente: `docs/04-jueces.md`. Puntaje: **Impacto 30, Técnico 20, Innovación 15, Demo 15, Producto y UX 10, Tecnología de sponsors 10.** Empate: más Impacto, luego quien entregó antes. **Entregables: video de 1-4 min, slide deck, repo GitHub con README que explique el uso de Zetaris, Meterless y NVIDIA** (y, si se quiere, la herramienta de código; Cursor es opcional desde el anuncio del 2026-10-22). Los jueces ven sobre todo el video. **Meterless es obligatorio.**

| Criterio | Cómo lo atacamos |
|---|---|
| Impacto (30) | Doña Marta + dolor citado + cifra en ₡ de los datos de ejemplo + voz real de un dueño |
| Técnico (20) | SQL → chequeo en código → verificador → respuesta; cálculos en SQL; métrica `golden.yaml`; README y `DEMO.md` que corren |
| Innovación (15) | Sin interfaz + prueba por respuesta + "no sé" honesto + 80/20 de ganancia |
| Demo (15) | ~2:30, 3 escenas, momento "aha" arroz vs helado |
| Producto/UX (10) | Modo dueño / modo juez; respuestas de 2-3 frases; marca MIDAZ |
| Sponsors (10) | Ver 8.1 |

### 8.1 No negociable
1. Recibo SQL junto a cada frase con número (consulta, vista de origen, filas, hora).
2. 3 fuentes unidas en Zetaris (no un CSV), idealmente vista semántica `margen_por_producto`.
3. Lane Nemotron fijo + verificador Nemotron (una llamada por respuesta); receipt de Nightshift con nombre del modelo, sin llaves.
4. H-MEM con pruebas en pantalla.
5. Cifra en ₡ sobre datos rotulados para cerrar.
6. (Opcional) Slide de cómo se construyó.

## 9. Tecnología obligatoria
- **Zetaris** en Docker local, REST (`POST /api/v1.0/sql-editor/sqls/run` en :8888, según el kit). Toda cifra sale de Zetaris. **Dueño: Josué.**
- **Meterless Nightshift** (compatible con OpenAI). Llave NVIDIA solo en Providers de Nightshift, nunca en app ni repo.
- **NVIDIA Nemotron**, lane fijo. Nombres exactos de modelos **(sin verificar)**: copiarlos del catálogo de Nightshift.
- **H-MEM** con prueba. Markovian / Scout Intent solo si sobra tiempo.
- Herramienta de código a elección (Cursor, Claude Code, Windsurf o Copilot). **Cursor no da créditos**: el plan no depende de ellos.

## 10. Restricciones
- Repo de código nuevo y público (commits desde el 21-oct 6:00 pm CR). Nada de archivos privados de Abdiel.
- Datos 100 % de ejemplo, rotulados.
- Cupo NVIDIA ~400 solicitudes/día compartidas: caché, SQL determinístico, modo replay, verificador una vez por respuesta.
- Sin llaves en repo, video ni capturas.
- Inscripción antes del **22-oct 5:59 pm CR**. Entrega límite **27-oct 5:45 pm CR**; apuntar al mediodía.
- Documentación interna en español; video y README pueden ir en inglés con resumen en español.

## 11. Roles (reparto corregido por VERA)
- **Abdiel — producto, datos y narrativa:** instalar Docker/Zetaris el miércoles; generador de datos de ejemplo; diseño de la conversación y del recibo; front; marca MIDAZ; validación con dueños; guion, video, deck, README visual; checklist de entrega.
- **Josué — backend e infraestructura de datos:** **federación de Zetaris (fuentes, vistas, REST)**, repo, API, agente (SQL → chequeo → verificador → respuesta), Nightshift, H-MEM y su prueba, `golden.yaml`, errores, modo replay.

## 12. Calendario (hora CR)
| Día | Abdiel | Josué |
|---|---|---|
| Mié 21 noche | Docker + WSL + Zetaris | Nightshift + llave NVIDIA en Providers + lane Nemotron probado |
| **Jue 22, 12:00** | **Portón: P1 (80/20) de punta a punta** con datos mínimos | **Portón: P1 de punta a punta** (Zetaris + Nightshift + recibo) |
| Jue 22 (inscripción 5:59 pm) | Equipo en HackOS. Esquema y generador de datos. Si P1 falló: decidir plan B hoy | Repo público; 3 fuentes en Zetaris |
| Vie 23 | Datos finales; respuestas esperadas a mano; entrevistas a dueños | P2 + "no sé"; verificador una vez por respuesta |
| Sáb 24 | Front (chat + recibo, modo dueño/juez) | H-MEM + prueba; caché y tope de cupo |
| Dom 25 | Guion ~2:30; diagrama; voz solo si sobra | `golden.yaml`, replay, `DEMO.md` |
| Lun 26 | Grabar video, deck, README | Congelar código, revisión de secretos, instalación desde cero |
| Mar 27 | Entregar antes del mediodía | Tag/release y clone limpio |

## 13. Competencia
- **SocIA (Argentina, PymeCloud):** "La IA que te dice la verdad de tu negocio"; conecta al ERP y responde por WhatsApp. https://socia.com.ar/
- **Margen / asistente "Margo" (LATAM):** margen real por producto, punto de equilibrio, "¿por qué gano menos si vendí más?" — casi la misma historia del demo. https://margen.lat/
- **Cuenta Clara (Argentina):** costos, márgenes y caja para kioscos y almacenes. https://cuentaclara.ar/
- **SocIA (WHITE RUBYK):** agente conversacional de negocio y finanzas. https://tusociapp.com/terminos
- **Negocio Claro IA:** asistente por WhatsApp de inventario y finanzas. https://negocioclaroia.com/
- **Finlessly**, **CafeTally**, **CentsOf.AI**, **Figureit**, **StoreHero** (en inglés, atados a Shopify/Square/QuickBooks). https://finlessly.ai/ai-in-retail/ · https://cafetally.com/pricing · https://centsof.ai/solutions/retail · https://figureit.ai/ · https://storehero.ai/
- Copilotos de BI (Power BI Copilot, Tableau): para analistas, no dueños.

**Diferenciador real (ya no es "nadie lo hace en español"):** **cada respuesta con prueba SQL verificada por un segundo modelo, y "no sé" cuando falta el dato.** Ninguno de los competidores vistos lo promete explícitamente (revisión rápida de sitios; no probamos los productos). Frase: "El mercado ya validó que los dueños quieren hablar con sus números. Lo que nadie resuelve es la confianza."

## 14. Riesgos
1. Base técnica con 5 incógnitas (REST de Zetaris, federación Postgres+CSV, capa semántica local, paquete H-MEM, nombres de modelos) → portón del jueves al mediodía.
2. Abdiel sobrecargado → federación pasada a Josué.
3. Cupo NVIDIA → verificador una vez por respuesta, caché, replay.
4. Datos que parecen arreglados → frase honesta + validación del amigo.
5. El LLM inventa números → cálculos en SQL; chequeo en código compara cada número con las filas.
6. Video largo → ~2:30, 3 escenas; el resto al deck.
7. Marca MIDAZ sin revisar → chequeo rápido en USPTO y Registro Nacional antes del logo.

## 15. Preguntas abiertas
1. ¿MIDAZ libre como marca de software? (5 min de chequeo.)
2. Nombres exactos de modelos Nemotron en Nightshift y cuál para el verificador.
3. ¿El amigo dueño valida el demo o presta la estructura (no los datos) de su Excel/POS?
4. Tamaño del dataset de ejemplo (productos, meses).
