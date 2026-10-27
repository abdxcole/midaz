# 14 · Kit para ganar el Open Agent Hackathon 2026 (2026-10-21)

Lo preparó ARGOS para Abdiel y Josué. Leí en modo solo lectura: la página del evento (hackathon.genai.works/event/open-agent-hackathon-2026), la guía de setup (Google Doc), la guía de Zetaris (zetaris.github.io/getting-started), Gmail y la PC de Abdiel.
**(sin verificar)** = no lo pude confirmar en una fuente oficial.

---

## 0. Datos duros (verificados en la página del evento y en la guía)

- **Fechas (hora Costa Rica, UTC-6):**
  - Se abre el build: 21 oct, 6:00 pm
  - **Cierra la inscripción: 22 oct, 5:59 pm** ⚠️ (hay que estar inscritos y con equipo armado)
  - Abre el juzgamiento: 26 oct, 6:00 pm
  - **Cierran las entregas: 27 oct, 5:45 pm (límite duro)**
  - Resultados: 6 nov, 10:00 am
- **Formato:** 100 % en línea. Equipos de 1 a 5. Edad mínima 16. Una sola cuenta por persona: si alguien tiene cuentas duplicadas, **descalifican a todo el equipo**.
- **Inscritos:** ~5.240 personas (dato de hoy). Ojo: son personas, no proyectos entregados.
- **Jueces:** Michael Hay (CTO de **Zetaris**), Michael Armentano (SpaceXAI), Sam Cummings, Shestakov Vladyslav y Remus Ranca (GenAI Works).

### Tracks y premios (en USD)
| Track | Qué piden | Premios |
|---|---|---|
| 01 Solving Fragmented Intelligence | Encontrar fuentes de datos dispersas y trabajar con todas | 1.600 / 1.200 / 900 |
| **02 The Agent That Can Explain Why** | Investigar preguntas complejas en varias fuentes, conectar hallazgos y dar respuestas o recomendaciones **respaldadas con evidencia** | 1.600 / 1.200 / 900 |
| 03 Reasoning Architecture | Convertir datos, conocimiento, memoria y razonamiento en decisiones y acciones confiables | 1.500 / 1.200 / 900 |
| Wildcard [Tinkerer] | Traer un proyecto que ya existe y extenderlo con Zetaris y Meterless. Solo se califica el trabajo nuevo | 1.000 / 600 / 400 |
| Especial: Best use of NVIDIA Nemotron | Usar Nemotron **a través de Meterless Nightshift** en una función que sirva de verdad | NVIDIA DGX Spark (valor 4.699) |

- **"Best use of Cursor-built product":** descartado. Anuncio oficial 2026-10-22: Cursor no da tokens ni créditos y es opcional.
- Según la página, se elige **un** track.

### Cómo califican (100 puntos)
- **Impacto: 30.** Que cumpla el enunciado del reto y resuelva un problema real para usuarios bien definidos.
- **Calidad técnica**, **Creatividad** y **Claridad del demo:** cuánto vale cada uno **(sin verificar)**. La página no muestra esos números. Por descarte, entre los tres suman 50, pero no sé cómo se reparten.
- **Producto y UX: 10.**
- **Sponsor tech: 10.** Cómo se usan Zetaris, Meterless y Nemotron.

### Reglas obligatorias (de la guía de setup)
1. **Data:** usar **Zetaris** sí o sí, corriendo en Docker local. Es "el centro de cada build".
2. **Build:** construir con la herramienta de código que se quiera (**Cursor es opcional**; Claude Code, Windsurf o Copilot valen; **Cursor no da tokens ni créditos** (actualizado 2026-10-22, anuncio oficial)) y meter **al menos un Meterless Engine funcionando de verdad** en el producto: H-MEM (memoria), Markovian (tareas largas en pasos), World Model (estado compartido) o Scout Intent (ruteo por intención). No basta con mencionarlo ni con dejar una dependencia sin usar: tiene que vivir **dentro de una función real de MIDAZ** y probarse con **un test que pase o un demo en vivo**. En MIDAZ: **H-MEM**, ver HU-15 en `docs/06-plan-midas.md`.
3. **Power:** la app tiene que usar **Meterless Nightshift como proveedor principal de IA**. El endpoint es compatible con OpenAI (`/v1/chat/completions`, `/v1/models`, headers `meterless-app` y `meterless-scope: user`). La llave de NVIDIA va en la pestaña Providers de Nightshift, **no en la app**.
4. **Premio NVIDIA:** usar al menos un modelo Nemotron vía Nightshift en un feature real, con evidencia visible de qué modelo respondió. `meterless/auto` puede terminar en otro modelo, así que hay que **fijar un lane Nemotron**.
5. **Qué mostrarle al jurado (según la guía):** la app resolviendo un problema útil, la conexión con Meterless y un request real que pase por Nightshift y vuelva con resultado. Las llaves no se muestran.
6. **Requisitos exactos de la entrega:** la sección 06 de la página está colapsada y no la pude leer **(sin verificar)**. Un blog de terceros (Parsec AI Labs) dice "repo público en GitHub + documentación de arquitectura". Lo normal es pedir además un video demo y una descripción, pero eso hay que confirmarlo en HackOS.
7. **¿Se puede preparar código antes del build?** La guía dice: "Check the event rules on how much project code you may prepare in advance" **(sin verificar)**. Si no está claro, lo seguro es arrancar el repo nuevo **después** de las 6:00 pm de hoy y reusar *ideas y patrones* del proyecto previo de Abdiel, no copiar el repo entero.

