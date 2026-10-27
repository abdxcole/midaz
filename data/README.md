# Datos de muestra — Minisuper "Doña Marta" (HU-05)

> **SAMPLE DATA / DATOS DE MUESTRA.** No son datos reales de ningún negocio. Productos y precios son realistas para Costa Rica; los **patrones de margen están inspirados en datos públicos de precios** (p. ej. los rangos de Konkurransetilsynet citados en el brief).

## Cómo generar
```
python data/generator.py
```
Solo librería estándar de Python, semilla fija (`20260701`): la salida es idéntica en cada corrida. Escribe en `data/output/`.

## Las 3 fuentes (separadas, para federar en Zetaris)
| Archivo | Columnas | Contenido |
|---|---|---|
| `ventas_pos.csv` | date, ticket, product_id, qty, unit_price_with_iva | ~46 mil líneas, 1-jul a 30-sep-2026 (90+ días), ~200 productos |
| `costos_inventario.csv` | product_id, name, category, unit_cost, stock | Costo unitario **sin IVA**. Las carnes (P007-P009) **no tienen fila** |
| `gastos_operativos.csv` | month, concept, amount | Planilla 4 empleados, alquiler, luz, agua, internet, patente, datáfono, otros |

Precios de venta en colones **con IVA 13 % incluido**. Ganancia bruta = `qty × (precio / 1.13 − costo)`.
Simplificación: se usa 13 % para todo (en la vida real la canasta básica, como arroz y frijoles, paga 1 %).

## Patrones sembrados (para las 3 escenas)
- **Arroz (P001) y frijoles (P002):** #1 y #2 en unidades, margen ~1-1,5 % → abajo en ganancia.
- **Helado (P004, P005) y Coca-Cola (P003, P006):** menos unidades, margen 36-45 %.
- **Carnes (P007-P009):** con ventas pero sin costo → el agente debe decir "no sé".
- **Coca-Cola 2.5 L (P003):** precio sube de ₡1.650 a ₡1.850 el **15-ago-2026**; ventas antes y después (algo menos de demanda después).
- **Gastos operativos** ≈ 6 % por encima de la ganancia bruta de cada mes → faltante en "¿me alcanza?".

## Hoja de control
`output/control_8020.csv` (ranking completo por ganancia con % acumulado y rank por volumen) y `output/control_8020.md` (resumen: 80/20, arroz volumen vs ganancia, Coca antes/después, faltante mensual). Sirven para verificar a mano las respuestas del agente.
