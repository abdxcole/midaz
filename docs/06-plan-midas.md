# 19 - Plan de ejecución MIDAZ (Scrum, 3 sprints) — 2026-10-21

> **MIDAZ — Turn your data into gold.** Open Agent Hackathon 2026, Track 02 "The Agent That Can Explain Why".
> Fuente única: `15-BRIEF-MIDAZ-2026-10-21.md` (versión enviada a Claude). Todo lo que no está en el brief va marcado **(sin verificar)** o **(propuesta)**.
> Todas las horas son de Costa Rica (CR). Equipo: **Abdiel** (diseño, marca, datos, front, narrativa y orquestación) y **Josué** (desarrollo, agente y federación de Zetaris).

---

## 0. Reglas del plan

1. **La meta que manda:** la pregunta del 80/20 de ganancia de punta a punta (CSV → Zetaris → SQL → Nemotron por Nightshift → respuesta con recibo) **antes del jueves 22 a las 12:00**. Si no corre, ese mismo día se decide el plan B (sección 6).
2. **Toda cifra sale de Zetaris.** El modelo nunca calcula: redacta a partir de filas. El chequeo de números en código corre siempre; el verificador Nemotron corre **una vez por respuesta**.
3. **"No sé" lo decide el código**, no el modelo: si la consulta devuelve costo vacío o no hay filas, la respuesta es "no sé" + qué dato falta.
4. **Nada público dice "Jarvis".** Nada de llaves en repo, video ni capturas. Datos siempre rotulados **"Sample data"**.
5. **Lo que no está terminado al cierre de un sprint no se arrastra en silencio:** se re-prioriza o va a la lista de recortes (sección 7).
6. **Dormir es parte del plan.** Mínimo 6 h por noche cada uno; la noche del miércoles es la única en la que se puede estirar un poco.

### 0.1 Ritmo diario (igual todos los días)

| Hora | Qué | Duración | Formato |
|---|---|---|---|
| 8:30 AM | **Daily corto** (3 preguntas: ¿qué terminé?, ¿qué hago hoy?, ¿qué me bloquea?) | 10 min | Mensaje de texto o llamada |
| 9:00 PM | **Checkpoint**: demo de lo hecho en pantalla, revisar portón del día, mover tarjetas, decidir recortes | 20-30 min | Llamada con pantalla compartida |

Horario de disponibilidad de cada uno (clases, trabajo): **(sin verificar)** — confirmarlo en el arranque del miércoles y ajustar estas horas.

### 0.2 Cortes de sprint

El brief dice "21-23", "23-25" y "25-27": los días de borde se comparten. Para que no haya dudas, los sprints se cortan al mediodía:

| Sprint | Desde | Hasta | Revisión + retro + planificación |
|---|---|---|---|
| **Sprint 1** — Base técnica + 80/20 de punta a punta | Mié 21, 6:00 PM | Vie 23, 1:00 PM | Vie 23, 12:00-1:00 PM |
| **Sprint 2** — Confianza + memoria + conversación | Vie 23, 1:00 PM | Dom 25, 1:00 PM | Dom 25, 12:00-1:00 PM |
| **Sprint 3** — Pulido, demo, video, deck y entrega | Dom 25, 1:00 PM | **Mar 27, 12:00 PM (meta)** / 5:45 PM (límite) | Mar 27, después de entregar |

### 0.3 Definición de "terminado" (vale para todas las historias)

- Corre en la máquina de demo con datos de Zetaris (no con datos pegados en el código).
- Cada frase con número tiene recibo: SQL exacta, vista de origen, filas, hora.
- Está en el repo público (`main`), sin llaves, con commit después del 21-oct 6:00 PM.
- El otro miembro del equipo lo vio funcionar en el checkpoint de las 9:00 PM.
- Si toca al agente: no rompe `golden.yaml` (desde que exista).

---

## 1. Fases hasta el objetivo final

**Objetivo final: ganar el Track 02.** Cada fase termina en un portón: **seguir** o **cambiar al plan B**.

| Fase | Cuándo | Qué se logra | Portón (seguir / plan B) |
|---|---|---|---|
| **F0 Arranque** | Mié 21, 6:00 PM-medianoche | Docker+Zetaris arriba, Nightshift responde con Nemotron, repo creado, datos mínimos a mano | **P0 — Mié 9:00 PM:** ¿Zetaris contesta un `SELECT` por REST? ¿Nightshift contesta con lane Nemotron? Si alguno no: se trabaja de noche en eso y nada más. |
| **F1 Columna vertebral** | Jue 22, mañana | 80/20 de ganancia de punta a punta con recibo (sin front) | **P1 — Jue 12:00 (portón del brief):** si no corre → plan B (6.1) decidido antes de las 3:00 PM. |
| **F2 Datos y federación** | Jue 22 tarde-Vie 23 mediodía | Inscripción, 3 fuentes federadas, datos finales, vista `margen_por_producto` | **Cierre Sprint 1 — Vie 1:00 PM:** P1 corre sobre las 3 fuentes y datos finales. Si no: plan B (6.2). |
| **F3 Confianza** | Vie 23 tarde-Sáb 24 | "¿Me alcanza?", "no sé", verificador, H-MEM, chat | **P2 — Sáb 9:00 PM:** las 3 preguntas responden en el chat. Si no: recortes nivel 1 (sección 7). |
| **F4 Congelar funciones** | Dom 25 mañana | `golden.yaml` con métrica real, front conectado | **Cierre Sprint 2 — Dom 1:00 PM:** desde aquí **no entra ninguna función nueva**, solo arreglos. |
| **F5 Demo y narrativa** | Dom 25 tarde-Lun 26 | Replay, `DEMO.md`, guion, grabación, video, deck, README | **P3 — Lun 12:00:** congelar código. **P4 — Lun 9:00 PM:** video v1 completo. Si no: recortes nivel 2. |
| **F6 Entrega** | Mar 27 | Tag, clone limpio, subir video, entregar | **P5 — Mar 12:00:** entregado. 12:00-5:45 PM es colchón, no tiempo de trabajo. |

