-- "Vende mucho, deja poco": rank por volumen vs rank por ganancia (top 10 en unidades).
-- brecha > 0 = esta mas abajo en ganancia que en volumen.
WITH r AS (
    SELECT product_id, name, unidades, ganancia_bruta,
           100.0 * ganancia_bruta / ventas_sin_iva AS margen_pct,
           ROW_NUMBER() OVER (ORDER BY unidades DESC, product_id)       AS rank_volumen,
           ROW_NUMBER() OVER (ORDER BY ganancia_bruta DESC, product_id) AS rank_ganancia
    FROM margen_por_producto
    WHERE sin_costo = 0 AND unidades > 0
)
SELECT rank_volumen, rank_ganancia, rank_ganancia - rank_volumen AS brecha,
       product_id, name, unidades, ganancia_bruta, margen_pct
FROM r
WHERE rank_volumen <= 10
ORDER BY rank_volumen;
