"""Prompt constants for MIDAZ conversation flow (see docs/10-flujo-conversacion-midaz.md).

English on purpose: the demo is in English. No secrets here; keys live only in env vars.
Demo figures are NOT invented: they stay as DEMO_NUMBER_PLACEHOLDER until VERA brings them.
"""

DEMO_NUMBER_PLACEHOLDER = "[[PENDIENTE: NÚMERO DEMO — lo trae VERA]]"

# Real figure from the current sample run. Do not round it to 80 %.
TOP20_PROFIT_SHARE = "67.8%"

SLOGAN = "Turn your data into gold."

SYSTEM_PROMPT = """You are MIDAZ, the right hand of a small-business owner. Slogan: "Turn your data into gold."
Rules (non-negotiable):
1. You only state facts that come from the query results you are given (Zetaris SQL rows). Never compute or invent a number yourself.
2. Every sentence that contains a number must cite its receipt id in brackets, e.g. [R-8020]. A sentence without a receipt is deleted.
3. Every answer cites the source document (invoice / receipt / POS export) the rows came from.
4. If there is no evidence, or a data-quality rule fired, say "I don't know" and name the missing data. Do not guess.
5. Answer in 2-3 short, warm, plain sentences for the owner, then exactly one recommendation.
6. End every finding with one actionable "What do I do now?" button (label <= 5 words). You suggest; the owner decides.
7. Memories (H-MEM) are usable only if they carry provenance = a receipt id. If two memories contradict, say so.
8. Never mention API keys, internal names, or anything private. Data shown is labeled "Sample data".
"""

GREETING_TEMPLATE = """Hi {owner_name}, I'm MIDAZ. Ask me anything about your sales, costs or expenses.
Every answer comes with its receipt, or I'll tell you "I don't know"."""

CLASSIFY_TEMPLATE = """Classify the owner's question into one intent: profit_8020 | can_i_cover | price_change | memory_followup | out_of_scope.
Return JSON: {{"intent": "...", "entities": [...], "needs_sql": true|false}}.
Question: {question}"""

ANSWER_TEMPLATE = """Owner question: {question}
Query results (one block per receipt):
{receipt_blocks}
Data-quality warnings: {warnings}
Relevant memories (each with provenance receipt id): {memories}

Write the owner answer following the system rules. Cite [receipt_id] after every sentence with a number.
Then output: ACTION: <button label> | <what it does>."""

NO_EVIDENCE_TEMPLATE = """The data-quality rule "{rule_code}" fired for: {items}.
Write one sentence that starts with "I don't know" and names exactly what data is missing,
then one ACTION button to fix it (e.g. "Add beef cost")."""

VERIFIER_TEMPLATE = """You are the MIDAZ verifier. One call per answer.
For each sentence below, return KEEP if every number in it appears in the cited receipt rows, else STRIKE.
Receipts: {receipt_blocks}
Answer sentences: {sentences}
Return JSON list: [{{"sentence": n, "verdict": "KEEP|STRIKE", "reason": "..."}}]"""

MEMORY_WRITE_TEMPLATE = """Owner decision to remember: {decision}
Based on receipt: {receipt_id} (executed_at {executed_at}).
Write one H-MEM fact: subject, predicate, object, provenance={receipt_id}. No facts without provenance."""

FOLLOWUP_TEMPLATE = """Owner asks about a past decision: {question}
Memory facts (with provenance): {memories}
Fresh query results: {receipt_blocks}
Compare before vs after using only receipts. Flag contradictions explicitly. End with one ACTION button."""

CLOSING_LINE = (
    "Messy data in, honest answers out. That's " + DEMO_NUMBER_PLACEHOLDER
    + " a month she can get back. Receipts, or 'I don't know.' MIDAZ: turn your data into gold."
)

GOLDEN_SET_LINE = DEMO_NUMBER_PLACEHOLDER + "/15 on the golden set, 0 invented numbers."

# Demo slots are COMPUTED, never hardcoded (see doc 10, section 5).
# X_FALTANTE -> sql/30_me_alcanza.sql, column `faltante` of the month under review (> 0 = short).
# X_MES      -> sql/31_recuperable_mes.sql (to be written by backend), metric `recuperable_mes`.
X_FALTANTE_SLOT = "₡234.741 [PROVISIONAL demo, reemplazar lun 26]"  # VERA 22-oct, sept
# X_MES: not defensible (VERA 22-oct); closing uses GOLDEN_SET_LINE instead.
X_MES_SLOT = DEMO_NUMBER_PLACEHOLDER
# UI mockup values only. Labeled EJEMPLO. NEVER used in the video, deck or README.
UI_EXAMPLE_LABEL = "EJEMPLO"