---

## 2. Sprint 1 — Base técnica y 80/20 de punta a punta

**Mié 21, 6:00 PM → Vie 23, 1:00 PM**

### 2.1 Objetivo del sprint
"Doña Marta pregunta qué productos le dan la plata y MIDAZ responde con el 80/20 de **ganancia** (no de volumen), sacado de 3 fuentes federadas en Zetaris, con recibo SQL y el modelo Nemotron vía Nightshift."

### 2.2 Backlog (historias de usuario)

| ID | Historia | Dueño | Prioridad |
|---|---|---|---|
| HU-00 | Como equipo, tenemos Docker + WSL + Zetaris corriendo y contestando por REST (`POST /api/v1.0/sql-editor/sqls/run` en :8888, según el kit). | Abdiel instala, Josué conecta | Debe |
| HU-01 | Como equipo, llamamos a Nemotron por Meterless Nightshift con lane fijo (nunca `meterless/auto`), con la llave NVIDIA solo en Providers. | Josué | Debe |
| HU-02 | Como dueña, pregunto "¿Qué productos me dan la plata?" y recibo 2-3 frases: qué 20 % de productos hace el 80 % de la ganancia bruta, con el contraste por volumen (arroz vs helado). | Josué (agente) + Abdiel (SQL y texto) | Debe |
| HU-03 | Como juez, debajo de cada frase con número veo el recibo: SQL exacta, vista de origen, filas y hora. | Josué | Debe |
| HU-04 | Como equipo, los datos de ejemplo viven en **3 fuentes separadas** (ventas POS / costos+inventario / gastos operativos) federadas en Zetaris, con la vista `margen_por_producto`. | Josué | Debe |
| HU-05 | Como equipo, tenemos un generador de datos de ejemplo de minisúper rotulado "Sample data" que incluye los casos del demo (ver 2.3). | Abdiel | Debe |
| HU-06 | Como equipo, el repo es público, nuevo, con `.env.example`, `.gitignore` y sin llaves. | Josué | Debe |
| HU-07 | Como equipo, estamos inscritos en HackOS antes del jue 22, 5:59 PM. | Abdiel | Debe |
| HU-08 | Como marca, sabemos si "MIDAZ" está libre en software (USPTO + Registro Nacional CR). | Abdiel | Debería |

### 2.3 Lo que los datos tienen que traer sí o sí (para que las 3 escenas funcionen)
Esto no está escrito en el brief pero lo exige el guion (sección 6 del brief):
- **Arroz y frijoles:** muchas unidades, margen bajo → #1 en ventas, abajo en ganancia.
- **Helado y Coca-Cola:** menos unidades, margen alto.
- **Carne con ventas pero sin costo** en la fuente de costos → dispara el "no sé".
- **Un cambio de precio de la Coca-Cola en una fecha concreta**, con ventas antes y después → la escena de memoria ("¿Cómo me fue con lo de la Coca?") necesita esos datos en Zetaris; H-MEM solo guarda la decisión y la fecha.
- **Gastos operativos del mes** (planilla de 4 empleados, alquiler, luz) un poco **por encima** de la ganancia bruta → la escena "¿me alcanza?" muestra un faltante.
- Precios en colones **con IVA incluido** (el cálculo lo excluye).
- Tamaño: **(propuesta)** 150-300 productos y 90 días de ventas. Es la pregunta abierta 4 del brief: decidir en el checkpoint del jueves. El persona tiene ~1.200 productos; el demo no lo necesita.
- Frase honesta para README y video: "patrones de margen inspirados en datos públicos de precios" (p. ej. los rangos de Konkurransetilsynet del brief).

### 2.4 Criterios de "terminado" del sprint
- [ ] Pregunta 1 corre de punta a punta **sobre las 3 fuentes federadas y los datos finales**, no sobre un CSV suelto.
- [ ] El resultado del 80/20 coincide con el cálculo a mano de Abdiel en la hoja de control (ver HU-05).
- [ ] El recibo muestra SQL, vista, filas y hora; el receipt de Nightshift muestra el nombre del modelo.
- [ ] Repo público con commits del equipo, sin llaves.
- [ ] Inscripción en HackOS confirmada (captura).
- [ ] Nombres exactos de los modelos Nemotron copiados del catálogo de Nightshift (pregunta abierta 2).

### 2.5 Tareas por persona

