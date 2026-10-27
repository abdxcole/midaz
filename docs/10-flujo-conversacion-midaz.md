# 10 - Flujo de conversación de MIDAZ (ARGOS, 2026-10-22)

> **MIDAZ - Turn your data into gold.** (Antes MIDAS; renombrado 2026-10-22. La carpeta de código sigue siendo `midas/`.)
> Fuentes: guion v1 de VERA (ES/EN), playbook 23 de VERA, `docs/02-brief-midas.md`, `docs/06-plan-midas.md`, `docs/09-equipo-y-reparto.md`, `midas/core.py`, `receipt/receipt.schema.json`.
> Constantes de prompt: `midas/prompts.py`. Nada privado ni llaves en este documento.

**Principios:** casi sin interfaz (la pantalla es la conversación) · cada respuesta trae su prueba (SQL + filas + sello verificado = recibo) · cada respuesta cita la factura/recibo/export de donde salió · sin evidencia = "I don't know" · cada hallazgo termina en un botón "What do I do now?" · memoria H-MEM construida solo desde recibos.

**Cifra real actual:** el 20 % de productos que más deja hace el **67.8 %** de la ganancia bruta (corrida local de datos de ejemplo). No se maquilla a 80/20: decimos "the top 20% makes 67.8% of your profit".

**Marcador del número demo:** donde falte una cifra de la corrida del lunes 26 se escribe exactamente `[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]`. Nunca se rellena a mano.

---

## 1. Flujo de conversación (estados)

```
[S0 GREETING] -> [S1 QUESTION] -> [S2 DATA LOOKUP (Zetaris)] --hay evidencia--> [S3 ANSWER + RECEIPT] -> [S5 ACTION BUTTONS] -> [S6 FOLLOW-UP / MEMORY] -> S1
                                              \--regla de calidad / sin filas--> [S4 "I DON'T KNOW"] -> [S5 ACTION BUTTONS]
```

| Estado | Qué pasa | Entrada | Salida | Quién lo hace |
|---|---|---|---|---|
| **S0 Greeting** | Saludo corto + promesa ("receipts or I don't know"). Si H-MEM tiene decisiones abiertas, ofrece "How did X go?". | sesión, H-MEM | 1-2 frases + hasta 3 botones sugeridos | plantilla (sin LLM) |
| **S1 Question** | Clasifica intención: `profit_8020`, `can_i_cover`, `price_change`, `memory_followup`, `out_of_scope`. | texto del dueño | intención + entidades | Nemotron (CLASSIFY) |
| **S2 Data lookup** | Elige archivo(s) de `sql/`, **una sentencia SQL por llamada**, corre en Zetaris (USL: margen, costo operativo, producto estrella). Corre `01_calidad_datos.sql` siempre. | intención | filas + recibo(s) `R-*` según `receipt.schema.json` | código (sin LLM) |
| **S3 Answer + receipt** | 2-3 frases + 1 recomendación. Cada frase con número lleva `[R-id]` y cita la fuente (POS export / factura de proveedor / gastos). Chequeo determinístico de números en código + verificador Nemotron (una llamada por respuesta) que tacha frases sin evidencia. Sello "Verified" solo si `verifier.verdict = confirmado`. | filas, recibos, memorias | respuesta modo dueño + "View receipt" (modo juez) | Nemotron (ANSWER, VERIFIER) + código |
| **S4 "I don't know"** | Disparado por **regla de calidad en código** (`sin_costo`, `precio_bajo_costo`, `ventas_negativas`) o por 0 filas, nunca por el modelo. Dice qué dato falta. | warning del recibo | "I don't know: I have no cost for beef." + chip ámbar con la regla | código + Nemotron (NO_EVIDENCE) |
| **S5 Action buttons** | Todo hallazgo termina en 1 botón principal "What do I do now?" (+ "View receipt"). Ejemplos: *Raise ice cream price*, *Add beef cost*, *Log decision*, *Remind me in 2 weeks*. El botón sugiere; decide el dueño. | respuesta | acción local (anotar decisión, abrir recibo, pedir dato) | UI |
| **S6 Follow-up / memory** | "Log decision" escribe un hecho H-MEM con `provenance = receipt id`. Al preguntar "How did that Coke price change go?" se re-corre el SQL, se compara antes/después y se marcan contradicciones. | decisión, recibo | hecho H-MEM / respuesta antes-después | código + Meterless H-MEM + Nemotron (FOLLOWUP) |

