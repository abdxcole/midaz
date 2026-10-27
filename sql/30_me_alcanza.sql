-- "Me alcanza?": ganancia bruta del mes (solo productos con costo) vs gastos operativos del mes.
-- faltante > 0 = la ganancia NO cubre los gastos. Las ventas sin costo se reportan aparte
-- (no se suman como ganancia ni como cero).
WITH g AS (
    SELECT SUBSTR(CAST(v.date AS VARCHAR(10)), 1, 7) AS mes,
           SUM(CASE WHEN c.product_id IS NOT NULL
                    THEN v.qty * (v.unit_price_with_iva / 1.13 - c.unit_cost) END) AS ganancia_bruta,
           SUM(CASE WHEN c.product_id IS NULL
                    THEN v.qty * v.unit_price_with_iva / 1.13 ELSE 0 END)          AS ventas_sin_costo
    FROM pos.ventas_pos v
    LEFT JOIN inventario.costos_inventario c ON c.product_id = v.product_id
    GROUP BY SUBSTR(CAST(v.date AS VARCHAR(10)), 1, 7)
),
o AS (
    SELECT month AS mes, SUM(amount) AS costo_operativo
    FROM finanzas.gastos_operativos
    GROUP BY month
)
SELECT g.mes, g.ganancia_bruta, o.costo_operativo,
       o.costo_operativo - g.ganancia_bruta AS faltante,
       g.ventas_sin_costo
FROM g
JOIN o ON o.mes = g.mes
ORDER BY g.mes;
