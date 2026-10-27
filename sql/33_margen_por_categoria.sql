-- G13: ganancia bruta por categoria (solo productos con costo). SAMPLE DATA.
-- Usa la vista margen_por_producto (sql/00_margen_por_producto.sql).
SELECT category,
       COUNT(*)            AS productos,
       SUM(ganancia_bruta) AS ganancia_bruta
FROM margen_por_producto
WHERE sin_costo = 0
GROUP BY category
ORDER BY ganancia_bruta DESC;