**Abdiel**
- Mié: instalar Docker + WSL + Zetaris en la PC de Abdiel; probar un `SELECT 1` por REST.
- Mié: CSV mínimo **a mano** (~20 productos, 1 mes) con arroz, frijoles, helado, Coca y carne, para el portón del jueves. El generador va después.
- Mié: chequeo de marca MIDAZ (5 min) y anotar resultado.
- Jue mañana: escribir y validar a mano la SQL del 80/20 (orden por ganancia, acumulado, corte en 80 %) en una hoja de control.
- Jue: inscribir al equipo en HackOS (**meta 2:00 PM**, no esperar a las 5:59).
- Jue tarde-Vie mañana: esquema de las 3 fuentes + generador de datos.
- Vie mañana: datos finales cargados; hoja de "respuestas esperadas a mano" para P1 y P2.
- Orquestación: llevar el tablero, conducir daily y checkpoint, cronometrar el portón.

**Josué**
- Mié: Nightshift + llave NVIDIA en Providers + lane Nemotron probado; anotar nombres exactos.
- Mié: crear repo público (esqueleto API, `.env.example`, `.gitignore`).
- Mié noche-Jue mañana: conectar a Zetaris por REST; tubería del agente: pregunta → plantilla SQL del 80/20 → Zetaris → filas → Nemotron redacta → recibo (por consola/JSON, sin front).
- Jue tarde: federación de las 3 fuentes en Zetaris (**(propuesta)** ventas en Postgres, costos y gastos en CSV — el brief menciona "Postgres+CSV" como incógnita).
- Vie mañana: vista semántica `margen_por_producto`; P1 corriendo sobre los datos finales.

### 2.6 Riesgos del sprint

| Riesgo | Señal temprana | Respuesta |
|---|---|---|
| REST de Zetaris no responde como dice el kit | Mié 9:00 PM sin `SELECT` | Leer docs del kit esa noche; si al jue 9:00 AM sigue igual, plan B 6.1 |
| Josué no puede llegar a Zetaris que corre en la PC de Abdiel | Mié 9:00 PM | **(sin verificar)** ¿misma red, acceso remoto o Zetaris también en la máquina de Josué? Decidirlo en el arranque |
| Federación Postgres+CSV no soportada localmente | Jue 6:00 PM | Cargar las 3 fuentes como fuentes separadas del tipo que sí funcione, pero **mantener 3 fuentes** |
| Capa semántica local no existe o no anda | Vie 9:00 AM | Vista SQL normal llamada `margen_por_producto` |
| Nombres de modelo distintos / lane no disponible | Mié 9:00 PM | Otro Nemotron del catálogo; nunca `meterless/auto` |
| Inscripción olvidada | — | Hecha antes de las 2:00 PM del jueves |

### 2.7 Revisión y retro (Vie 23, 12:00-1:00 PM)
- **Revisión (30 min):** Josué corre P1 en vivo; Abdiel compara contra la hoja a mano. Se marca cada criterio de 2.4.
- **Retro (15 min):** ¿qué nos frenó?, ¿qué repetimos?, ¿una cosa que cambiamos para el Sprint 2?
- **Planificación S2 (15 min):** confirmar backlog de la sección 3 y mover recortes si hace falta.

---

## 3. Sprint 2 — Verificación, "no sé", memoria y conversación

**Vie 23, 1:00 PM → Dom 25, 1:00 PM**

### 3.1 Objetivo del sprint
"MIDAZ responde las 3 preguntas del MVP en un chat simple, cada frase con prueba, quita lo que no tiene evidencia, dice 'no sé' cuando falta el dato y recuerda decisiones del dueño. Y lo demostramos con una métrica real de `golden.yaml`."

### 3.2 Backlog (historias de usuario)

| ID | Historia | Dueño | Prioridad |
|---|---|---|---|
| HU-10 | Como dueña, pregunto "¿Me alcanza este mes?" y veo ganancia bruta vs gastos operativos, el faltante y el punto de equilibrio (gastos / margen % promedio). | Josué + Abdiel (SQL a mano) | Debe |
| HU-11 | Como dueña, pido una sugerencia de precio y veo el cálculo con supuestos en una caja: (precio nuevo − costo) × unidades estimadas; la caída de unidades la elijo yo; **IVA fuera, dicho en pantalla**; siempre es sugerencia. | Josué + Abdiel (texto) | Debe |
| HU-12 | Como dueña, pregunto "¿Cuánto gano con la carne?" y MIDAZ dice "No sé: no tengo el costo de la carne." (decidido en código). | Josué | Debe |
| HU-13 | Como dueña, cualquier frase sin evidencia se elimina: chequeo de números en código **siempre** + verificador Nemotron **una llamada por respuesta**. En pantalla, la frase tachada en rojo. | Josué (lógica) + Abdiel (cómo se ve) | Debe |
| HU-14 | Como dueña, pregunto "¿Cómo me fue con lo de la Coca?" y MIDAZ recuerda la decisión (H-MEM de Meterless) y responde con datos de Zetaris antes/después. | Josué | Debe |
| HU-15 | **Requisito central del hackathon.** Como juez, veo un Meterless Engine (**H-MEM**) funcionando **dentro de una función real de MIDAZ** (la memoria de decisiones del dueño que usa HU-14), probado con un test que pasa en `python run.py test` y en el demo en vivo. Criterios en 3.2.1. | Josué (motor) + Abdiel (escena del demo) | **Debe (no se recorta)** |
| HU-16 | Como dueña, uso un chat web mínimo: **modo dueño** (2-3 frases + sello "verificado") y **modo juez** ("bajo el capó": SQL, filas, receipts) en la misma pantalla. | Abdiel | Debe |
| HU-17 | Como equipo, caché de respuestas y tope de cupo para no pasar las ~400 solicitudes/día. | Josué | Debe |
| HU-18 | Como juez, `golden.yaml` con 15 preguntas y su resultado real: "X/15 correctas, 0 números inventados, N/N 'no sé' correctos". | Josué (runner) + Abdiel (respuestas esperadas) | Debe |
| HU-19 | Como juez de Impacto, hay una cita o audio de 10 s de un dueño real (con permiso) o 3-5 frases textuales de entrevistas. | Abdiel | Debería |
| HU-20 | "Por qué" con hipótesis múltiples. | Josué | Solo si todo lo anterior está listo el domingo |