### Gmail
Encontré **un solo** correo relacionado: el aviso de Google de que el 19-oct entraste a GenAI.Works con tu cuenta de Google. No hay correos del onboarding de HackOS ni el resumen de HERMES en esta cuenta. El onboarding fue el 21-oct a las 12:00 UTC (6:00 am CR) y está grabado en academy.genai.works.

### PC de Abdiel (revisada solo lectura)
- **RAM:** 31,4 GB. Alcanza: Zetaris pide 8 GB y 4 CPU solo para Docker.
- **CPU:** Ryzen 5 5600G (6 núcleos).
- **Disco C:** 173 GB libres. Pide 15 GB, así que sobra.
- **Docker:** NO está instalado. Hace falta permiso de administrador.
- **WSL:** está instalado. **Falta una distro Ubuntu** para correr los comandos de Zetaris.
- **Git y Python:** sí están.
- **Proyecto previo de Abdiel:** privado, no se comparte aquí. Solo se reusan *ideas y patrones* (orquestador, verificador, control de cupo, memoria), reescritos desde cero.

---

## 1. Track recomendado: **02 · The Agent That Can Explain Why**

**Por qué este:**
1. **Es el que la guía amarra a Zetaris.** Dice literalmente que "Explain Why" es justo para lo que se hizo Zetaris: respuestas basadas en datos gobernados. Uno de los jueces es el CTO de Zetaris. Eso suma en Impacto (30) y en Sponsor tech (10).
2. **Es lo que el proyecto previo de Abdiel ya sabe hacer.** Planear, ejecutar pasos, sintetizar y **verificar** (verificador y revisión). Ustedes ya tienen las mañas de "no inventar y citar la fuente". La mayoría de equipos va a entregar un chat que corre SQL. Ustedes pueden entregar respuestas donde **cada frase trae su recibo**.
3. **La fuerza de Abdiel en diseño se nota.** Un "expediente de evidencia" visual (tarjetas por hallazgo, cadena causa → efecto y botón "ver la prueba") pega en Demo, UX y Creatividad. Track 3 es más abstracto y cuesta más que luzca en un video de 3 minutos.
4. **Competencia (estimado, sin verificar):** Track 1 y Track 2 van a ser los más llenos porque son los más obvios. Aun así, en el 2 el diferenciador (evidencia verificable más diseño) es más claro que en el 1. **No** recomiendo el Wildcard: paga la mitad y solo cuenta el trabajo nuevo.
5. **Es compatible con el premio NVIDIA**, que es aparte y no depende del track. Así se juega por dos premios.

## 2. La idea: **TESTIGO** (en inglés: *Witness — the agent that shows its receipts*)

**En 3 líneas:**
1. Un gerente de operaciones o finanzas le pregunta a TESTIGO "¿por qué pasó X?" (por ejemplo, "¿por qué cayeron las ganancias de tal región en 1996?").
2. TESTIGO investiga en varias fuentes de Zetaris (las tablas TPCH y TPCDS de ejemplo más una API pública registrada como tabla), arma hipótesis y las prueba o descarta con SQL.
3. Entrega un **expediente**: la respuesta y cada afirmación con su consulta, sus filas y un sello de "verificado". Un segundo lane de Nemotron hace de fiscal y vuelve a correr la prueba. Si no hay evidencia, la respuesta dice "no sé".

