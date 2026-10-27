-- Detalle de productos con ventas y SIN costo (para el texto del "no se").
SELECT product_id, unidades, ventas_sin_iva
FROM margen_por_producto
WHERE sin_costo = 1
ORDER BY product_id;
