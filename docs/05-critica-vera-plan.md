# 18 - Crítica constructiva del plan de MIDAZ (2026-10-21)

Revisión independiente (VERA) de `01-kit-hackathon`, `02-brief`, `03-plan` y `04-jueces`. Regla: cada cifra lleva su URL. Lo que no se pudo verificar dice **(sin verificar)**. No se tocó ningún otro archivo.

---

## 1. Veredicto

**El plan es bueno, mae. De hecho, muy bueno para un hackathon.** Está alineado al Track 02 y a la rúbrica: recibo SQL por frase, "no sé" honesto, fiscal Nemotron que borra frases, 3 fuentes en Zetaris, H-MEM con pruebas, portones diarios y una lista de recortes. Pocos equipos llegan con algo tan aterrizado.

**Pero así como está, es demasiado plan para 6 días y 2 personas.** El riesgo no es la idea, es la ejecución. Calificación honesta: idea 9/10, alcance 6/10.

### Riesgos de factibilidad (de mayor a menor)
1. **Demasiadas incógnitas en la base técnica** (sección 14 del plan): REST de Zetaris, si Zetaris federa Postgres + CSV, la capa semántica en local, el paquete y la suite de H-MEM, los nombres de los modelos en Nightshift. Son 5 dependencias **(sin verificar)** que bloquean todo lo demás. Si dos fallan el jueves, el viernes se cae.
2. **Abdiel está sobrecargado.** Le tocan Docker/Zetaris, datos sintéticos, las 3 fuentes federadas (viernes), el front completo (sábado), marca, voz, guion, video, deck y README visual. Josué tiene el backend, que es grande pero coherente. La infraestructura de Zetaris (fuentes y vistas) es trabajo de backend y debería ser de Josué.
3. **El fiscal de 3 capas cuesta llamadas.** Re-ejecutar SQL + chequear números + lane Nemotron por cada frase, con unas 400 solicitudes al día compartidas, se va rápido mientras se ensaya. El chequeo numérico en código es lo valioso. El lane Nemotron fiscal debería correr una vez por respuesta, no una vez por frase.
4. **Datos sintéticos "calibrados" pueden verse arreglados.** Si el video dice "18 productos hacen el 80 %" y el juez sospecha que el generador está hecho para que dé eso, se pierde credibilidad. Hace falta una frase honesta: "patrones de margen inspirados en datos públicos de precios" + la estructura validada por el amigo dueño de negocio.
5. **Video de 3:00-3:45 con 7 escenas.** Es denso para jueces que lo ven en inglés. Cada escena extra es una toma más que puede fallar el lunes.
6. **La competencia LATAM ya existe** (ver 2.3). Si un juez busca "AI margin assistant Spanish", encuentra a SocIA o Margen/Margo y el "nadie hace esto" del brief se cae.
7. **El nombre "Jarvis"** es un riesgo real y documentado (sección 5). Hay que cambiarlo antes de pintar el logo.
8. **Dato a confirmar en el kit:** el brief dice que Meterless es obligatorio y la página oficial dice "Zetaris + Meterless integrados, Cursor para desarrollar, NVIDIA donde aporte". El encargo de esta revisión lo resume como "Zetaris + Cursor + Nemotron". Que no se les olvide que **Meterless es obligatorio** según el archivo 17.

---

## 2. Qué mejorar y qué agregar

### 2.1 Mejoras (prioridad alta)
1. **Spike de 4 horas el miércoles o jueves en la mañana, antes de escribir código de verdad.** Una sola pregunta (P1, el 80/20) de punta a punta: CSV → Zetaris → SQL → Nemotron por Nightshift → frase con recibo. Si eso corre el jueves al mediodía, el resto es repetir el patrón. Si no corre, se decide el plan B ese mismo día y no el viernes.
2. **Repartir mejor el trabajo:** Josué se encarga de Zetaris (fuentes, vistas, REST) y del backend. Abdiel se encarga de los datos (generador de datos), la conversación, el front, la marca, el video y el deck. Abdiel instala Docker el miércoles, pero el viernes la federación es de Josué.
3. **Recortar el MVP a 3 escenas fuertes en vez de 7:** (a) 80/20 de ganancia, con el arroz contra el helado y el recibo; (b) "¿me alcanza?" + "no sé" de la carne; (c) memoria + bajo el capó. El "por qué" con hipótesis H1-H4 queda como el clímax de (b) solo si ya está listo el domingo.
4. **Fiscal más barato:** el chequeo determinístico de números (en código) se hace siempre. El lane Nemotron fiscal se llama **una vez por respuesta** con todas las frases y sus filas. Así baja el consumo de cupo y sigue habiendo un "segundo Nemotron" visible para el premio DGX Spark.
5. **Video de 2:30-3:00, no de 3:45.** Si sobra contenido, va al deck. Jueces cansados premian claridad.
6. **Cambiar la sección "Competencia y hueco".** Ya no es "nadie lo hace en español". El diferenciador real es: **"cada frase con prueba SQL verificada por un segundo modelo, y 'no sé' cuando falta el dato"**. Ninguno de los competidores que vimos promete eso de forma explícita (revisión rápida de sus sitios; no probamos los productos).