**Usuario definido** (vale para Impacto): analista u operaciones de una pyme que tiene los datos regados y no tiene equipo de datos.

### Historia del demo (≤3 min, en inglés con subtítulos)
1. **(0:00–0:20) El dolor:** "Los dashboards dicen *qué* pasó, nadie dice *por qué*, y los chatbots inventan."
2. **(0:20–1:30) La investigación en vivo:** se escribe la pregunta. Se ve el plan de hipótesis (H1 precio, H2 proveedor, H3 región, H4 factor externo). Cada paso muestra el SQL que corre en Zetaris y el resultado. H2 se descarta con datos, en pantalla y en rojo.
3. **(1:30–2:10) El expediente:** la respuesta final con 3 hallazgos. Clic en un hallazgo y aparecen la consulta exacta, las filas y la fuente. El sello "Verified by second Nemotron lane" está a la vista.
4. **(2:10–2:35) La memoria:** al día siguiente se pregunta algo relacionado. H-MEM recuerda la investigación anterior y la reusa ("ya sé que el proveedor 12 no es la causa").
5. **(2:35–3:00) Bajo el capó:** Nightshift Console con el lane Nemotron que respondió, la arquitectura en una lámina y las pruebas en verde.

### Arquitectura
```
[UI web: expediente]  (Next.js o Streamlit; Abdiel diseña)
        │
[API Python (FastAPI)]
        │
 ┌──────┴───────────────────────────────────────────┐
 │ Orquestador (patrón del proyecto previo de Abdiel, reescrito limpio)  │
 │  1. Scout Intent → tipo de pregunta (por qué / qué / comparar) │
 │  2. Planner (Nemotron SUPER, lane profundo) → hipótesis │
 │  3. Markovian loop: un paso = 1 hipótesis → SQL → filas → resumen corto │
 │     (el contexto entre pasos va acotado)          │
 │  4. Fiscal (Nemotron lane rápido) → re-ejecuta SQL y revisa que cada frase tenga evidencia │
 │  5. Síntesis → expediente JSON {claim, sql, rows, source, verdict} │
 │  6. H-MEM → guarda los hallazgos para la próxima sesión │
 └──────┬──────────────────────────┬────────────────┘
        │                          │
 Zetaris REST :8888/api/v1.0   Meterless Nightshift (OpenAI-compat)
 POST /sql-editor/sqls/run     lanes: nemotron-3.5-lightning (rápido), nemotron-3-super (profundo)
 (TPCH, TPCDS, NY Taxi + 1 API REST pública como tabla Lightning)
```
- **Engines Meterless:** mínimo **H-MEM**, ideal también **Markovian**. Scout Intent queda opcional. Cada uno con su prueba de conformidad corriendo.
- **Ahorro de cupo NVIDIA (~400 req/día compartidos):**
  - caché de respuestas por hash del prompt
  - SQL determinístico donde se pueda
  - modo `--replay` para ensayar el demo sin gastar
  - presupuesto aproximado de 8–12 llamadas por investigación
  - poner un tope diario en `costos.py`, al estilo del proyecto previo de Abdiel
  - (Los nombres exactos de modelos están **sin verificar**: hay que copiarlos del catálogo de Nightshift.)

---

## 3. Plan de 6 días (hora CR)

| Día | Abdiel | Josué |
|---|---|---|
| **Mié 21 (hoy, noche)** | Docker Desktop (admin) + Ubuntu WSL + registro en Zetaris Cloud. Arrancar `docker compose pull` (30–45 min) | Instalar Nightshift, crear la llave en build.nvidia.com, ponerla en Providers, crear el lane Nemotron y probarlo |
| **Jue 22** (inscripción cierra 5:59 pm) | Confirmar que el **equipo está armado en HackOS**. `verify.sh` + Pikachu OK. Crear la API key de Zetaris. Bocetos de la UI del expediente | Repo nuevo y público (`testigo`) con `.gitignore` de `.env`. `smoke_test.py` con 3 PASS. Prompt POWER "Add Meterless as a provider" |
| **Vie 23** | Elegir el caso del demo y las preguntas buenas en TPCH/TPCDS. Registrar 1 API REST pública en Zetaris | Loop del agente: planner → SQL → fiscal → expediente JSON. Engine **Markovian** con su prueba |
| **Sáb 24** | UI: expediente, tarjetas y "ver prueba". Identidad visual y logo | Engine **H-MEM** con su prueba. Caché y tope de cupo. Logs de qué modelo respondió |
| **Dom 25** | Integrar UI y API. Guion del demo. Diagrama de arquitectura | Tests (pytest) y manejo de errores (Zetaris caído, 429 de NVIDIA). Modo replay |
| **Lun 26** | Grabar el video (2 tomas) y escribir el README con capturas | Congelar el código. Revisión de secretos (`git log`, que no haya llaves). Instrucciones de instalación probadas desde cero |
| **Mar 27** | **Entregar antes del mediodía** (el límite es 5:45 pm; no apostar a la última hora). Revisar que los links abran | Respaldo: release o tag del repo y probar el clone limpio |

