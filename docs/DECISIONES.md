# Decisiones

Registro de decisiones del equipo. Una línea por decisión, la más nueva abajo.

| Fecha (CR) | Decisión | Quién decidió |
|---|---|---|
| 2026-10-21 | Nombre público: **MIDAZ** (no usar "Jarvis" en nada público). | Abdiel |
| 2026-10-21 | La coordinación interna pasa a entradas numeradas con índice y dos equipos (Abdiel / Josué). | Abdiel |
| 2026-10-21 | Gate P0 de las 9 PM: Zetaris `SELECT` por REST + Nightshift con Nemotron, dueño Josué. | Plan (`docs/06-plan-midas.md`) |
| 2026-10-22 | Según el anuncio oficial (Discord): Cursor no da tokens ni créditos y es opcional; el plan no depende de créditos de ninguna herramienta. Requisito central: un Meterless Engine dentro de una función real con test o demo; elegimos **H-MEM** (memoria de decisiones del dueño), HU-15 en Sprint 2, test `tests/test_hmem.py` en `python run.py test`. Llave NVIDIA y token del Meterless Runtime van en Nightshift y en la configuración de la app, nunca en la herramienta de código ni en el repo. | Abdiel (anuncio oficial) |
| 2026-10-22 | Reparto del equipo: Abdiel dueño y decide; VERA coordina/audita (guion 2:30 en inglés con subtítulos #15, auditoría final y del README); ARGOS PM + UX; IRIS dirige lo visual, PIXEL imágenes, MOTION video; Josué backend (Zetaris/Nightshift + Nemotron, 3 fuentes, reglas de calidad, H-MEM HU-15 con ARGOS). Sin bot nuevo de datos; MIDAZ sin landing. Code freeze lun 26 12:00 PM, entrega interna mar 27 12:00 PM, oficial mar 27 5:45 PM (CR); checkpoint diario 9:00 PM. Detalle en `docs/09-equipo-y-reparto.md`. | Abdiel |
| 2026-10-22 | (Propuesta, falta OK de Josué/Abdiel) Backend en `josue/backend`: H-MEM como **port Python** de la referencia oficial de Meterless con sus vectores de conformidad en `tests/test_hmem.py` (no hay paquete Python oficial); motor `zetaris` con la vista como CTE por defecto (`MIDAZ_ZETARIS_VIEW`); lane Nemotron en `MIDAZ_NEMOTRON_LANE`, cualquier id con `auto` se rechaza; guardia de números en código tacha frases con números sin recibo; el recibo suma el campo opcional `redaccion`. Detalle en `docs/11-backend-josue.md`. | equipo-josue / jayden (propuesta) |
| 2026-10-22 | Nightshift corre en la PC de Abdiel. | Josué |
| 2026-10-26 | El video del pitch va en español con subtítulos en inglés, narrado por Abdiel sobre la pantalla. Si Nemotron no está verificado, el video muestra solo H-MEM. | Abdiel |
| 2026-10-26 | Pantalla local para el video del pitch: `python run.py ui` (stdlib, en español). No cambia la lógica de `midas/core.py`, `verifier.py` ni `memory.py`. Muestra la respuesta, el SQL, las filas, las fuentes/tablas y el sello del verificador. Zetaris sigue en la máquina del equipo; el video es la prueba en vivo. `run.py` carga un `.env` local si existe, sin pisar variables ya definidas y sin imprimir valores. El PR no se fusiona: lo audita el lead. | Abdiel (pedido para el video) |
| 2026-10-26 | La terminal imprime «SAMPLE DATA» solo cuando el motor no es Zetaris (muestra u offline). | Revisor del PR #9 |
| 2026-10-27 | La pantalla local (`python run.py ui`) queda en inglés para los jueces: fondo oscuro, una columna, respuesta grande con el número clave en oro, sello Verified / Not verified, y la prueba plegada en «Show proof». No cambia el motor, el verificador, el SQL ni el contrato de `/api/pregunta`. La etiqueta Sample data solo si el motor no es Zetaris. | Abdiel (pedido) |