Reglas transversales: sin recibo la frase no se muestra; ninguna llave en prompts/logs; datos rotulados "Sample data"; Doña Marta = personaje.

---

## 2. Prompts (inglés; fuente de verdad: `midas/prompts.py`)

### 2.1 System prompt base
```
You are MIDAZ, the right hand of a small-business owner. Slogan: "Turn your data into gold."
Rules (non-negotiable):
1. You only state facts that come from the query results you are given (Zetaris SQL rows). Never compute or invent a number yourself.
2. Every sentence that contains a number must cite its receipt id in brackets, e.g. [R-8020]. A sentence without a receipt is deleted.
3. Every answer cites the source document (invoice / receipt / POS export) the rows came from.
4. If there is no evidence, or a data-quality rule fired, say "I don't know" and name the missing data. Do not guess.
5. Answer in 2-3 short, warm, plain sentences for the owner, then exactly one recommendation.
6. End every finding with one actionable "What do I do now?" button (label <= 5 words). You suggest; the owner decides.
7. Memories (H-MEM) are usable only if they carry provenance = a receipt id. If two memories contradict, say so.
8. Never mention API keys, internal names, or anything private. Data shown is labeled "Sample data".
```

### 2.2 Plantillas por paso
- **S0 GREETING:** `Hi {owner_name}, I'm MIDAZ. Ask me anything about your sales, costs or expenses. Every answer comes with its receipt, or I'll tell you "I don't know".`
- **S1 CLASSIFY:** `Classify the owner's question into one intent: profit_8020 | can_i_cover | price_change | memory_followup | out_of_scope. Return JSON {"intent","entities","needs_sql"}. Question: {question}`
- **S3 ANSWER:** `Owner question: {question} / Query results (one block per receipt): {receipt_blocks} / Data-quality warnings: {warnings} / Relevant memories: {memories}. Write the owner answer following the system rules. Cite [receipt_id] after every sentence with a number. Then output: ACTION: <button label> | <what it does>.`
- **S3 VERIFIER (1 llamada/respuesta):** `For each sentence return KEEP if every number appears in the cited receipt rows, else STRIKE. Return JSON [{sentence, verdict, reason}].`
- **S4 NO_EVIDENCE:** `The data-quality rule "{rule_code}" fired for: {items}. Write one sentence that starts with "I don't know" and names exactly what data is missing, then one ACTION button to fix it.`
- **S6 MEMORY_WRITE:** `Owner decision: {decision}. Based on receipt {receipt_id} (executed_at {executed_at}). Write one H-MEM fact: subject, predicate, object, provenance={receipt_id}.`
- **S6 FOLLOWUP:** `Owner asks about a past decision: {question}. Memory facts: {memories}. Fresh results: {receipt_blocks}. Compare before vs after using only receipts. Flag contradictions. End with one ACTION button.`

### 2.3 Ejemplos de salida (demo en inglés)
- **profit_8020:** "Your top 20% of products make **67.8%** of your gross profit [R-8020] — source: POS export + supplier invoices. Rice is #1 in units but near the bottom in profit [R-VOL]. **[What do I do now? → Review rice price]** · View receipt"
- **I don't know:** "I don't know: I have no cost for beef [R-NOSE], so it's left out. **[What do I do now? → Add beef cost]**"
- **can_i_cover:** "No: this month you're short **₡234.741 [PROVISIONAL demo, reemplazar lun 26]** [R-MES]. **[What do I do now? → See price options]**"
- **Cierre del video (decisión VERA 22-oct: X_MES no defendible):** "**[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]**/15 on the golden set, 0 invented numbers."