## 4. Checklist de entrega
- [ ] Equipo inscrito en HackOS con las 2 cuentas, **antes del 22-oct 5:59 pm CR**. Una cuenta por persona.
- [ ] Track 02 seleccionado.
- [ ] Repo público en GitHub (**sin verificar** que lo pidan, pero seguro sí) con README: problema, usuario, cómo correrlo, arquitectura, engines y dónde están en el código.
- [ ] Evidencia de **Zetaris**: SQL por REST, captura y logs.
- [ ] Evidencia del **Meterless Engine**: nombre, qué hace, ruta en el código y prueba en verde.
- [ ] Evidencia de **Nightshift como proveedor principal**: captura de la Console (sin el token) y un request real.
- [ ] Evidencia de **Nemotron** para NVIDIA: run details o logs de Nightshift con el nombre del modelo.
- [ ] (Opcional) Mención de la herramienta de código usada (Cursor no es obligatorio): cómo se construyó (Composer/Grok). Si existe el premio Cursor (sin verificar), agregar capturas o commits del proceso.
- [ ] Video demo (formato y duración **sin verificar**; apuntar a 3 min o menos).
- [ ] Sin llaves en el repo ni en el video.
- [ ] Revisar la sección 06 de las reglas en HackOS y ajustar esta lista.

## 5. Mapa contra los criterios
| Criterio | Cómo lo atacamos |
|---|---|
| Impacto (30) | Usuario concreto (pyme sin equipo de datos). Pregunta "¿por qué?" que hoy cuesta días. Calza exacto con el texto del Track 2 |
| Calidad técnica | Orquestador probado, fiscal que re-ejecuta SQL, pruebas, manejo de errores y caché |
| Creatividad | "Recibos por frase" y un fiscal que puede tumbar hipótesis en vivo |
| Claridad del demo | Historia de 3 min con un momento "aha" (H2 descartada en rojo) |
| Producto/UX (10) | Expediente visual hecho por Abdiel, legible para alguien no técnico |
| Sponsor tech (10) | Zetaris en el centro (varias fuentes + REST API como tabla), 2 engines Meterless, 2 lanes Nemotron vía Nightshift |

## 6. Riesgos
1. **Docker y Zetaris no levantan** (admin, WSL o registro). Plan B: Zetaris en AWS; la guía estima ~US$1 por 8 h **(sin verificar el costo real)**. Hacerlo HOY.
2. **Cupo NVIDIA de ~400 por día compartido con el otro proyecto.** Pausar el otro proyecto durante la semana, usar caché y replay, y que el lane rápido haga casi todo.
3. **Reglas sobre código previo:** repo nuevo, sin copiar archivos privados ni las personalidades, y commits desde el 21-oct a las 6 pm.
4. **Que `meterless/auto` caiga en un modelo no Nemotron:** fijar el lane y guardar la evidencia.
5. **Fuga de secretos:** `.env` en `.gitignore`, `git log -p` antes de publicar y nada de llaves en capturas.
6. **El demo depende de los servicios en vivo:** grabar con tiempo y tener el modo replay.
7. **Alcance:** si el jueves en la noche no hay `smoke_test` con 3 PASS, recortar el UI fancy y priorizar el expediente simple.

## 7. Pendiente de verificar (en HackOS o academy)
- Sección 06 "Submission requirements" (video, repo, formato).
- Cuánto vale cada uno de: calidad técnica, creatividad y demo.
- ~~Premio de Cursor~~: resuelto 2026-10-22 (Cursor opcional, sin créditos).
- Cuánto código previo se permite.
- Nombres exactos de los modelos Nemotron en Nightshift.
- Fecha de los workshops de vibe coding (la guía dice "[Organisers: add…]").