### 3.2.1 HU-15 - Meterless Engine dentro de MIDAZ (criterios de aceptación)

Anuncio oficial (Discord, 2026-10-22): hay que implementar **al menos un** Meterless Engine (H-MEM, Markovian, World Model o Scout Intent) **dentro de una función real** y probarlo con un test que pase o un demo en vivo. Mencionarlo o dejar una dependencia sin usar **no cuenta**.

**Motor elegido: H-MEM.** Por qué: MIDAZ necesita memoria persistente del negocio (decisiones del dueño: "subí la Coca", "dejé de traer X") para responder "¿cómo me fue con...?" con datos antes/después. H-MEM exige `source` y `provenance` en cada recuerdo, igual que nuestro recibo SQL. Scout Intent (ruteo por intención de la pregunta) queda como segundo motor **solo si sobra tiempo** en Sprint 2; hoy el ruteo es por plantillas.

- [ ] `midas/memory.py` (nombre propuesto) usa H-MEM de verdad para **guardar** y **recuperar** decisiones; nada de un dict propio con el nombre "H-MEM".
- [ ] La función de respuesta de HU-14 lee la memoria por ese módulo: si se quita H-MEM, HU-14 deja de funcionar (no es dependencia decorativa).
- [ ] Cada recuerdo lleva `source` (pregunta/turno) y `provenance` (recibo SQL o mensaje del dueño); uno sin fuente se rechaza.
- [ ] La memoria sobrevive entre sesiones (reiniciar el proceso y seguir recordando).
- [ ] Test nuevo `tests/test_hmem.py` dentro de la suite existente: `python run.py test` pasa con él. Casos mínimos: (1) guardar la decisión de la Coca y recuperarla en otra instancia; (2) rechazar un recuerdo sin `source`/`provenance`; (3) la respuesta de HU-14 cita el recuerdo y el recibo antes/después. Si Meterless trae conformance suite de H-MEM, también se corre y se anota el resultado.
- [ ] Demo en vivo: escena C del video muestra la memoria respondiendo y la terminal con `python run.py test` en verde.
- [ ] README: sección "Meterless Engine" con nombre, qué hace, ruta en el código y cómo correr el test.
- Paquete/API exacto de H-MEM: **(sin verificar)**, confirmar en https://github.com/Meterless/Meterless/tree/main/engines/hmem al inicio de Sprint 2. Si no se puede integrar, plan B: Scout Intent sobre la clasificación de preguntas con la misma regla (función real + test).

**(Propuesta) reparto de las 15 preguntas de `golden.yaml`:** 5 de 80/20 (variantes de redacción), 4 de "¿me alcanza?"/precio, 3 de "no sé" (carne y otros datos faltantes), 3 de memoria. Las respuestas esperadas salen de la hoja a mano de Abdiel, no del propio agente.

### 3.3 Criterios de "terminado" del sprint
- [ ] Las 3 preguntas del MVP responden en el chat web con datos de Zetaris.
- [ ] El "no sé" de la carne sale siempre, y nunca aparece un número de la carne.
- [ ] Se ve al menos un caso real del verificador quitando una frase (para la escena A del video).
- [ ] HU-15 cumplida: H-MEM dentro de la función de memoria, recuerda la Coca entre sesiones y `tests/test_hmem.py` pasa en `python run.py test`.
- [ ] `golden.yaml` corre de un comando y da una cifra real (la que salga; no se maquilla).
- [ ] Caché activa y contador de solicitudes del día visible en el log.
- [ ] Modo dueño / modo juez funcionan en la misma pantalla.

### 3.4 Tareas por persona

**Abdiel**
- Vie tarde: diseño de la conversación (tono de 2-3 frases, cómo se dice "no sé", cómo se ve el sello y el recibo). Wireframe rápido.
- Vie (o jue): entrevistas a 3-5 dueños de pulpería/soda, o el audio del amigo dueño. Pedir permiso por escrito para usar la frase.
- Vie: respuestas esperadas a mano de P2 y de las 15 preguntas de `golden.yaml`.
- Sáb: front — chat + recibo + modo dueño/juez + marca MIDAZ (logo solo si la marca está libre).
- Dom mañana: conectar front a la API, revisar en móvil y en laptop.