### 2.2 Qué agregar
1. **Una métrica de confianza medible para la slide de Impacto/Técnico:** correr el set de 15 preguntas (`golden.yaml`) y reportar "X/15 correctas, 0 números inventados, 4/4 'no sé' correctos". Esto le habla directo a Michael Hay ("la esperanza no es estrategia") y a Shestakov (tests).
2. **Un dato de por qué el recibo importa**, ya con fuente: en la encuesta de la Reserva Federal de EE. UU. de 2025, **la precisión (46 %) es el principal reto de las pymes que ya usan IA** (ver 3.4). Ese es el puente perfecto entre "dueños deciden a ciegas" y "la IA inventa": el producto resuelve los dos.
3. **Validación humana real, aunque sea pequeña:** un audio o una cita de 10 segundos del amigo dueño de negocio (con permiso), o 3-5 dueños de pulpería/soda entrevistados el jueves o viernes, con una frase textual. Impacto vale 30 y desempata. Una voz real pesa más que cualquier estadística gringa.
4. **"Modo dueño" contra "modo juez" en la misma pantalla:** el dueño ve 2-3 frases y un sello; el juez toca "bajo el capó". El plan ya lo tiene; la idea es que salga explícito en el deck como decisión de UX.
5. **Supuesto de precios en colones con IVA:** el plan deja el IVA fuera. Está bien, pero hay que decirlo en pantalla en la escena de precios para que nadie lo cuestione.
6. **Un `DEMO.md` de 60 segundos para jueces** (un comando con `MODO=replay`), por si alguno sí corre el repo.

### 2.3 Competencia que el brief no menciona (encontrada en esta revisión)
- **SocIA (Argentina, PymeCloud):** "La IA que te dice la verdad de tu negocio"; se conecta al ERP y responde por WhatsApp. https://socia.com.ar/
- **Margen / asistente "Margo" (LATAM):** margen real por producto, punto de equilibrio, "¿por qué gano menos si vendí más?". Es casi la misma historia del demo. https://margen.lat/
- **Cuenta Clara (Salta, Argentina):** costos, márgenes y proyección de caja para kioscos y almacenes. https://cuentaclara.ar/
- **SocIA (WHITE RUBYK, otra empresa con el mismo nombre):** agente conversacional para negocio y finanzas, web y WhatsApp. https://tusociapp.com/terminos
- **Negocio Claro IA:** asistente por WhatsApp de inventario y finanzas. https://negocioclaroia.com/

**Cómo usarlo a favor:** "El mercado ya validó que los dueños quieren hablar con sus números. Lo que nadie resuelve es la confianza: nosotros mostramos la prueba de cada frase y decimos 'no sé'."

---

## 3. Datos reales del dolor (con fuente)

Verificados hoy en la fuente original (marcados ✔) o tomados del brief 15 y no re-verificados (marcados ↺, el brief ya trae la URL). **No se inventó ningún número.**

### 3.1 Decidir a ciegas / no saber el margen
- ✔ **47 %** de los dueños de pequeños negocios (menos de 50 empleados, EE. UU.) dice que maneja su negocio "casi exclusivamente" o "mayormente" por intuición y no por datos. H&R Block, n=1.110, sept. 2020. **Ojo:** son clientes de H&R Block y la encuesta es de plena pandemia; decirlo así en letra pequeña. https://www.hrblock.com/tax-center/newsroom/small-business/small-business-financial-risks/
- ✔ En esa misma encuesta, **90 %** no buscó asesoría financiera ni tributaria profesional por los efectos del COVID, y **61 %** se sentía más ansioso o deprimido de lo normal. Solo **22 %** buscaría apoyo de salud mental. (Misma URL.)
- ↺ **33 %** de los dueños de microempresas en Reino Unido no sabe su margen de ganancia (YouGov para FreeAgent, n=505, 2015). Es un dato viejo (2015); usarlo con el año visible. https://d3nkl3psvxxpe9.cloudfront.net/documents/Results-for_Free-Agent-Micro-Business-150623.pdf
- ↺ **72 %** de los emprendedores se guía por intuición en decisiones de crecimiento (Capital One Business + Inc., 2024). https://www.capitalone.com/learn-grow/business-resources/risk-reward-leaders-make-decisions/

