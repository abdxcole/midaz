-- HU-02 resumen: cuantos productos, ganancia total, cuanto hace el top 20 %, y cuantos llegan al 80 %.
WITH base AS (
    SELECT product_id, ganancia_bruta
    FROM margen_por_producto
    WHERE sin_costo = 0 AND unidades > 0
),
r AS (
    SELECT product_id, ganancia_bruta,
           ROW_NUMBER() OVER (ORDER BY ganancia_bruta DESC, product_id) AS rk,
           SUM(ganancia_bruta) OVER (ORDER BY ganancia_bruta DESC, product_id
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS acum,
           SUM(ganancia_bruta) OVER () AS total,
           COUNT(*) OVER () AS n
    FROM base
)
SELECT MAX(n)                                              AS n_productos,
       MAX(total)                                          AS ganancia_total,
       CAST(MAX(n) * 0.2 AS INTEGER)                       AS n_top20,
       100.0 * SUM(CASE WHEN rk <= CAST(n * 0.2 AS INTEGER) THEN ganancia_bruta ELSE 0 END) / MAX(total) AS pct_top20,
       MIN(CASE WHEN acum >= 0.8 * total THEN rk END)       AS n_para_80,
       100.0 * MIN(CASE WHEN acum >= 0.8 * total THEN rk END) / MAX(n) AS pct_catalogo_para_80
FROM r;
