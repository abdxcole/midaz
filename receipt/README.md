# Recibo (HU-03)

Cada frase con número que ve Doña Marta lleva un recibo con: la frase, la SQL exacta, la vista y su definición, los términos de negocio (margen, ganancia bruta, costo operativo, producto estrella), fuentes y columnas, filas, hora y duración, advertencias de calidad de datos y el veredicto del verificador (por ahora `pendiente`; lo llena el verificador Nemotron en Sprint 2).

- Esquema: [`receipt.schema.json`](receipt.schema.json) (JSON Schema 2020-12).
- Ejemplo real generado por `python run.py`: [`example.json`](example.json).
- Regla dura (test `tests/test_receipts.py`): **ninguna frase con número sale sin recibo**, y si hay productos sin costo la respuesta empieza con **"No sé: N productos no tienen costo"**.