### 3.2 Costos, plata apretada y márgenes
- ✔ Reserva Federal de EE. UU., Small Business Credit Survey 2025 (6.525 empresas con empleados, publicado el 3 mar 2026): **el aumento de costos (mercadería, servicios o salarios) fue el reto financiero más común**, y **77 %** de las empresas reportó ese reto o el de costos por aranceles. Entre quienes pidieron financiamiento, **56 %** lo hizo para cubrir gastos operativos. https://www.fedsmallbusiness.org/reports/survey/2026/2026-report-on-employer-firms
  - Nota: el brief cita 73 % / 54 % / 50 % de ese mismo reporte. Esas cifras exactas **no aparecen en el resumen web**; pueden estar en el PDF completo. **Verificar en el PDF antes de usarlas.**
- ↺ La ganancia neta promedio de los minoristas de alimentos fue **2,1 %** en 2025 (FMI). https://www.fmi.org/our-research/food-industry-facts
- ↺ Márgenes por producto muy distintos en supermercados de Noruega (snacks y chocolate 51-56 %, carne -4 a 5 %), Konkurransetilsynet 2025. https://konkurransetilsynet.no/significant-differences-in-income-between-various-grocery-products/?lang=en
- **El famoso "82 % de los negocios quiebra por flujo de caja" (U.S. Bank / Jessie Hagen) NO tiene un estudio original verificable. No usarlo.** El brief ya lo marcó bien. https://www.maplestbookkeeping.com/questions/cash-flow-failure-statistic

### 3.3 Supervivencia y PYMEs en Costa Rica y LATAM
- ↺ **Costa Rica:** de las empresas formales que nacieron en 2017, solo **50,3 %** seguía viva a los 5 años (BCCR, vía La Nación). https://www.nacion.com/economia/negocios/mitad-de-las-empresas-en-costa-rica-desaparecen-en/GHOT2VGWGZAT3OJPXT7GLBSRNQ/story/
- ↺ **Costa Rica:** las microempresas tienen **53 %** de probabilidad de llegar a 5 años; las grandes, 95 % (Estado de la Nación 2023). https://repositorio.conare.ac.cr/server/api/core/bitstreams/685631b9-a29d-477a-85c9-61fd7a2a9464/content
- ↺ **Costa Rica:** 97,4 % de las empresas son pyme y 80,84 % son micro (MEIC 2021). https://taxescr.com/wp-content/uploads/2022/07/DIGEPYME-INF-038-2021.pdf
- ✔ **América Latina y el Caribe:** las pymes son el **99,5 %** de las empresas y cerca del **60 %** del empleo formal; casi 9 de cada 10 son microempresas (OCDE/CAF/SELA, SME Policy Index LAC 2024). https://www.oecd.org/es/publications/indice-de-politicas-para-pymes-america-latina-y-el-caribe-2024_807e9eaf-es.html
- ✔ **América Latina:** **61 %** del empleo está en microempresas, pero su productividad es solo **17 %** de la de las grandes (CEPAL). Esto encaja con la frase "trabajan muchísimo y no ven la ganancia". https://www.cepal.org/en/notas/cepal-presenta-un-panorama-actual-mipymes-america-latina-caribe-foro-economia-cuba
- **No encontré** un estudio de Costa Rica o LATAM que mida qué porcentaje de dueños de pyme conoce su margen. Ese dato **no existe** en lo que revisé. Es una oportunidad: "nadie lo ha medido aquí; nosotros preguntamos a X dueños" (si hacen las entrevistas de 2.2).

