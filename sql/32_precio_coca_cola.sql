-- G09: Coca-Cola 2.5 L (P003) antes y despues del cambio de precio del 2026-08-15. SAMPLE DATA.
-- Dias = dias del periodo con ventas de cualquier producto (calendario del POS), no solo de P003.
-- Ganancia bruta = qty x (precio/1.13 - costo), IVA 13 % excluido.
WITH dias AS (
    SELECT CASE WHEN date < '2026-08-15' THEN 'antes' ELSE 'despues' END AS periodo,
           COUNT(DISTINCT date) AS dias
    FROM pos.ventas_pos
    GROUP BY CASE WHEN date < '2026-08-15' THEN 'antes' ELSE 'despues' END
),
p AS (
    SELECT CASE WHEN v.date < '2026-08-15' THEN 'antes' ELSE 'despues' END AS periodo,
           MIN(v.unit_price_with_iva) AS precio_min_con_iva,
           MAX(v.unit_price_with_iva) AS precio_max_con_iva,
           SUM(v.qty) AS unidades,
           SUM(v.qty * (v.unit_price_with_iva / 1.13 - c.unit_cost)) AS ganancia_bruta
    FROM pos.ventas_pos v
    JOIN inventario.costos_inventario c ON c.product_id = v.product_id
    WHERE v.product_id = 'P003'
    GROUP BY CASE WHEN v.date < '2026-08-15' THEN 'antes' ELSE 'despues' END
)
SELECT p.periodo, p.precio_min_con_iva, p.precio_max_con_iva, d.dias, p.unidades,
       1.0 * p.unidades / d.dias AS unidades_por_dia,
       p.ganancia_bruta,
       p.ganancia_bruta / d.dias AS ganancia_por_dia
FROM p
JOIN dias d ON d.periodo = p.periodo
ORDER BY p.periodo;
