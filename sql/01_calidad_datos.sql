-- Chequeos de calidad de datos (HU-03 / "no se"). Una fila por tipo de problema.
-- Si sin_costo > 0, la respuesta DEBE decir "No se: N productos no tienen costo".
SELECT 'sin_costo' AS chequeo,
       SUM(sin_costo) AS productos,
       SUM(CASE WHEN sin_costo = 1 THEN unidades ELSE 0 END) AS unidades,
       SUM(CASE WHEN sin_costo = 1 THEN ventas_sin_iva ELSE 0 END) AS ventas_sin_iva
FROM margen_por_producto
UNION ALL
SELECT 'precio_bajo_costo', SUM(CASE WHEN lineas_precio_bajo_costo > 0 THEN 1 ELSE 0 END),
       SUM(lineas_precio_bajo_costo), NULL
FROM margen_por_producto
UNION ALL
SELECT 'ventas_negativas', SUM(CASE WHEN lineas_negativas > 0 THEN 1 ELSE 0 END),
       SUM(lineas_negativas), NULL
FROM margen_por_producto;