**Josué**
- Vie tarde: P2 ("¿me alcanza?" + precio) y "no sé" en código; verificador una vez por respuesta; chequeo numérico en código que compara cada número contra las filas.
- Sáb: H-MEM + pruebas; caché y tope de cupo.
- Dom mañana: runner de `golden.yaml` y primera métrica real.

### 3.5 Riesgos del sprint

| Riesgo | Respuesta |
|---|---|
| Paquete H-MEM no instala o no se entiende (incógnita del brief) | Si al sáb 9:00 PM no corre: Plan B 6.3 |
| El verificador nunca quita nada (no hay momento para el video) | Pregunta del guion donde el borrador incluye algo sin filas; registrar el caso real, no fabricarlo a mano |
| El modelo inventa un número | El chequeo en código lo bloquea; si pasa en `golden.yaml`, se reporta tal cual y se corrige el prompt/plantilla |
| Cupo NVIDIA agotado | Caché; correr `golden.yaml` completo máximo 3 veces/día; trabajar el front con respuestas guardadas |
| Front se come el sábado | Chat sin adornos: lista de mensajes + caja de recibo. El diseño fino va al video, no al código |

### 3.6 Revisión y retro (Dom 25, 12:00-1:00 PM)
- **Revisión:** correr las 3 preguntas en el chat + `golden.yaml` en vivo; anotar la cifra real.
- **Decisión de alcance (portón F4):** lo que no está terminado entra a la lista de recortes. **Desde la 1:00 PM no entra ninguna función nueva.**
- **Retro (15 min)** y planificación del Sprint 3.

---

## 4. Sprint 3 — Pulido, demo, video, presentación y entrega

**Dom 25, 1:00 PM → Mar 27, 12:00 PM (meta) / 5:45 PM (límite)**

### 4.1 Objetivo del sprint
"Un juez entiende MIDAZ en 2:30 de video, lo puede correr en 60 s con `DEMO.md`, y encuentra en el README y el deck cómo usamos Zetaris, Meterless y NVIDIA. Entregado antes del mediodía del martes."

### 4.2 Backlog (historias de usuario)

| ID | Historia | Dueño | Prioridad |
|---|---|---|---|
| HU-30 | Como juez, corro `DEMO.md` en 60 s con un comando y `MODO=replay` (respuestas grabadas, sin gastar cupo). | Josué | Debe |
| HU-31 | Como juez, veo un video de ~2:30 (máx. 3:00), en inglés con subtítulos en español, con las 3 escenas del brief. | Abdiel | Debe |
| HU-32 | Como juez, veo un deck con lo que no entra en el video (fuentes de las cifras, competencia, arquitectura, visión). | Abdiel | Debe |
| HU-33 | Como juez, el README explica el uso de Zetaris, Meterless (incluye el engine de HU-15) y NVIDIA, con resumen en español. | Josué (técnico) + Abdiel (visual) | Debe |
| HU-34 | Como juez, hay un diagrama: 3 fuentes → Zetaris → agente → Nightshift (lane Nemotron) → verificador → respuesta con recibo. | Abdiel | Debe |
| HU-35 | Como equipo, el repo instala desde cero en una carpeta limpia y no tiene llaves (revisión de secretos). | Josué | Debe |
| HU-36 | Como equipo, hay tag/release y un clone limpio probado. | Josué | Debe |
| HU-37 | Voz (hablarle a MIDAZ). | Abdiel/Josué | **Primero en recortarse**; solo si sobra tiempo el domingo |

### 4.3 Criterios de "terminado" del sprint (= checklist de entrega, sección 9)
- [ ] Video subido, 1-4 min (meta ~2:30), con "Sample data" visible y cifras tomadas de Zetaris el día de la grabación.
- [ ] Deck exportado.
- [ ] Repo público con README, `DEMO.md`, `golden.yaml`, tag de release.
- [ ] Entrega hecha y confirmada (captura) antes del mar 27, 12:00 PM.

### 4.4 Tareas por persona

**Abdiel**
- Dom tarde: guion ~2:30 por escenas (sección 6 del brief) + storyboard + diagrama.
- Dom noche: lista de tomas de pantalla con la pregunta exacta de cada escena.
- Lun mañana: grabar pantallas **con datos en vivo de Zetaris**; anotar las cifras en ₡ que salgan (son las del video y del cierre).
- Lun tarde: edición, subtítulos en español, cierre "MIDAZ. Turn your data into gold. Stop deciding blind."; deck; parte visual del README.
- Mar mañana: revisión final del video con ojos frescos; subir.

**Josué**
- Dom tarde: modo replay (grabar las respuestas del guion **el mismo día de la grabación**, para que los números coincidan) + `DEMO.md`.
- Lun antes de 12:00: arreglos de bugs vistos en la grabación; **congelar código a las 12:00**.
- Lun tarde: revisión de secretos (historial incluido), instalación desde cero, README técnico (sección por sponsor), métrica final de `golden.yaml` pegada en el README.
- Mar mañana: tag/release, clone limpio, prueba de `DEMO.md` siguiendo el texto al pie de la letra.

