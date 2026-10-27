#!/usr/bin/env python3
"""MIDAZ HU-05 - Generador de DATOS DE MUESTRA (Sample data) para el minisuper "Dona Marta".
Solo stdlib, semilla fija => salida identica en cada corrida.
Patrones de margen inspirados en datos publicos de precios. NO son datos reales de ningun negocio.
Uso: python data/generator.py   (escribe en data/output/)
"""
import csv, os, random, datetime as dt
from collections import defaultdict

SEED = 20260701
IVA = 0.13
START, END = dt.date(2026, 7, 1), dt.date(2026, 9, 30)
COCA_ID, COCA_CHANGE = "P003", dt.date(2026, 8, 15)  # Coca-Cola 2.5L: 1650 -> 1850 desde esta fecha
COCA_OLD, COCA_NEW = 1650, 1850
SHORTFALL = 0.06  # gastos ~6% por encima de la ganancia bruta del mes
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
NOTE = "SAMPLE DATA / DATOS DE MUESTRA - patrones de margen inspirados en datos publicos de precios"

# (id fijo, nombre, categoria, precio con IVA, margen s/precio sin IVA, peso de venta)
ANCHORS = [
    ("P001", "Arroz Tio Pelon 99% 2 kg", "Granos", 2350, 0.010, 60),
    ("P002", "Frijoles negros Don Pedro 900 g", "Granos", 1450, 0.015, 40),
    (COCA_ID, "Coca-Cola 2.5 L", "Bebidas", COCA_OLD, 0.36, 9),
    ("P004", "Helado Dos Pinos vainilla 1 L", "Helados", 2950, 0.42, 5),
    ("P005", "Paleta Dos Pinos Choco", "Helados", 650, 0.45, 9),
    ("P006", "Coca-Cola lata 355 ml", "Bebidas", 650, 0.38, 8),
    ("P007", "Carne molida especial (kg)", "Carnes", 5200, None, 7),     # SIN costo
    ("P008", "Bistec de res (kg)", "Carnes", 6900, None, 4),            # SIN costo
    ("P009", "Chuleta de cerdo (kg)", "Carnes", 4600, None, 3),         # SIN costo
]
BASE = {  # categoria: (rango margen, [(nombre, precio con IVA)])
    "Granos": ((0.06, 0.14), [("Arroz Luisiana 80% 1 kg", 1150), ("Arroz Sabanero 2 kg", 2200), ("Frijoles rojos Don Pedro 900 g", 1500),
              ("Frijoles negros Kamuk 1 kg", 1600), ("Lentejas 400 g", 850), ("Garbanzos 400 g", 950), ("Maiz pira 400 g", 700), ("Avena Quaker 400 g", 1300)]),
    "Abarrotes": ((0.12, 0.22), [("Azucar Doña Maria 2 kg", 1900), ("Aceite Clover 1 L", 2100), ("Sal Sol 1 kg", 450), ("Cafe Rey 250 g", 2450),
              ("Cafe 1820 500 g", 4200), ("Pasta Roma spaghetti 250 g", 550), ("Atun Sardimar 140 g", 1150), ("Sardinas Sardimar 155 g", 850),
              ("Salsa Lizano 280 ml", 1450), ("Salsa de tomate Kerns 400 g", 1250), ("Harina Maseca 1 kg", 1350), ("Harina Gallo de Oro 1 kg", 950),
              ("Mantequilla Dos Pinos 115 g", 1100), ("Margarina Numar 500 g", 1500), ("Consome Maggi 12 u", 900), ("Mayonesa Hellmanns 400 g", 2300),
              ("Leche en polvo Dos Pinos 400 g", 3600), ("Galletas Maria Pozuelo", 650), ("Galletas Chiky", 450), ("Tortillas Tortirica 10 u", 850)]),
    "Lacteos": ((0.15, 0.24), [("Leche Dos Pinos 1 L", 1050), ("Leche deslactosada 1 L", 1200), ("Natilla Dos Pinos 230 g", 950), ("Queso Turrialba (kg)", 4800),
              ("Yogurt Dos Pinos 1 L", 1850), ("Huevos 15 u", 2650), ("Queso crema Dos Pinos 225 g", 1500)]),
    "Bebidas": ((0.25, 0.35), [("Fanta naranja 2.5 L", 1550), ("Fresca 2.5 L", 1550), ("Agua Cristal 600 ml", 650), ("Tropical 500 ml", 750),
              ("Del Valle 1 L", 1400), ("Gatorade 600 ml", 1050), ("Te frio Lipton 500 ml", 800), ("Pepsi 3 L", 1650), ("Malta Pilsen 355 ml", 600)]),
    "Cervezas y licores": ((0.20, 0.30), [("Cerveza Imperial lata 350 ml", 950), ("Cerveza Pilsen lata 350 ml", 950), ("Cerveza Bavaria lata 350 ml", 1050), ("Guaro Cacique 750 ml", 6500)]),
    "Snacks y dulces": ((0.28, 0.40), [("Papas Tosty 150 g", 1450), ("Doritos 145 g", 1600), ("Chicharron Jack's", 750), ("Chocolate Tapita", 500),
              ("Chicles Trident", 350), ("Mani Kiss", 600), ("Bon Bon Bum", 100), ("Gomitas Trululu", 550)]),
    "Helados": ((0.38, 0.46), [("Helado Dos Pinos fresa 1 L", 2950), ("Copa Dos Pinos", 750), ("Cono Dos Pinos", 900)]),
    "Panaderia": ((0.18, 0.28), [("Pan cuadrado Bimbo", 1850), ("Pan baguette", 700), ("Bizcocho (bolsa)", 1200), ("Pan dulce (unidad)", 350)]),
    "Frutas y verduras": ((0.20, 0.32), [("Platano maduro (u)", 250), ("Papa (kg)", 1100), ("Cebolla (kg)", 1300), ("Tomate (kg)", 1500), ("Chile dulce (u)", 300),
              ("Banano (kg)", 750), ("Culantro (rollo)", 300), ("Yuca (kg)", 800)]),
    "Limpieza": ((0.18, 0.28), [("Jabon Irex 1 kg", 2400), ("Cloro Ole 1 L", 900), ("Lavaplatos Axion 450 g", 1300), ("Papel higienico Nevax 4 u", 1650),
              ("Suavitel 850 ml", 1700), ("Bolsas basura 10 u", 900)]),
    "Cuidado personal": ((0.22, 0.32), [("Jabon Protex", 750), ("Shampoo Head&Shoulders 375 ml", 3900), ("Pasta Colgate 75 ml", 1250), ("Desodorante Rexona", 2350), ("Toallas Kotex 10 u", 1500)]),
}
VARIANTS = ["", " (presentacion pequena)", " (presentacion grande)", " marca economica"]
VAR_PRICE = [1.0, 0.6, 1.7, 0.85]

