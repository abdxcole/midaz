-- Vista semantica margen_por_producto (HU-04). SAMPLE DATA.
-- Fuentes (3, separadas): pos.ventas_pos, inventario.costos_inventario, finanzas.gastos_operativos.
-- Precios POS traen IVA 13 % incluido; aqui se excluye: precio_sin_iva = unit_price_with_iva / 1.13.
-- Ganancia bruta = qty x (precio_sin_iva - unit_cost). Margen = ganancia_bruta / ventas_sin_iva.
-- LEFT JOIN a costos: un producto con ventas y sin fila de costo queda con sin_costo = 1 y
-- ganancia_bruta NULL (nunca 0): el agente debe decir "no se", no inventar.
-- Dialecto: ANSI SQL (CTE, CASE, LEFT JOIN, SUM). Supuestos para Zetaris/Spark SQL en sql/README.md.
CREATE VIEW margen_por_producto AS
SELECT
    v.product_id,
    c.name,
    c.category,
    SUM(v.qty)                                              AS unidades,
    SUM(v.qty * v.unit_price_with_iva / 1.13)               AS ventas_sin_iva,
    SUM(v.qty * c.unit_cost)                                AS costo_total,
    SUM(v.qty * (v.unit_price_with_iva / 1.13 - c.unit_cost)) AS ganancia_bruta,
    CASE WHEN MAX(c.product_id) IS NULL THEN 1 ELSE 0 END   AS sin_costo,
    SUM(CASE WHEN c.unit_cost IS NOT NULL
              AND v.unit_price_with_iva / 1.13 < c.unit_cost THEN 1 ELSE 0 END) AS lineas_precio_bajo_costo,
    SUM(CASE WHEN v.qty < 0 OR v.unit_price_with_iva < 0 THEN 1 ELSE 0 END)     AS lineas_negativas
FROM pos.ventas_pos v
LEFT JOIN inventario.costos_inventario c
       ON c.product_id = v.product_id
GROUP BY v.product_id, c.name, c.category;