### 4.5 Riesgos del sprint

| Riesgo | Respuesta |
|---|---|
| Video se alarga | Cortar a 3 escenas; todo lo demás va al deck (regla del brief) |
| Números del video no coinciden con replay/README | Grabar replay y video el mismo día; una sola corrida de referencia |
| Una llave aparece en una captura o en el historial | Revisión de secretos antes de subir; rotar la llave en Nightshift si aparece |
| Algo se rompe el martes | Nada de cambios de código el martes salvo que algo esté roto; entregar lo que hay al mediodía |

### 4.6 Revisión y retro (Mar 27, después de entregar)
- **Revisión:** ver el video completo como si fuéramos jueces, con la rúbrica al lado (sección 10).
- **Retro:** qué nos llevamos para el próximo hackathon; guardarlo en docs/.

---

## 5. Plan diario

### Mié 21 (6:00 PM-medianoche) — Sprint 1, Fase F0

| | Abdiel | Josué |
|---|---|---|
| 6:00-6:30 | **Arranque juntos:** leer el plan, confirmar horarios, decidir cómo llega Josué a Zetaris (sin verificar), crear tablero | igual |
| 6:30-9:00 | Docker + WSL + Zetaris; `SELECT 1` por REST; chequeo de marca MIDAZ | Nightshift + llave en Providers + lane Nemotron; anotar nombres de modelo; repo público con esqueleto |
| **9:00 PM** | **Checkpoint P0:** ¿Zetaris contesta? ¿Nightshift contesta con Nemotron? ¿Repo creado? | |
| 9:30-medianoche | CSV mínimo a mano (~20 productos) con los casos de 2.3; cargarlo en Zetaris | Conectar al REST de Zetaris; primera consulta desde el código |

**Daily del jueves (8:30 AM):** ¿qué falta para el portón de las 12:00?

### Jue 22 — Sprint 1, Fases F1 y F2 · **Portón P1 a las 12:00 · Inscripción antes de 5:59 PM**

| | Abdiel | Josué |
|---|---|---|
| Mañana | SQL del 80/20 validada a mano; texto de ejemplo de respuesta en 2-3 frases | Tubería P1: pregunta → SQL → Zetaris → Nemotron → recibo |
| **12:00** | **PORTÓN P1** juntos: ¿corre de punta a punta? Si no → plan B 6.1, decidido antes de las 3:00 PM | |
| Tarde | **Inscripción HackOS (meta 2:00 PM)**; esquema de las 3 fuentes; generador de datos | Repo público al día; federación de las 3 fuentes en Zetaris |
| **9:00 PM** | Checkpoint: ¿3 fuentes registradas en Zetaris? ¿Generador produce los casos de 2.3? Decidir tamaño del dataset | |

### Vie 23 — Cierre Sprint 1 (1:00 PM) e inicio Sprint 2

| | Abdiel | Josué |
|---|---|---|
| Mañana | Datos finales cargados; hoja de respuestas esperadas a mano | Vista `margen_por_producto`; P1 sobre los datos finales |
| **12:00-1:00** | **Revisión + retro Sprint 1 + planificación Sprint 2** | |
| Tarde | Entrevistas a dueños / audio del amigo; diseño de la conversación y del recibo | P2 + "no sé" en código; verificador una vez por respuesta; chequeo numérico |
| **9:00 PM** | Checkpoint: ¿P2 y "no sé" corren por consola? ¿Hay al menos una frase quitada por el verificador? | |

### Sáb 24 — Sprint 2, Fase F3 · **Portón P2 a las 9:00 PM**

| | Abdiel | Josué |
|---|---|---|
| Día | Front: chat + recibo + modo dueño/juez + marca | H-MEM + pruebas; caché y tope de cupo |
| **9:00 PM** | **PORTÓN P2:** ¿las 3 preguntas responden en el chat? ¿H-MEM corre? Si no → recortes nivel 1 y plan B 6.3 | |

### Dom 25 — Cierre Sprint 2 (1:00 PM) e inicio Sprint 3

| | Abdiel | Josué |
|---|---|---|
| Mañana | Conectar y pulir el front; las 15 preguntas de `golden.yaml` con su respuesta esperada | Runner de `golden.yaml`; primera métrica real |
| **12:00-1:00** | **Revisión + retro Sprint 2. Congelar funciones.** | |
| Tarde | Guion ~2:30, storyboard, diagrama; voz solo si sobra | Modo replay + `DEMO.md`; arreglos |
| **9:00 PM** | Checkpoint: guion aprobado por los dos; replay corre | |

### Lun 26 — Sprint 3, Fase F5 · **Congelar código 12:00 · Video v1 a las 9:00 PM**

| | Abdiel | Josué |
|---|---|---|
| Mañana | Grabar pantallas con datos en vivo; anotar cifras en ₡ | Arreglos de lo que salga en la grabación; grabar replay ese mismo día |
| **12:00** | **PORTÓN P3: congelar código** | |
| Tarde | Edición del video, subtítulos, deck, README visual | Revisión de secretos, instalación desde cero, README técnico, métrica final |
| **9:00 PM** | **PORTÓN P4:** ver video v1 completo juntos con la rúbrica. Si no está → recortes nivel 2 | |