def r_price(x):  # precios redondeados a 25 colones
    return int(round(x / 25.0)) * 25

def build_products(rng):
    prods = []
    for pid, name, cat, price, m, w in ANCHORS:
        cost = None if m is None else round(price / (1 + IVA) * (1 - m), 2)
        prods.append(dict(id=pid, name=name, cat=cat, price=price, cost=cost, w=w))
    n = len(prods)
    for vi, suf in enumerate(VARIANTS):
        for cat, (mr, items) in BASE.items():
            for name, price in items:
                if len(prods) >= 200: break
                n += 1
                p = max(100, r_price(price * VAR_PRICE[vi]))
                m = rng.uniform(*mr)
                w = rng.uniform(0.5, 3.0) / (1 + vi * 1.5)
                prods.append(dict(id=f"P{n:03d}", name=name + suf, cat=cat, price=p,
                                  cost=round(p / (1 + IVA) * (1 - m), 2), w=w))
    return prods

def price_on(p, d):
    if p["id"] == COCA_ID:
        return COCA_NEW if d >= COCA_CHANGE else COCA_OLD
    return p["price"]

def main():
    rng = random.Random(SEED)
    prods = build_products(rng)
    os.makedirs(OUT, exist_ok=True)
    ids = [p["id"] for p in prods]
    weights = [p["w"] for p in prods]
    byid = {p["id"]: p for p in prods}
    ventas, ticket = [], 0
    d = START
    while d <= END:
        n_tickets = int(rng.gauss(170, 15) * (1.15 if d.weekday() >= 4 else 1.0))
        for _ in range(n_tickets):
            ticket += 1
            lines = {}
            for _ in range(rng.choice([1, 1, 2, 2, 3, 3, 4, 5, 6])):
                pid = rng.choices(ids, weights)[0]
                w = 1.0
                if pid == COCA_ID and d >= COCA_CHANGE:
                    w = 0.85  # algo menos de demanda tras la subida
                    if rng.random() > w: continue
                q = rng.choice([1, 1, 1, 2, 2, 3]) if pid in ("P001", "P002") else rng.choice([1, 1, 1, 1, 2])
                lines[pid] = lines.get(pid, 0) + q
            for pid, q in lines.items():
                ventas.append((d.isoformat(), f"T{ticket:06d}", pid, q, price_on(byid[pid], d)))
        d += dt.timedelta(days=1)

    with open(os.path.join(OUT, "ventas_pos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["date", "ticket", "product_id", "qty", "unit_price_with_iva"]); w.writerows(ventas)
    with open(os.path.join(OUT, "costos_inventario.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["product_id", "name", "category", "unit_cost", "stock"])
        for p in prods:
            if p["cost"] is None: continue  # carnes: SIN fila de costo (dispara el "no se")
            w.writerow([p["id"], p["name"], p["cat"], f"{p['cost']:.2f}", rng.randint(5, 120)])

    # ganancia bruta (sin IVA) por producto y por mes, solo productos con costo
    agg = defaultdict(lambda: [0, 0.0, 0.0])  # qty, ventas sin IVA, ganancia
    gp_month = defaultdict(float); sales_month = defaultdict(float); nocost = defaultdict(lambda: [0, 0.0])
    for date, _, pid, q, up in ventas:
        net = q * up / (1 + IVA); m = date[:7]; sales_month[m] += net
        p = byid[pid]
        if p["cost"] is None:
            nocost[pid][0] += q; nocost[pid][1] += net; continue
        g = net - q * p["cost"]
        a = agg[pid]; a[0] += q; a[1] += net; a[2] += g
        gp_month[m] += g

    gastos = []
    for m in sorted(gp_month):
        target = round(gp_month[m] * (1 + SHORTFALL), -3)
        fixed = [("Planilla 4 empleados (salarios + cargas sociales)", 1_880_000), ("Alquiler del local", 650_000),
                 ("Luz (CNFL, refrigeracion)", {"2026-07": 372_000, "2026-08": 391_000, "2026-09": 365_000}[m]),
                 ("Agua (AyA)", 38_000), ("Internet y telefono", 34_000), ("Patente municipal", 55_000),
                 ("Comision datafono", round(sales_month[m] * 0.6 * 0.025, -3))]
        rest = target - sum(a for _, a in fixed)
        assert rest > 0, (m, rest)
        for c, a in fixed + [("Otros (bolsas, limpieza, mantenimiento, transporte)", rest)]:
            gastos.append((m, c, int(a)))
    with open(os.path.join(OUT, "gastos_operativos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["month", "concept", "amount"]); w.writerows(gastos)

    # ---- hoja de control ----
    rows = sorted(agg.items(), key=lambda kv: -kv[1][2])
    total_gp = sum(a[2] for _, a in rows)
    vol_rank = {pid: i + 1 for i, (pid, _) in enumerate(sorted(agg.items(), key=lambda kv: -kv[1][0]))}
    cum, cut80 = 0.0, None
    with open(os.path.join(OUT, "control_8020.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank_ganancia", "rank_volumen", "product_id", "name", "category", "qty", "ventas_sin_iva", "ganancia_bruta_sin_iva", "pct_ganancia", "pct_acumulado"])
        for i, (pid, a) in enumerate(rows, 1):
            cum += a[2]
            if cut80 is None and cum / total_gp >= 0.8: cut80 = i
            w.writerow([i, vol_rank[pid], pid, byid[pid]["name"], byid[pid]["cat"], a[0], f"{a[1]:.2f}", f"{a[2]:.2f}",
                        f"{100*a[2]/total_gp:.2f}", f"{100*cum/total_gp:.2f}"])
    n = len(rows); top = max(1, round(n * 0.2))
    top_share = sum(a[2] for _, a in rows[:top]) / total_gp
    gp_rank = {pid: i for i, (pid, _) in enumerate(rows, 1)}
    exp_month = defaultdict(int)
    for m, _, a in gastos: exp_month[m] += a
    coca = defaultdict(lambda: [0, 0, 0.0])
    for date, _, pid, q, up in ventas:
        if pid == COCA_ID:
            k = "antes" if date < COCA_CHANGE.isoformat() else "despues"
            c = coca[k]; c[0] += q; c[2] += q * (up / (1 + IVA) - byid[pid]["cost"])
    days_before = (COCA_CHANGE - START).days; days_after = (END - COCA_CHANGE).days + 1

    L = [f"# Hoja de control HU-05 - {NOTE}", "",
         f"Semilla `{SEED}`. Ganancia bruta = qty x (precio/1.13 - costo). IVA 13% excluido. Productos sin costo (carnes) NO entran al 80/20.", "",
         "## 80/20 por ganancia bruta", "",
         f"- Productos con costo y ventas: **{n}**; ganancia bruta total 90 dias: **CRC {total_gp:,.0f}**",
         f"- Top 20% ({top} productos) = **{100*top_share:.1f}%** de la ganancia",
         f"- El 80% acumulado se alcanza con **{cut80} productos** ({100*cut80/n:.1f}% del catalogo)", "",
         "## Volumen vs ganancia", "", "| Producto | Rank volumen | Rank ganancia | Unidades | Ganancia CRC |", "|---|---|---|---|---|"]
    for pid in ("P001", "P002", COCA_ID, "P004", "P005", "P006"):
        a = agg[pid]; L.append(f"| {byid[pid]['name']} | {vol_rank[pid]} | {gp_rank[pid]} | {a[0]:,} | {a[2]:,.0f} |")
    L += ["", "Top 5 por ganancia: " + ", ".join(f"{byid[p]['name']}" for p, _ in rows[:5]), "",
          "## Carnes sin costo (deben disparar el \"no se\")", ""]
    for pid, (q, net) in sorted(nocost.items()):
        L.append(f"- {pid} {byid[pid]['name']}: {q:,} unidades, ventas sin IVA CRC {net:,.0f}, SIN fila en costos_inventario")
    L += ["", f"## Cambio de precio Coca-Cola 2.5 L ({COCA_ID}) el {COCA_CHANGE.isoformat()}: CRC {COCA_OLD} -> {COCA_NEW} (con IVA)", ""]
    for k, nd in (("antes", days_before), ("despues", days_after)):
        q, _, g = coca[k]; L.append(f"- {k}: {nd} dias, {q:,} unidades ({q/nd:.1f}/dia), ganancia CRC {g:,.0f} ({g/nd:,.0f}/dia)")
    L += ["", "## Faltante mensual (gastos operativos - ganancia bruta)", "", "| Mes | Ganancia bruta | Gastos | Faltante |", "|---|---|---|---|"]
    for m in sorted(gp_month):
        L.append(f"| {m} | {gp_month[m]:,.0f} | {exp_month[m]:,.0f} | **{exp_month[m]-gp_month[m]:,.0f}** |")
    with open(os.path.join(OUT, "control_8020.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\nfilas ventas: {len(ventas)}, productos: {len(prods)}")

if __name__ == "__main__":
    main()