---

## 3. Checkpoints: auditoría de VERA y OK de Abdiel

| # | Momento | Quién | Qué se revisa / aprueba | Bloquea |
|---|---|---|---|---|
| V1 | Guion (ES/EN) antes de grabar (dom 25, 9:00 PM) | **VERA audita** | cada frase del VO tiene fuente o recibo; no "Jarvis"; 67.8 % sin maquillar | grabación |
| V2 | Claims de cada respuesta del demo y del deck | **VERA audita** | cada cifra ↔ recibo `R-*` ↔ filas; "I don't know" disparado por regla; sin cifras sin verificar | deck, README |
| V3 | Número demo (lun 26, 12:00 PM) | **VERA audita** (Josué corre, ARGOS redacta) | `X_FALTANTE`, `X_MES` y X/15 salen de la corrida, con recibo y hora | reemplazo de `[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]` |
| V4 | Auditoría final (mar 27, 10:00 AM) | **VERA audita** | sin llaves en repo/historial/video/capturas; checklist completo | entrega |
| A1 | Publicar algo (repo público, video, post, deck) | **OK de Abdiel** | nada sale sin su OK explícito | publicación |
| A2 | Acciones externas (correos, mensajes, formularios, cambios en Zetaris/Nightshift compartidos) | **OK de Abdiel** | quién recibe, qué dice | la acción |
| A3 | Entrega final (tag, video, envío al hackathon; meta mar 27 12:00 PM, límite 5:45 PM CR) | **OK de Abdiel** (VERA confirma) | V4 en verde | envío |

Dentro del producto: los botones de acción **nunca** ejecutan nada fuera de MIDAZ (no cambian precios en el POS ni mandan mensajes); solo anotan la decisión del dueño.

---

## 4. Memoria H-MEM desde recibos
- Hecho = `(sujeto, predicado, objeto, provenance = R-id, executed_at)`. Sin `R-id` no se guarda.
- Se escribe solo al tocar "Log decision" (S5) o al confirmar un hallazgo verificado.
- Al recordar: se muestra la tarjeta con "provenance = receipt #id" → salto al recibo. Si un hecho nuevo contradice uno viejo: badge "contradiction detected", se muestran los dos recibos, no se oculta ninguno.

---

## 5. Slots del demo: se CALCULAN, no se escriben a mano

Los dos huecos del guion (`₡[X_FALTANTE]` y `₡[X_MES]`) los **calcula MIDAZ desde los datos de ejemplo** con una métrica definida y un recibo. Nadie teclea el valor en el guion, deck o README: se copia de la salida de la corrida del **lunes 26** (misma corrida que el replay y el README). Hasta entonces el texto dice `[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]`.

### 5.1 X_FALTANTE — cuánto le falta a Doña Marta para cubrir el mes
- **Definición:** `faltante(mes) = costo_operativo(mes) - ganancia_bruta(mes)`, con `ganancia_bruta = SUM(qty * (unit_price_with_iva/1.13 - unit_cost))` solo productos con costo; ventas sin costo se reportan aparte (no cuentan como ganancia ni como cero). Si `faltante <= 0`, la respuesta es "Yes, you cover it" y no hay slot.
- **Mes del demo:** el mes del guion (definirlo en el replay); hoy `core.py` toma el peor mes.
- **SQL:** ya existe, `sql/30_me_alcanza.sql` (columna `faltante`). Recibo `R-MES`.
```sql
-- esbozo (ver sql/30_me_alcanza.sql)
SELECT g.mes, g.ganancia_bruta, o.costo_operativo,
       o.costo_operativo - g.ganancia_bruta AS faltante, g.ventas_sin_costo
FROM g JOIN o ON o.mes = g.mes;
```
- **Valor en guion (VERA, 22-oct):** **₡234.741 [PROVISIONAL demo, reemplazar lun 26]** = sept: gastos ₡4.145.000 − ganancia bruta ₡3.910.259 (fuente `data/output/control_8020.md`; ago: ₡245.546). Se reemplaza por la salida de la corrida del lun 26 (V3).