### Mar 27 — Entrega · **Meta 12:00 PM · Límite 5:45 PM**

| | Abdiel | Josué |
|---|---|---|
| 8:30 | Daily: ¿qué falta del checklist? | |
| 8:30-10:30 | Últimos ajustes de video y deck (solo texto y cortes) | Tag/release; clone limpio; probar `DEMO.md` al pie de la letra |
| 10:30-12:00 | Subir video, deck, enlaces; **entregar**; captura de confirmación | Revisar que el repo público se ve bien sin sesión iniciada |
| 12:00-5:45 PM | Colchón. Solo se toca algo si está roto. | |

---

## 6. Plan B por portón

### 6.1 Si el 80/20 no corre el jueves a las 12:00
Decidir antes de las 3:00 PM según dónde falló (Zetaris y Meterless son obligatorios, así que el plan B **no** los quita, los simplifica):
- **Falla el REST de Zetaris:** buscar en el kit otra vía oficial de consulta (sin verificar cuál existe); mientras tanto Josué avanza el agente contra una base local con **la misma SQL**, para cambiar solo el conector cuando Zetaris responda. Límite: si el viernes 9:00 AM Zetaris sigue sin responder, pedir ayuda en los canales del hackathon (sin verificar cuáles).
- **Falla la federación:** las 3 fuentes en el formato que sí funcione (aunque sean 3 CSV separados), pero siempre 3 fuentes unidas dentro de Zetaris, nunca un CSV único.
- **Falla Nightshift/Nemotron:** probar otro modelo Nemotron del catálogo; nunca `meterless/auto`.
- **Falla todo junto:** reducir el MVP a P1 + "no sé" con recibo, y P2 pasa a "si sobra".

### 6.2 Si el Sprint 1 cierra sin 3 fuentes federadas
Se sigue con P2 sobre lo que haya y Josué dedica el viernes por la tarde a la federación antes que al verificador. Las 3 fuentes son no negociables (8.1 del brief).

### 6.3 Si H-MEM no corre el sábado 9:00 PM
H-MEM es no negociable. Domingo mañana solo para H-MEM con su prueba más simple (guardar y recuperar una decisión). Si al domingo 1:00 PM no corre: la escena C del video se acorta a "bajo el capó" + métrica, y H-MEM se explica en el deck como lo intentado (honesto, sin fingir que funciona).

---

## 7. Qué recortar si vamos atrasados (en este orden)

**Nivel 1 (se decide en el portón P2, sáb 9:00 PM):**
1. Voz.
2. "Por qué" con hipótesis múltiples.
3. Markovian / Scout Intent.
4. Logo elaborado → solo tipografía MIDAZ.
5. Sugerencia de precio interactiva → una sola sugerencia con supuesto fijo en la caja (IVA fuera sigue diciéndose).

**Nivel 2 (se decide en P4, lun 9:00 PM):**
6. Animaciones del front → el recibo como bloque de texto.
7. Audio del dueño → cita textual en pantalla.
8. `golden.yaml` de 15 a 10 preguntas (reportando 10, no 15).
9. Deck reducido a 6-8 slides.

**Nunca se recorta:** recibo SQL por frase · 3 fuentes en Zetaris · lane Nemotron fijo + verificador · "no sé" · HU-15: un Meterless Engine (H-MEM) dentro de una función real con test que pasa · "Sample data" · README con los 4 sponsors · video.

---

## 8. Presupuesto de cupo NVIDIA (estimación propia, verificar el número real)

El brief dice ~400 solicitudes/día compartidas. **(Propuesta)** cada respuesta usa como máximo 2 llamadas (redactar + verificar); la SQL sale de plantillas, no del modelo.
- 1 corrida de `golden.yaml` (15 preguntas) ≈ 30 llamadas.
- Tope sugerido: 3 corridas completas al día (≈ 90) + pruebas manuales; el resto con caché o replay.
- Si se usa una llamada extra para entender la pregunta, son 3 por respuesta (≈ 45 por corrida): bajar a 2 corridas al día.
- Log con contador diario; al llegar a 300, solo replay.

---

## 9. Checklist de entrega

**Registro y plataforma**
- [ ] Equipo inscrito en HackOS antes del jue 22, 5:59 PM (captura).
- [ ] Dónde y cómo se entrega (formulario, enlaces, formatos) **(sin verificar)** — confirmarlo el jueves.

**Video**
- [ ] 1-4 min (meta ~2:30), inglés con subtítulos en español.
- [ ] 3 escenas: 80/20 de ganancia · "¿me alcanza?" + "no sé" · memoria + bajo el capó.
- [ ] "Sample data" visible; cifras en ₡ las de Zetaris del día de la grabación.
- [ ] Cifras del dolor con fuente en pantalla (BCCR; Reserva Federal; H&R Block **con el año 2020**).
- [ ] Ninguna llave, ningún "Jarvis".
- [ ] Enlace accesible para los jueces (formato **sin verificar**).

**Deck**
- [ ] Problema y cifras con fuente · Doña Marta · solución (modo dueño/juez como decisión de UX) · demo · arquitectura · confianza (recibo, verificador, "no sé", métrica `golden.yaml`) · sponsors · competencia y diferenciador · visión · equipo.