### 3.4 Estrés del dueño y confianza en la IA
- ↺ **81 %** de los dueños de pequeños negocios vivió burnout en 2025 (Enji, n=245; muestra pequeña, decirlo). https://www.enji.co/state-of-small-business-report-2025
- ↺ **72 %** de los solopreneurs que pensaron en dejar su negocio citó el estrés financiero (Simply Business 2025). https://www.simplybusiness.com/wp-content/uploads/sites/2/2025/08/Simply_Business_2025_Solopreneur_Report.pdf
- ✔ **46 %** de las pymes de EE. UU. ya usa IA, y entre ellas **la precisión (46 %) es el reto número uno** (Reserva Federal, SBCS 2025). Es el mejor dato para justificar el recibo SQL. https://www.fedsmallbusiness.org/reports/survey/2026/2026-report-on-employer-firms

### 3.5 Las 2 cifras más fuertes para el pitch
1. **"En Costa Rica, la mitad de las empresas formales no llega a 5 años."** (BCCR, 50,3 %; local, oficial y emocional.)
2. **"Para las pymes que ya usan IA, el problema número uno es la precisión (46 %)."** (Reserva Federal 2025; conecta el dolor con la solución.)
Como apoyo: 47 % decide por intuición (H&R Block 2020, con el año visible).

---

## 4. Pitch emocional mejorado

Alineado al archivo 17: Impacto 30 (persona + cifra), Técnico 20, Innovación 15, Demo 15, UX 10, Sponsors 10. Los jueces ven sobre todo el video, en inglés.

### 4.1 Gancho (primeros 5 segundos)
> **"Marta sold 18 million colones last month. She still couldn't pay the light bill. Her best-selling product was the reason."**

Alternativa más corta: **"Her best seller was quietly bankrupting her."**

### 4.2 La historia (30 segundos, en inglés con subtítulos en español)
Doña Marta abre su minisúper a las 6 a. m. y cierra a las 9 p. m. Vende arroz y frijoles todo el día; la caja se llena. A fin de mes, no alcanza. No es floja ni mala para los negocios: **nadie le ha mostrado nunca cuánto le deja cada producto.** Su contador viene una vez al año. Los dashboards no los entiende y los chatbots le inventan números. En Costa Rica, la mitad de los negocios como el suyo no llega a 5 años.
Entonces le pregunta a su mano derecha: *"¿Qué productos me dan la plata?"*. Le responde con la verdad y le enseña la prueba. Y cuando no sabe, se lo dice.

**Frase de cierre:** *"It doesn't guess. It shows its receipts."* / *"No adivina. Le enseña el recibo."*

### 4.3 Guion de video de 60-90 segundos (versión corta; la de 3 minutos del plan queda como respaldo)

| Tiempo | Imagen | Voz (EN) | Criterio que suma |
|---|---|---|---|
| 0:00-0:08 | Mano de Marta contando billetes de noche; rótulo "Sample data" | "Marta sold 18 million colones last month. She still couldn't pay the light bill." | Impacto |
| 0:08-0:18 | Texto grande: "50% of Costa Rican businesses don't survive 5 years — BCCR" | "Half the businesses like hers close within five years. Most never knew which products paid the bills." | Impacto (cifra con fuente) |
| 0:18-0:35 | Chat: "Which products actually make me money?" → respuesta corta + sello ✔ → tap → recibo SQL + filas | "Rice is her #1 seller… and #41 in profit. Every sentence comes with its SQL receipt from Zetaris." | Innovación, Track 02, Sponsors |
| 0:35-0:48 | Frase con número inventado tachada en rojo por el fiscal | "A second Nemotron audits every claim against the data and deletes what it can't prove." | Técnico, premio NVIDIA |
| 0:48-0:58 | "How much do I make on meat?" → "I don't know — I don't have meat costs." | "And when there's no evidence, it says: I don't know." | Confianza, UX |
| 0:58-1:10 | "Do I cover my expenses?" → "You're short ₡180,000. Raise these 6 items ₡100 and you close the gap." Supuestos en una caja | "Not just what happened: why, and what to do." | Impacto, Demo |
| 1:10-1:22 | Bajo el capó: 3 fuentes → Zetaris → Nightshift con lane Nemotron → `pytest` verde (H-MEM) | "Three sources federated in Zetaris. Nemotron via Meterless Nightshift. H-MEM memory, tested." | Sponsors, Técnico |
| 1:22-1:30 | Negro. Cifra en ₡ de Zetaris. Nombre + lema | "Stop deciding blind." | Cierre emocional |

