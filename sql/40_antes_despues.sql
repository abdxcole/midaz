-- HU-14: antes vs despues de una decision del dueno guardada en H-MEM (p. ej. "subi la Coca").
-- Parametros (los sustituye midas/core.py: run_query, validados): {{product_id}} (P###),
-- {{fecha}} (AAAA-MM-DD, dia de la decision), {{desde}} / {{hasta}} (ventana de {{dias}} dias a cada lado).
-- Comparar `date` contra texto 'AAAA-MM-DD' funciona en SQLite; en Spark/Zetaris se castea solo (sin verificar).
SELECT CASE WHEN v.date < '{{fecha}}' THEN 'antes' ELSE 'despues' END   AS periodo,
       SUM(v.qty)                                                    AS unidades,
       SUM(v.qty * (v.unit_price_with_iva / 1.13 - c.unit_cost))     AS ganancia_bruta,
       {{dias}}                                                      AS dias
FROM pos.ventas_pos v
JOIN inventario.costos_inventario c ON c.product_id = v.product_id
WHERE v.product_id = '{{product_id}}'
  AND v.date >= '{{desde}}' AND v.date < '{{hasta}}'
GROUP BY CASE WHEN v.date < '{{fecha}}' THEN 'antes' ELSE 'despues' END
ORDER BY periodo;