**Repo GitHub**
- [ ] Público, nuevo, commits desde 21-oct 6:00 PM, sin archivos privados de Abdiel.
- [ ] README (inglés + resumen en español) con una sección por sponsor: **Zetaris, Meterless (Nightshift + H-MEM), NVIDIA Nemotron** (Cursor es opcional).
- [ ] `DEMO.md` de 60 s con `MODO=replay`.
- [ ] `golden.yaml` + cifra real: "X/15 correctas, 0 números inventados, N/N 'no sé' correctos".
- [ ] Pruebas de H-MEM pasando.
- [ ] `.env.example`, sin llaves (historial revisado).
- [ ] Frase honesta sobre los datos de ejemplo.
- [ ] Tag/release; clone limpio probado.
- [ ] Licencia **(sin verificar si la piden)**.

---

## 10. Cómo suma cada parte en la rúbrica

| Criterio (pts) | Qué lo gana | Dónde se ve | Sprint |
|---|---|---|---|
| **Impacto (30)** | Doña Marta; cifras con fuente (BCCR 50,3 %, Reserva Federal 46 % precisión, H&R Block 47 %); cifra en ₡ del cierre; cita o audio de un dueño real | Video 0:00-0:25 y cierre; deck | S2 (entrevistas), S3 |
| **Técnico (20)** | SQL → chequeo en código → verificador → respuesta; cálculos en SQL; 3 fuentes federadas; métrica `golden.yaml`; `DEMO.md` que corre | Escena C, README, repo | S1, S2 |
| **Innovación (15)** | Casi sin interfaz + prueba por respuesta + "no sé" honesto + 80/20 aplicado **a la ganancia** | Escenas A y B; deck (diferenciador vs SocIA/Margen) | S2 |
| **Demo (15)** | ~2:30, 3 escenas, el "aha" arroz vs helado, frase tachada en rojo | Video | S3 |
| **Producto y UX (10)** | Modo dueño / modo juez; 2-3 frases; sello "verificado"; marca MIDAZ | Video, front | S2, S3 |
| **Sponsors (10)** | Zetaris federando 3 fuentes; Nightshift con lane Nemotron y receipt con nombre de modelo; verificador Nemotron; H-MEM dentro de una función real con test (HU-15) | Escena C, README, deck | S1-S3 |

**Desempate:** más Impacto, luego quien entregó antes → otra razón para entregar al mediodía del martes y para cuidar la parte de Impacto.

---

## 11. Pendiente de verificar (consolidado)

| # | Qué | Quién | Cuándo |
|---|---|---|---|
| 1 | "MIDAZ" libre como marca de software (USPTO + Registro Nacional CR) | Abdiel | Mié noche |
| 2 | Nombres exactos de los modelos Nemotron en Nightshift y cuál es el verificador | Josué | Mié noche |
| 3 | Endpoint REST de Zetaris (`/api/v1.0/sql-editor/sqls/run`, :8888) tal como dice el kit | Abdiel + Josué | Mié noche |
| 4 | Cómo accede Josué a Zetaris si corre en la PC de Abdiel | Ambos | Arranque mié |
| 5 | Federación Postgres+CSV y capa semántica en Zetaris local | Josué | Jue |
| 6 | Paquete H-MEM: cómo se instala y cómo se prueba | Josué | Vie |
| 7 | Cupo NVIDIA real (~400/día) y si es por persona o compartido | Josué | Mié |
| 8 | Plataforma y formato de la entrega final (enlaces, tamaño del video, deck) | Abdiel | Jue |
| 9 | Si el amigo dueño valida el demo o presta la estructura de su Excel/POS | Abdiel | Jue-Vie |
| 10 | Tamaño del dataset (propuesta: 150-300 productos, 90 días) | Abdiel | Jue 9:00 PM |
| 11 | Horarios disponibles de cada uno | Ambos | Arranque mié |
| 12 | Si piden licencia en el repo | Josué | Lun |

---

## 12. Notas sobre el brief (cosas que encontré al armar el plan)

1. **Sprints con días compartidos:** resuelto cortando al mediodía del 23 y del 25 (sección 0.2).
2. **El portón del jueves pide "datos mínimos", pero el generador está en la tarde del jueves:** por eso el CSV mínimo a mano va el miércoles en la noche.
3. **Las escenas B y C dependen de datos específicos** (carne sin costo, cambio de precio de la Coca, gastos por encima de la ganancia): quedaron como requisito del generador (2.3).
4. **Inscripción:** el brief la deja para el jueves con límite 5:59 PM; el plan la adelanta a las 2:00 PM.
5. **Frase del video "50 % of Costa Rican businesses don't survive 5 years":** el dato dice que el 50,3 % de las empresas formales nacidas en 2017 **seguía viva** a los 5 años. "Half of formal businesses don't make it to year 5 — BCCR" es más fiel al dato.
6. **Dos "47 %" distintos en el brief** (H&R Block: deciden por intuición; Intuit: no saben qué es ganancia bruta). En el pitch usar solo el de H&R Block para no confundir.
7. **Replay y video el mismo día:** las cifras en ₡ del video, del replay y del README tienen que ser la misma corrida.
