# SQL de MIDAZ (Sprint 1)

> SAMPLE DATA. Todo corre igual en el sustituto local (`python run.py`, SQLite) y, cuando este arriba, en Zetaris.

| Archivo | Qué responde | HU |
|---|---|---|
| `00_margen_por_producto.sql` | Vista `margen_por_producto` (une ventas POS + costos; IVA 13 % excluido; marca `sin_costo`) | HU-04 |
| `01_calidad_datos.sql` | Productos sin costo, precio bajo costo, ventas negativas | HU-03 |
| `02_sin_costo_detalle.sql` | Detalle de los productos sin costo (texto del "no sé") | HU-03 |
| `10_hu02_8020_ranking.sql` | Ranking por ganancia con % acumulado y `producto_estrella` | HU-02 |
| `11_hu02_8020_resumen.sql` | Top 20 % = X % de la ganancia; cuántos llegan al 80 % | HU-02 |
| `20_vende_mucho_deja_poco.sql` | Rank volumen vs rank ganancia (top 10 en unidades) | HU-02 |
| `30_me_alcanza.sql` | Ganancia bruta del mes vs gastos operativos → faltante | Sprint 2 (adelantado) |
| `32_precio_coca_cola.sql` | Coca-Cola 2.5 L antes/después del cambio de precio (2026-08-15): unidades y ganancia por día | golden G09 |
| `33_margen_por_categoria.sql` | Ganancia bruta por categoría (solo productos con costo) | golden G13 |
| `40_antes_despues.sql` | Antes vs después de una decisión guardada en H-MEM (parámetros `{{product_id}}`, `{{fecha}}`) | HU-14 / HU-15 |
| `zetaris/01_federar_fuentes.sql` | Registro de las 3 fuentes separadas en Zetaris **(sin verificar)** | HU-04 |

## Términos de negocio (los mismos del recibo)

- **Precio sin IVA** = `unit_price_with_iva / 1.13`.
- **Ganancia bruta** = `qty × (precio sin IVA − unit_cost)`.
- **Margen** = `ganancia bruta / ventas sin IVA`.
- **Costo operativo (del mes)** = `SUM(gastos_operativos.amount)` del mes.
- **Producto estrella** = está en el top `FLOOR(0,2 × N)` por ganancia bruta, con N = productos con costo y ventas.
- **Sin costo** = tiene ventas pero no fila en `costos_inventario` → no entra al 80/20 y dispara "No sé".

## Supuestos de dialecto (Zetaris / Spark SQL) **(sin verificar en Zetaris)**

1. **Nombres de 2 partes** `pos.ventas_pos`, `inventario.costos_inventario`, `finanzas.gastos_operativos`. En Zetaris probablemente sean 3 partes (`<lightning_db>.<schema>.<tabla>`, p. ej. un Postgres registrado con `CREATE DATASOURCE` y CSV como Lightning DB). Al federar, Josué ajusta solo los prefijos; `midas/core.py: load_sql()` los reescribe con la variable de entorno `MIDAZ_SCHEMA_MAP` (p. ej. `pos=pg_pos.public,inventario=csv_inv.default`).
2. **`CREATE VIEW`**: en SQLite el runner la crea como `CREATE TEMP VIEW` (SQLite no deja que una vista normal cruce bases adjuntas). En Zetaris puede requerir `CREATE VIEW <db>.<schema>.margen_por_producto` o la capa semántica; si no existe, plan B del plan: vista SQL normal.
3. **`date`** se usa como nombre de columna sin comillas (no reservado en SQLite ni en Spark por defecto). Si Zetaris corre con ANSI estricto, poner `` `date` `` (Spark) o `"date"`.
4. **`SUBSTR(CAST(date AS VARCHAR(10)),1,7)`** saca el mes `AAAA-MM` sirva la columna como texto o como DATE.
5. **División**: `/ 1.13` da decimal en ambos; Spark devuelve DECIMAL y REST lo manda como string (a veces en notación exponencial) → convertir antes de comparar.
6. **`CAST(x AS INTEGER)`** trunca (= FLOOR para positivos) en SQLite y Spark.
7. Ventanas `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` y `ROW_NUMBER()`: SQLite ≥ 3.25 y Spark las soportan.
8. Un archivo = una sentencia, terminada en `;` (quitar el `;` si el endpoint REST lo rechaza; el runner lo quita).