### 5.2 X_MES — ₡/mes recuperables
- **Definición propuesta (VERA la aprueba en V3):** plata que se recupera al mes **sin vender más**, solo corrigiendo lo que los datos ya muestran:
  `recuperable_mes = pérdida_bajo_costo_mes` donde `pérdida_bajo_costo_mes = SUM(qty * (unit_cost - unit_price_with_iva/1.13))` en líneas con precio sin IVA < costo (regla `precio_bajo_costo`), promedio mensual del periodo. Es conservadora y 100 % trazable: llevar esos productos al menos a su costo. No incluye supuestos de elasticidad ni "subir precio X %" (eso sería inventar).
- **Variante opcional (solo si VERA la acepta y se documenta el supuesto):** sumar el escenario de precio de la acción sugerida, mostrado como escenario, nunca como hecho.
- **SQL (a crear por Josué como `sql/31_recuperable_mes.sql`, una sentencia):**
```sql
-- recuperable_mes: pérdida por vender bajo costo, por mes (₡ sin IVA)
SELECT SUBSTR(CAST(v.date AS VARCHAR(10)), 1, 7) AS mes,
       SUM(v.qty * (c.unit_cost - v.unit_price_with_iva / 1.13)) AS recuperable_mes,
       COUNT(DISTINCT v.product_id) AS productos
FROM pos.ventas_pos v
JOIN inventario.costos_inventario c ON c.product_id = v.product_id
WHERE v.unit_price_with_iva / 1.13 < c.unit_cost AND v.qty > 0
GROUP BY SUBSTR(CAST(v.date AS VARCHAR(10)), 1, 7)
ORDER BY mes;
```
  Cifra del video = promedio mensual de `recuperable_mes` (o el mes del demo; VERA decide en V3). Recibo `R-RECUP`.
- **Estado (VERA, 22-oct): NO defendible → no se usa en video/deck.** Queda documentada por si la corrida del lun 26 la vuelve defendible.

### 5.3 Fallback (ACTIVO desde 22-oct)
Como `recuperable_mes` no es defendible (VERA lo rechazó el 22-oct), el cierre usa la métrica del golden set: "**[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]**/15 correct on the golden set, 0 invented numbers" (salida real de `tests/golden.yaml`, sin maquillar). **Bloqueador: `tests/golden.yaml` todavía no existe (dueño: ARGOS; runner: Josué).**

### 5.4 Valores fijos en la UI
Cualquier valor fijo para maquetar la UI (Figma, mockups, respuestas guardadas) lleva el rótulo visible **EJEMPLO** y **nunca** aparece en el video, deck ni README. IRIS y ARGOS los reemplazan por la salida de la corrida.

---

## 6. Qué queda bloqueado por el número demo
1. **X/15 del golden set** (cierre del video 2:10-2:30, deck slide 9, README, `GOLDEN_SET_LINE` en `midas/prompts.py`): sigue `[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]`. **Bloqueador principal: falta crear `tests/golden.yaml` (15 preguntas + respuestas esperadas) — dueño ARGOS**, luego Josué corre el runner y VERA audita (V3).
2. **X_FALTANTE**: provisional ₡234.741 (sept) en guion y ejemplo; se confirma o reemplaza con la corrida del lun 26.
3. **X_MES**: descartado por VERA (no defendible); el cierre usa X/15. `X_MES_SLOT` queda con el marcador y no se usa.
Nadie rellena estos valores a mano antes de la corrida.