Las cifras en ₡ son de calibración: se usan las que devuelva Zetaris el día de la grabación y siempre con el rótulo "sample data".

---

## 5. Riesgo de marca de "Jarvis" y nombres alternativos

### 5.1 El riesgo es real y alto
- **Marvel Characters, Inc. es dueña de la marca registrada "JARVIS" en EE. UU.** (Reg. 4737881, clase 9) precisamente para *"software … for use as a voice controlled personal digital assistant"*. Está viva y renovada. https://trademarks.justia.com/862/94/jarvis-86294162.html · https://www.trademarkia.com/jarvis-86294162
- **Precedente directo:** Jarvis.ai (asistente de escritura con IA) recibió un cease-and-desist de Marvel/Disney por usar "Jarvis" con "AI assistant" y se cambió el nombre a **Jasper** en enero de 2022. El CEO dijo que Disney "podía tenerlos en la corte todo lo que quisiera". https://www.linkedin.com/posts/daverogenmoser_jaspernation-activity-6891440232487555072-2bO_ · https://marketingwithrobots.com/blog/jarvis-ai-rebrands-to-jasper-ai/
- Para un hackathon, el riesgo legal inmediato es bajo. El riesgo de **imagen** con los jueces (se ve "derivado") y el de **tener que cambiar el nombre después** si el proyecto sigue sí son reales. Además, "asistente de voz" es exactamente el uso que cubre la marca de Marvel. **Recomendación: no usar "Jarvis" en nada público (repo, video, deck).** Internamente se puede seguir diciendo así.

### 5.2 Alternativas (chequeo rápido por web el 2026-10-21; **no es una búsqueda de marcas formal**)

| Nombre | Por qué funciona | Chequeo rápido |
|---|---|---|
| **Dato Duro** ⭐ | En tico y en LATAM, "dato duro" es un hecho comprobado: es exactamente la promesa del Track 02. En inglés se explica solo con el lema "Hard facts, with receipts". | No encontré ninguna app o producto de IA con ese nombre (la búsqueda solo dio otros productos genéricos). **Parece libre (sin verificar en registros de marcas).** |
| **Doña Datos** | Cálido, latino, personifica a la mano derecha; perfecto para la historia de Doña Marta. | La búsqueda no devolvió ningún producto con ese nombre. Parece libre (sin verificar). |
| **Mano Derecha** | La idea original del brief. | **Choca:** ya existe "La Mano Derecha" (red de ejecutivos para pymes en España/Francia) y una empresa "Mano Derecha" que ofrece agentes de IA para pymes. https://www.lamanoderecha.com/ · https://linkedin.com/company/manoderecha-formaciones — **No recomendado.** |
| **Cuadre** | "Cuadrar caja" es muy tico. | **Ocupado:** Cuadre.io (Colombia, conciliación con IA). https://www.cuadre.io/ — **No recomendado.** |
| **Testigo** (el nombre anterior) | Encaja con la evidencia. | **Ocupado:** testigo.ai (plataforma legal de evidencia digital). https://andresguzman.law/investigacion-desarrollo — **No recomendado.** |
| *Margen / Margo / SocIA / Cuenta Clara / Pulpo* | — | **Todos ocupados** por competidores directos (ver 2.3; Pulpo: https://pulpoapp.com/). Evitar. |

**Recomendación:** **"Dato Duro"**, con el lema *"Hard facts. With receipts."* / *"Datos duros, con recibo."* Doña Datos queda como segunda opción si quieren algo más emotivo. Antes de imprimir el logo: revisar el dominio, el handle de GitHub y una búsqueda en el registro de marcas de Costa Rica (Registro Nacional) y en USPTO (5 minutos).

---

## 6. Lista corta de acción (para el check-in de hoy a las 9 p. m.)
1. Cambiar el nombre público a "Dato Duro" (o el que decida Abdiel) **antes del jueves**; repo `dato-duro`.
2. Spike P1 de punta a punta antes del jueves a mediodía.
3. Pasar la federación de Zetaris a Josué; Abdiel se queda con datos, front, marca y video.
4. Fiscal Nemotron: una llamada por respuesta, no por frase.
5. Video objetivo de 2:30; deck con la competencia real y el diferenciador "prueba + no sé".
6. Verificar en el PDF de la Fed las cifras 73/54/50 o reemplazarlas por las verificadas aquí.
7. Conseguir una cita real de un dueño de negocio (el amigo) para Impacto.
