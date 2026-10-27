-- HU-02: ranking 80/20 por GANANCIA BRUTA (no por volumen). Excluye productos sin costo.
WITH base AS (
    SELECT product_id, name, category, unidades, ventas_sin_iva, ganancia_bruta
    FROM margen_por_producto
    WHERE sin_costo = 0 AND unidades > 0
),
r AS (
    SELECT b.*,
           ROW_NUMBER() OVER (ORDER BY ganancia_bruta DESC, product_id) AS rank_ganancia,
           ROW_NUMBER() OVER (ORDER BY unidades DESC, product_id)       AS rank_volumen,
           SUM(ganancia_bruta) OVER ()                                  AS ganancia_total,
           COUNT(*) OVER ()                                             AS n_productos
    FROM base b
)
SELECT rank_ganancia, rank_volumen, product_id, name, category, unidades,
       ventas_sin_iva, ganancia_bruta,
       100.0 * ganancia_bruta / ganancia_total AS pct_ganancia,
       100.0 * SUM(ganancia_bruta) OVER (ORDER BY rank_ganancia
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / ganancia_total AS pct_acumulado,
       CASE WHEN rank_ganancia <= CAST(n_productos * 0.2 AS INTEGER) THEN 1 ELSE 0 END AS producto_estrella
FROM r
ORDER BY rank_ganancia;
