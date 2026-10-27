# 16 — Plan de ejecución: MIDAZ (2026-10-21)

Para Abdiel y Josué. Open Agent Hackathon 2026, **Track 02 "The Agent That Can Explain Why"**.
Fuentes: el brief (qué construimos, hoy [02-brief-midas.md](02-brief-midas.md)), el kit del hackathon (reglas y setup, hoy [01-kit-hackathon.md](01-kit-hackathon.md)) y la investigación de jueces (rúbrica, hoy [04-jueces.md](04-jueces.md)), en sus versiones del 2026-10-21.
Regla del documento: lo que no sabemos con certeza dice **(sin verificar)**. Hay que confirmarlo antes de depender de eso.

**Fechas duras (hora Costa Rica):**
- Build abre: **mié 21-oct, 6:00 pm**.
- Inscripción del equipo cierra: **jue 22-oct, 5:59 pm**. Hacerlo antes del mediodía.
- Juzgamiento abre: lun 26-oct, 6:00 pm.
- Entrega cierra: **mar 27-oct, 5:45 pm**. Nuestra meta: **entregar el martes antes de las 12:00 m.d.** (en un empate gana quien entregó antes).

---

## 0. Resumen en 10 líneas

1. Doña Marta le pregunta a su "mano derecha" (chat y, si da tiempo, voz) cosas como "¿qué productos me dan la plata?" o "¿me alcanza para los gastos?".
2. Los datos del minisúper viven en **3 fuentes separadas** (ventas del POS, costos e inventario del ERP, gastos operativos) y **Zetaris** las une sin copiarlas, con una **vista semántica `margen_por_producto`**.
3. Todas las cuentas se hacen **en SQL dentro de Zetaris**. El modelo nunca calcula: elige la consulta, lee las filas y redacta.
4. Un lane **Nemotron fijo** redacta. Un segundo lane **Nemotron fiscal** revisa cada frase contra las filas y **borra la que no tenga prueba**. Si no queda nada, la respuesta es **"no sé"** y dice qué dato falta.
5. Cada frase con número trae su **recibo**: SQL exacto, vista de origen, filas, hora, modelo que redactó y modelo que verificó (receipt de Nightshift).
6. **H-MEM** (motor Meterless) recuerda hallazgos y decisiones del dueño. Sus pruebas pasan en pantalla.
7. Todo corre a través de **Meterless Nightshift**, que es el proveedor principal. La llave de NVIDIA vive solo en Nightshift.
8. La cifra de plata del cierre (en colones, sobre **datos de ejemplo rotulados**) sale de una consulta en Zetaris, no de una diapositiva.
9. La herramienta de código es libre (Cursor es opcional y **no da créditos**, anuncio 2026-10-22). El plan no depende de créditos de ninguna herramienta.
10. Entregables: video de 1 a 4 min, slide deck y repo público con README que corre y explica el uso de Zetaris, Meterless y NVIDIA.

**Dónde está cada parte:** arquitectura y repo → 2 · datos del minisúper → 3 · Zetaris → 4 · Nightshift/Nemotron → 5 · agente (plantillas SQL, fiscal, "no sé", precios) → 6 · conversación y voz → 7 · motor H-MEM y su prueba → 8 · tareas por día → 9 · checklist y slide deck → 10 · guion del demo → 11 · riesgos → 12 · qué recortar → 13.

---

## 1. Cómo sumamos puntos (rúbrica oficial → qué lo prueba)

| Criterio (puntos) | Qué hacemos | Qué lo prueba (en el video, el deck o el repo) |
|---|---|---|
| **Impacto (30)** | Doña Marta, dolor con fuente (47 % decide por intuición; 1 de cada 3 no sabe su margen; la mitad de las empresas de CR cierra antes de 5 años) y **una cifra en ₡** | Video 0:00-0:25 y cierre con la cifra en ₡. Slide "Impacto". Estas cifras también desempatan |
| **Técnico (20)** | Plan → SQL en Zetaris → fiscal → respuesta. Cuentas en SQL. Pruebas. Manejo de errores. Modo replay. README que corre | `pytest -v` en verde en el video. README con 5 comandos. Diagrama |
| **Innovación (15)** | Sin interfaz (solo conversación/voz), **recibo por frase**, "no sé" honesto, 80/20 **de ganancia** (no de volumen), fiscal que borra frases en vivo | Momento "aha" arroz vs helado. Frase tachada en rojo por el fiscal |
| **Demo (15)** | Historia de 3 min con un solo hilo: "¿por qué no me alcanza?" → respuesta → prueba → acción → cifra | Guion de la sección 11 |
| **Producto y UX (10)** | Lenguaje de dueño, respuestas de 2-3 frases, recibo bonito, sello claro | Diseño de Abdiel. Capturas en el deck |
| **Sponsor tech (10)** | Zetaris federado + vista semántica, Nightshift con 2 lanes Nemotron y receipt, H-MEM dentro de una función real con prueba en verde (HU-15) | Sección "Bajo el capó" del video. Sección del README. Slides 7-9 |

**Los 5 no negociables (si falta uno, no entregamos así):**
1. Recibo SQL por cada afirmación con número.
2. 3 fuentes separadas unidas en Zetaris, más la vista semántica `margen_por_producto`.
3. Lane Nemotron fijo + verificador Nemotron que borra frases sin evidencia, con receipt visible de Nightshift (sin llaves).
4. H-MEM (y Markovian si da tiempo) integrado de verdad, con pruebas pasando en pantalla.
5. Una cifra de plata concreta en ₡ sobre los datos de ejemplo rotulados.

---

## 2. Arquitectura y estructura del repo

### 2.1 Diagrama

```
                Doña Marta (chat o voz en el navegador)
                         │  texto (voz → texto con Web Speech API)
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│  web/  (una sola página: conversación + "ver recibo" + sello)       │
└───────────────────────────┬────────────────────────────────────────┘
                            │ POST /preguntar   (JSON)
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  API (Python, FastAPI)                                              │
│                                                                     │
│  1. Intención ──► lane NEMOTRON RÁPIDO: ¿qué pregunta es?           │
│        (pareto | volumen_vs_margen | cobertura | por_que |          │
│         simular_precio | memoria | fuera_de_alcance)                │
│  2. Plan ──────► plantillas SQL fijas + parámetros validados        │
│  3. Ejecutar ──► Zetaris REST  (filas + hash + hora)                │
│  4. Redactar ──► lane NEMOTRON RÁPIDO → JSON {frases, citas}        │
│  5. FISCAL ────► a) re-ejecuta el SQL en Zetaris, compara hash      │
│                  b) chequeo de números (código, sin LLM)            │
│                  c) lane NEMOTRON FISCAL: ¿la frase sale de filas?  │
│                  → borra frases sin prueba; si no queda nada: "no sé"│
│  6. Memoria ───► H-MEM (Meterless Engine): guarda hallazgos         │
│                  y decisiones; los números se vuelven a consultar   │
│  7. Presupuesto ► caché, tope diario, modo replay, log de receipts  │
└───────┬───────────────────────────────┬────────────────────────────┘
        │ SQL por REST                  │ OpenAI-compatible /v1/chat/completions
        ▼                               ▼  headers: meterless-app, meterless-scope
┌───────────────────────────┐   ┌──────────────────────────────────────┐
│ ZETARIS (Docker local)    │   │ METERLESS NIGHTSHIFT (proveedor único)│
│ POST /api/v1.0/sql-editor │   │  lane rápido  → Nemotron (sin verificar)│
│      /sqls/run  (:8888)   │   │  lane fiscal  → Nemotron (sin verificar)│
│                           │   │  llave NVIDIA solo en Providers       │
│ Vista semántica:          │   └──────────────────────────────────────┘
│  margen_por_producto      │
│      ▲      ▲      ▲      │   Federado, sin ETL: los datos se quedan
│      │      │      │      │   donde viven.
└──────┼──────┼──────┼──────┘
       │      │      │
  ┌────┴──┐┌──┴───┐┌─┴─────────┐
  │ A.POS ││ B.ERP││ C.Gastos  │   ← 3 fuentes separadas
  │Postgres││Postgres││ CSV (libreta│     (datos de ejemplo)
  │ ventas ││costos+ ││ del contador)│
  │        ││invent. ││            │
  └────────┘└──────┘└───────────┘

Construido sobre ZETARIS (data harness); herramienta de código a elección.
```

### 2.2 Decisiones de stack (para no discutir después)
- **Backend:** Python 3.11+, FastAPI, `httpx` (Zetaris), SDK `openai` apuntando a Nightshift, `sqlglot` (validar que el SQL sea solo lectura), `pytest`, SQLite (caché y bitácora).
- **Frontend:** **una sola página** `web/index.html` + `app.js` + `estilo.css`, sin framework. Es lo más rápido, no se rompe y Abdiel la diseña con la herramienta de código que prefiera. Nada de Next.js.
- **Interfaz:** web mínima (WhatsApp/Telegram quedan para "después"; WhatsApp tiene fricción de aprobación).
- **Nombre del repo (provisional):** `midaz`. Nombre público decidido: **MIDAZ** (ver DECISIONES.md). Al repo se le puede cambiar el nombre después.
- **Código nuevo:** nada copiado del proyecto previo de Abdiel ni de archivos privados. Se reusan **ideas** (orquestador, verificador, control de cupo), escritas desde cero en el repo nuevo.

### 2.3 Estructura del repo

```
midaz/
├── README.md                    # en inglés + resumen en español; corre en 5 comandos
├── LICENSE                      # MIT
├── .gitignore                   # .env, *.db, cache/, __pycache__, grabaciones privadas
├── .env.example                 # nombres de variables, SIN valores reales
├── .cursor/rules/               # (opcional) reglas para la herramienta de código
├── docker-compose.fuentes.yml   # Postgres "pos-db" y "erp-db" (fuentes A y B)
├── datos/
│   ├── LEEME_DATOS_DE_EJEMPLO.md   # "Súper La Esquina es ficticio"
│   ├── generar.py                  # semilla fija → CSV reproducibles
│   ├── calibracion.md              # qué patrones se diseñaron a propósito y por qué
│   └── salida/ejemplo_*.csv        # se generan; se pueden subir (son ficticios)
├── zetaris/
│   ├── PASOS.md                 # cómo levantar Zetaris y registrar las 3 fuentes
│   ├── cargar_fuentes.py        # CSV → pos-db / erp-db; copia gastos.csv
│   └── vistas.sql               # vistas semánticas (margen_por_producto, etc.)
├── app/
│   ├── main.py                  # FastAPI: /preguntar, /recibo/{id}, /salud
│   ├── config.py                # lee .env; falla si falta algo
│   ├── conectores/
│   │   ├── zetaris.py           # run_sql(sql) → filas, columnas, hash, hora
│   │   └── nightshift.py        # chat(lane, mensajes) → texto + receipt
│   ├── agente/
│   │   ├── intencion.py         # clasifica la pregunta (lane rápido)
│   │   ├── plantillas.py        # SQL fijo de las preguntas (sección 6)
│   │   ├── orquestador.py       # plan → SQL → redactar → fiscal → respuesta
│   │   ├── redactor.py          # pide JSON {frases, citas}
│   │   ├── fiscal.py            # re-ejecuta, chequea números, lane fiscal, borra
│   │   ├── no_se.py             # respuestas "no sé" + qué dato falta
│   │   ├── simulador.py         # simulación de precio (cuentas en SQL)
│   │   └── guardia_sql.py       # solo SELECT, solo vistas permitidas, LIMIT
│   ├── memoria/
│   │   └── hmem.py              # adaptador al motor H-MEM de Meterless
│   └── presupuesto/
│       ├── cache.py             # caché por hash (modelo + mensajes)
│       ├── tope.py              # tope diario de llamadas
│       └── replay.py            # graba y reproduce (LLM + Zetaris)
├── web/
│   ├── index.html  app.js  estilo.css
│   └── voz.js                   # opcional: micrófono y lectura en voz alta
├── tests/
│   ├── test_plantillas.py       # cada plantilla contra cifras esperadas
│   ├── test_fiscal.py           # borra frases con números inventados
│   ├── test_no_se.py            # carne sin costo, fuera de alcance, 0 filas
│   ├── test_simulador.py
│   ├── test_guardia_sql.py      # rechaza DELETE, DROP, tablas no permitidas
│   ├── test_hmem.py             # nuestras pruebas del motor
│   ├── test_lane_nemotron.py    # falla si el modelo que respondió no es Nemotron
│   ├── test_replay.py
│   └── test_sin_llaves.py       # busca patrones de llaves en el repo
├── scripts/
│   ├── smoke_test.py            # 3 PASS: Zetaris, Nightshift, consulta real
│   ├── demo.py                  # corre el guion del demo (vivo o replay)
│   └── revisar_secretos.sh      # gitleaks + grep en git log -p
├── evidencia/
│   ├── receipts.jsonl           # receipts de Nightshift saneados (sin llaves)
│   └── capturas/                # Zetaris, Nightshift Console, pytest
└── docs/
    ├── arquitectura.md
    ├── como_usamos_sponsors.md  # Zetaris, Meterless, NVIDIA + qué fue único
    └── cursor.md                # (opcional) cómo se construyó (herramienta de código)
```

---

## 3. Modelo de datos del minisúper (datos de ejemplo)

### 3.1 Antes de empezar: corregir una cifra del brief
El brief dice "vendí ₡3 millones este mes" con 4 empleados. **No cuadra:** solo la planilla de 4 personas con cargas sociales ronda ₡2 millones (monto de ejemplo; salarios mínimos 2026 **sin verificar**). Propuesta para que la historia sea creíble:
- **Ventas del mes: ~₡18 millones** (unos ₡600.000 por día, ~250 tiquetes de ~₡2.400).
- **Margen bruto promedio: ~19 %**, o sea **~₡3,4 millones** de ganancia bruta.
- **Gastos operativos: ~₡3,6 millones**, o sea **faltan ~₡180.000** en agosto. Así se mantiene la cifra del brief.
- Frase nueva para el demo: *"Vendí 18 millones este mes… ¿y por qué no me alcanza?"*

Todos estos montos son **metas de calibración** del generador. **La cifra que se dice en el video es la que devuelva Zetaris**, aunque no sea exactamente esa.

### 3.2 Las 3 fuentes y sus tablas

**Fuente A: POS (caja) → Postgres `pos-db`, base `pos`**
| Tabla | Columnas |
|---|---|
| `ventas_tiquetes` | `tiquete_id` (PK), `fecha` (DATE), `mes` (TEXT 'AAAA-MM'), `hora` (TIME), `caja` (INT), `medio_pago` ('efectivo','tarjeta','sinpe'), `cliente_id` (NULL o INT; para "clientes fieles" después) |
| `ventas_lineas` | `tiquete_id`, `linea`, `sku`, `cantidad` (NUMERIC), `precio_unitario` (NUMERIC, ₡ sin IVA), `descuento` (NUMERIC, ₡ total de la línea), `fecha`, `mes` |

**Fuente B: ERP (costos e inventario) → Postgres `erp-db`, base `erp`**
| Tabla | Columnas |
|---|---|
| `productos` | `sku` (PK), `nombre`, `categoria`, `subcategoria`, `unidad` ('un','kg','L'), `proveedor_id`, `canasta_basica` (BOOL), `activo` (BOOL) |
| `proveedores` | `proveedor_id`, `nombre`, `dias_entrega` |
| `costos` | `sku`, `vigente_desde` (DATE), `vigente_hasta` (DATE o NULL), `costo_unitario` (₡ sin IVA) — es la lista de precios del proveedor |
| `compras` | `compra_id`, `fecha`, `proveedor_id`, `sku`, `cantidad`, `costo_unitario` |
| `inventario` | `sku`, `fecha_corte`, `existencias` |

**Fuente C: gastos operativos → archivo CSV `ejemplo_gastos_operativos.csv`** (la "libreta del contador")
| Columna | Ejemplo |
|---|---|
| `mes` | '2026-08' |
| `rubro` | 'planilla', 'cargas_sociales', 'alquiler', 'electricidad', 'agua', 'internet_telefono', 'patente_municipal', 'contador_y_sistema', 'otros' |
| `descripcion` | 'Recibo ICE agosto' (texto de ejemplo) |
| `monto` | 412000 |

> Si Zetaris no puede leer un CSV como fuente (**sin verificar**), plan B: la fuente C pasa a un tercer Postgres (`gastos-db`). Siguen siendo 3 fuentes separadas.

**Simplificaciones que se declaran en el README (supuestos, no hechos):**
- Montos **sin IVA** (en CR la canasta básica tiene IVA reducido y el resto 13 %; para el MVP lo dejamos fuera y lo decimos).
- Sin merma ni robo.
- La **carne fresca no tiene costos cargados a propósito**: así existe el caso real de "no sé" ("no tengo el costo de la carne").

### 3.3 Cómo generar datos creíbles (`datos/generar.py`)
- **Semilla fija** (`random.seed(2026)`): todos ven las mismas cifras siempre.
- **~220 productos** en estas categorías. Rangos de margen inspirados en la **forma** del estudio noruego (Konkurransetilsynet 2025), no en datos de Costa Rica:

| Categoría | Ejemplos | Margen bruto del ejemplo | Volumen |
|---|---|---|---|
| Granos y básicos (canasta) | arroz, frijoles, azúcar, aceite, sal, harina | 3-8 % | muy alto |
| Lácteos y huevos | leche, natilla, queso, huevos | 8-17 % | alto |
| Carne fresca | posta, molida, pollo | **sin costo cargado** | medio |
| Embutidos | mortadela, salchichón | 15-25 % | medio |
| Pan | pan cuadrado, bollos | 15-25 % | alto |
| Bebidas sin alcohol | gaseosas 600 ml / 3 L, jugos, agua | 25-35 % | medio |
| Snacks y confites | papas, galletas, chocolates | 35-50 % | medio-bajo |
| Helados | paletas, potes | 35-45 % | bajo |
| Limpieza | jabón, cloro, papel higiénico | 18-28 % | medio |
| Cuidado personal | pasta de dientes, desodorante | 25-35 % | bajo |
| Frutas y verduras | tomate, papa, banano | 20-35 % | medio |

- **3 meses de ventas: julio, agosto y setiembre 2026**, con 3 momentos de la historia:
  - **Julio (línea base):** la ganancia apenas cubre los gastos.
  - **Agosto (el problema):** se venden **más unidades** que en julio (+4 %), pero la mezcla se va a la canasta básica (una "promo de arroz"), el **proveedor sube el aceite** sin que cambie el precio de venta y **sube la luz** (refrigeradores). Resultado: **faltan ~₡180.000**. Esto arma el momento "no es que vendió menos".
  - **Setiembre (después de la decisión):** se aplica la sugerencia de precio en ~6 productos de alto margen; sus unidades bajan ~5 % y la ganancia sube. Sirve para la memoria ("¿cómo me fue con lo de la Coca?").
- **Patrón 80/20:** el generador reparte la demanda (Pareto/Zipf) para que **~18-25 % de los productos haga ~80 % de la ganancia** y para que el **arroz sea #1 en unidades pero quede lejos (puesto ~40) en ganancia**.
- **Ruido realista:** más venta los viernes y sábados, quincenas (15 y 30), horas pico 7-9 am y 5-8 pm, precios terminados en ₡0 o ₡50, descuentos en ~3 % de las líneas.
- **Rotulado:** archivos `ejemplo_*.csv`, `LEEME_DATOS_DE_EJEMPLO.md`, franja fija en la web "DATOS DE EJEMPLO · Súper La Esquina es ficticio" y la misma frase en el video y el deck.
- **Honestidad:** `datos/calibracion.md` explica que los datos se **diseñaron** para mostrar un patrón conocido (alto volumen y bajo margen). Los jueces técnicos lo valoran; esconderlo sería peor.
- **Control a mano:** Abdiel saca las cifras clave en Excel desde los CSV (pareto, faltante de agosto, arroz vs helado). Son la "verdad esperada" para `tests/test_plantillas.py`.

---

## 4. Setup de Zetaris paso a paso y carga de datos

Responsable: **Abdiel** (con Josué en el paso 6). Máquina: la PC de Abdiel (31 GB RAM, Ryzen 5 5600G, 173 GB libres; según el kit, Docker no estaba instalado).

1. **Docker Desktop** (pide administrador). En Settings → Resources: ≥8 GB RAM y 4 CPU para Docker (lo que pide Zetaris según el kit).
2. **Ubuntu en WSL:** `wsl --install -d Ubuntu` en PowerShell como administrador. En Docker Desktop → Settings → Resources → WSL integration, activar Ubuntu.
3. **Registro en Zetaris** y seguir la guía oficial `zetaris.github.io/getting-started`: clonar su repo, `docker compose pull` (30-45 min) y `docker compose up -d`. Comandos exactos y nombre del script de verificación: **(sin verificar)**; el kit menciona `verify.sh` y una prueba "Pikachu OK".
4. **Crear la API key de Zetaris** en su interfaz y guardarla **solo** en `.env` (`ZETARIS_TOKEN`). Nunca en capturas.
5. **Probar el REST** desde Ubuntu:
   ```bash
   curl -s -X POST http://localhost:8888/api/v1.0/sql-editor/sqls/run \
     -H "Authorization: Bearer $ZETARIS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT 1"}'
   ```
   El endpoint sale del kit. El formato del header de auth y del cuerpo es **(sin verificar)**: copiarlo del AGENTS.md o de los ejemplos de la guía de Zetaris. **Listo cuando** devuelve una fila con 1.
6. **Levantar las fuentes A y B:** `docker compose -f docker-compose.fuentes.yml up -d` (dos Postgres: `pos-db` y `erp-db`, **en la misma red Docker que Zetaris**). Luego `python zetaris/cargar_fuentes.py` carga los CSV con `COPY`.
7. **Registrar las 3 fuentes en Zetaris** como data sources separados (Postgres `pos`, Postgres `erp`, archivo `gastos`). En la interfaz o por SQL, según la guía **(sin verificar)**. Ojo: dentro de Docker, el host es el nombre del contenedor (`pos-db`), no `localhost`.
8. **Crear las vistas semánticas** con `zetaris/vistas.sql` (sección 6.2). Si Zetaris tiene una capa semántica propia (USL), definirla ahí **(sin verificar cómo)**; si no, usar vistas SQL normales en un esquema `semantica`.
9. **Comprobar:** `SELECT COUNT(*)` en cada fuente y en `margen_por_producto`, y comparar las cifras clave con el Excel de control (±₡1).
10. **Capturas para la evidencia:** las 3 fuentes registradas, la vista y una consulta corriendo (sin token visible).

**Nombres de tablas en Zetaris:** la forma exacta de referirse a una tabla federada (por ejemplo `pos.public.ventas_lineas`) es **(sin verificar)**. Por eso `app/agente/plantillas.py` arma los nombres desde `.env` (`ZT_POS`, `ZT_ERP`, `ZT_GASTOS`, `ZT_SEM`) y no van fijos en el SQL.

**Plan B si Zetaris no levanta el miércoles:** el jueves en la mañana, Zetaris en AWS según la guía (costo **sin verificar**; el kit dice ~US$1 por 8 h). **Plan C** si no se puede federar Postgres: cargar los 3 CSV a Zetaris como 3 datasets separados. Es más débil para Michael Hay, pero sigue habiendo 3 fuentes y una vista que las une.

---

## 5. Nightshift + Nemotron

Responsable: **Josué**.

### 5.1 Setup
1. Instalar Meterless Nightshift según la guía de setup del evento.
2. Crear la llave en build.nvidia.com y pegarla **solo** en Nightshift → Providers. La app nunca la ve.
3. `GET /v1/models` y copiar los nombres **exactos** de los Nemotron disponibles. El kit menciona `nemotron-3.5-lightning` y `nemotron-3-super`: **(sin verificar)**.
4. Definir 2 lanes fijos (si Nightshift tiene "lanes" con nombre propio, usarlos; si no, el id exacto del modelo). **Nunca `meterless/auto`.**

| Lane | Variable `.env` | Para qué | Modelo |
|---|---|---|---|
| Rápido | `LANE_RAPIDO` | intención, redactar, conversar | Nemotron rápido **(sin verificar nombre)** |
| Fiscal | `LANE_FISCAL` | verificar cada frase; planear el "por qué" | Nemotron grande **(sin verificar nombre)** |

Si solo hay un Nemotron disponible, los dos lanes usan ese modelo con prompts y temperaturas distintas. Sigue siendo "un segundo lane Nemotron que verifica".

### 5.2 Llamada (patrón)
```python
cliente = OpenAI(
    base_url=os.environ["NIGHTSHIFT_URL"],          # p. ej. http://localhost:PUERTO/v1 (sin verificar)
    api_key=os.environ.get("NIGHTSHIFT_TOKEN", "x"), # si Nightshift pide token (sin verificar)
    default_headers={"meterless-app": "midaz", "meterless-scope": "user"},
)
r = cliente.chat.completions.create(model=lane, messages=mensajes, temperature=0)
if "nemotron" not in r.model.lower():
    raise LaneNoNemotron(r.model)   # se cae a propósito: nunca responder con otro modelo
```
Los headers `meterless-app` y `meterless-scope: user` vienen del kit.

### 5.3 Evidencia del modelo (receipt)
- Por cada llamada se guarda en `evidencia/receipts.jsonl`: hora, lane, `r.model`, `r.id`, tokens, latencia, hash del prompt y si salió de caché. **Sin** llaves, sin headers de auth y sin el contenido completo del prompt.
- Si Nightshift devuelve un id de run o un header de receipt propio, también se guarda **(sin verificar qué devuelve)**. Con ese id se busca la misma llamada en la **Nightshift Console** para la captura del video.
- La web muestra en cada recibo: *"Redactó: <modelo> · Verificó: <modelo> · vía Meterless Nightshift · id …"*.

### 5.4 Cupo (~400 solicitudes/día **compartidas**)
- **Presupuesto por pregunta: 3-4 llamadas** (intención 1, redactar 1, fiscal 1, "por qué" +1). Máximo 1 reintento. Muy por debajo de las 8-12 del brief.
- **Intención sin LLM primero:** palabras clave ("ganancia", "me alcanza", "precio", "carne") resuelven la mayoría. El lane rápido solo se usa si no hay coincidencia. Ahorra ~25 % del cupo.
- **Caché** SQLite: clave = sha256(modelo + mensajes + temperatura). Con temperatura 0, la misma pregunta sobre los mismos datos no gasta cupo.
- **Tope diario de la app:** `TOPE_DIARIO=150` llamadas (deja el resto para pruebas y para el otro proyecto). Al 80 % se avisa; al 100 % la API responde "modo replay" y no llama.
- **Pausar el otro proyecto** que usa la misma llave durante la semana.

### 5.5 Modo replay
- `MODO=grabar`: cada respuesta del LLM y de Zetaris se guarda en `replay/` con su hash.
- `MODO=replay`: se responde desde la grabación, **sin red**. La web muestra un distintivo **"REPLAY"**.
- Sirve para ensayar el demo sin gastar cupo y como respaldo si Nightshift o NVIDIA fallan el lunes.
- **Regla de honestidad:** el video se graba **en vivo**. Si alguna toma sale de replay, se rotula "replay de una ejecución real del <fecha>".

---

## 6. Diseño del agente

### 6.1 Flujo de una pregunta
1. **Intención** → una de: `pareto`, `volumen_vs_margen`, `cobertura`, `por_que`, `simular_precio`, `memoria`, `fuera_de_alcance`.
2. **Parámetros** validados en código (mes `^\d{4}-\d{2}$` y dentro de los meses que existen; alza de precio en ₡ entre 25 y 500; caída de unidades entre 0 y 30 %). Zetaris por REST quizá no acepte parámetros (**sin verificar**), así que se sustituyen en el servidor **solo** con valores ya validados.
3. **Ejecutar plantillas** en Zetaris. Cada resultado queda con `consulta_id`, SQL exacto, vista de origen, filas, hash de filas y hora.
4. **Redactar** (lane rápido). Recibe **solo** las filas y devuelve JSON:
   ```json
   {"frases": [
      {"texto": "23 de sus 214 productos hacen el 80 % de su ganancia.",
       "citas": [{"consulta": "q1_resumen", "fila": 0, "columna": "productos_80", "valor": 23}]}
    ],
    "recomendacion": {"texto": "...", "citas": [...]},
    "supuestos": ["Unidades bajan 5 % tras el alza (lo eligió usted)"]}
   ```
   Regla del prompt: **prohibido hacer cuentas**. Todo número que aparezca tiene que estar en una fila. Las plantillas ya traen calculadas las diferencias, los porcentajes y los faltantes.
5. **Fiscal** (sección 6.4).
6. **Respuesta:** 2-3 frases + 1 recomendación, cada una con su sello. Recibo al tocar.
7. **Memoria:** se guardan en H-MEM los hallazgos y, si el dueño dice "listo, lo hago", la decisión.

### 6.2 Vistas semánticas (`zetaris/vistas.sql`)
Los nombres con `${...}` se reemplazan desde `.env`. Dialecto SQL de Zetaris: se escribe SQL estándar con funciones de ventana; que las soporte todas es **(sin verificar)**. Para evitar problemas con funciones de fecha, el generador ya escribe la columna `mes` como texto.

```sql
-- Costo vigente para cada línea de venta; NULL si no hay costo (ej. carne)
CREATE VIEW ${SEM}.lineas_con_costo AS
SELECT v.mes, v.fecha, v.sku, p.nombre, p.categoria, p.canasta_basica,
       v.cantidad,
       v.cantidad * v.precio_unitario - v.descuento        AS venta_neta,
       c.costo_unitario,
       v.cantidad * c.costo_unitario                        AS costo_venta
FROM ${POS}.ventas_lineas v
JOIN ${ERP}.productos p ON p.sku = v.sku
LEFT JOIN ${ERP}.costos c
       ON c.sku = v.sku
      AND v.fecha >= c.vigente_desde
      AND (c.vigente_hasta IS NULL OR v.fecha < c.vigente_hasta);

-- LA vista semántica: margen por producto y mes
CREATE VIEW ${SEM}.margen_por_producto AS
SELECT mes, sku, nombre, categoria, canasta_basica,
       SUM(cantidad)                                         AS unidades,
       SUM(venta_neta)                                       AS ventas_netas,
       SUM(venta_neta) / NULLIF(SUM(cantidad), 0)            AS precio_promedio,
       MAX(costo_unitario)                                   AS costo_unitario,
       CASE WHEN COUNT(costo_unitario) < COUNT(*) THEN NULL
            ELSE SUM(venta_neta) - SUM(costo_venta) END      AS ganancia_bruta,
       CASE WHEN COUNT(costo_unitario) < COUNT(*) THEN NULL
            ELSE (SUM(venta_neta) - SUM(costo_venta)) / NULLIF(SUM(venta_neta), 0)
       END                                                   AS margen_pct,
       COUNT(costo_unitario) < COUNT(*)                      AS falta_costo
FROM ${SEM}.lineas_con_costo
GROUP BY mes, sku, nombre, categoria, canasta_basica;

-- Gastos por mes (fuente C)
CREATE VIEW ${SEM}.gastos_mes AS
SELECT mes, rubro, SUM(monto) AS monto FROM ${GASTOS}.gastos_operativos GROUP BY mes, rubro;
```
Nota: `MAX(costo_unitario)` es una simplificación cuando el costo cambia dentro del mes (el aceite en agosto). La ganancia sí usa el costo de cada línea, así que es exacta.

### 6.3 Plantillas SQL de las 3 preguntas (+ "por qué" y simulación)

**P1 — 80/20 de GANANCIA (con el contraste por volumen)**
```sql
-- q1_ranking
WITH g AS (
  SELECT sku, nombre, categoria, unidades, ganancia_bruta, margen_pct
  FROM ${SEM}.margen_por_producto
  WHERE mes = '${MES}' AND falta_costo = false
), r AS (
  SELECT g.*,
         ROW_NUMBER() OVER (ORDER BY ganancia_bruta DESC) AS puesto_ganancia,
         ROW_NUMBER() OVER (ORDER BY unidades DESC)       AS puesto_volumen,
         SUM(ganancia_bruta) OVER (ORDER BY ganancia_bruta DESC
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
           / SUM(ganancia_bruta) OVER ()                  AS acumulado_ganancia,
         COUNT(*) OVER ()                                 AS total_productos
  FROM g
)
SELECT * FROM r ORDER BY puesto_ganancia;

-- q1_resumen (sobre q1_ranking como subconsulta)
SELECT MIN(puesto_ganancia)                           AS productos_80,
       MAX(total_productos)                           AS total_productos,
       MIN(puesto_ganancia) * 1.0 / MAX(total_productos) AS pct_productos
FROM (/* q1_ranking */) r
WHERE acumulado_ganancia >= 0.80;
```
El mismo cálculo con `ORDER BY unidades` da el 80/20 de **volumen**. La frase "aha": *"El arroz es el #1 en unidades y el #N en ganancia"* sale de `puesto_volumen` y `puesto_ganancia` del arroz, en la misma fila.

**P2 — Mucho volumen, poco margen**
```sql
-- q2_grupos
WITH m AS (
  SELECT *, PERCENT_RANK() OVER (ORDER BY unidades DESC) AS rango_volumen
  FROM ${SEM}.margen_por_producto
  WHERE mes = '${MES}' AND falta_costo = false
)
SELECT CASE WHEN rango_volumen <= 0.20 AND margen_pct < 0.10 THEN 'mucho_volumen_poco_margen'
            WHEN rango_volumen >  0.50 AND margen_pct > 0.30 THEN 'poco_volumen_mucho_margen'
            ELSE 'resto' END                                  AS grupo,
       COUNT(*)                                               AS productos,
       SUM(unidades)                                          AS unidades,
       SUM(unidades) * 1.0 / SUM(SUM(unidades)) OVER ()       AS pct_unidades,
       SUM(ganancia_bruta)                                    AS ganancia,
       SUM(ganancia_bruta) * 1.0 / SUM(SUM(ganancia_bruta)) OVER () AS pct_ganancia
FROM m GROUP BY 1;
```
Frase esperada: *"Arroz, frijoles, azúcar y aceite son el 31 % de lo que vende y solo el 5 % de lo que gana"* (cifras de calibración; valen las que devuelva Zetaris). El redactor agrega el "por qué igual conviene tenerlos" (atraen clientes) como **opinión rotulada**, sin número y sin sello, con el ícono "consejo".

**P3 — ¿El margen cubre los gastos?**
```sql
-- q3_cobertura
WITH gb AS (
  SELECT SUM(ganancia_bruta) AS ganancia, SUM(ventas_netas) AS ventas,
         SUM(ganancia_bruta) / SUM(ventas_netas) AS margen_pct
  FROM ${SEM}.margen_por_producto WHERE mes = '${MES}' AND falta_costo = false
), go AS (
  SELECT SUM(monto) AS gastos FROM ${SEM}.gastos_mes WHERE mes = '${MES}'
), sc AS (
  SELECT SUM(ventas_netas) AS ventas_sin_costo, COUNT(*) AS productos_sin_costo
  FROM ${SEM}.margen_por_producto WHERE mes = '${MES}' AND falta_costo = true
)
SELECT gb.ganancia, gb.ventas, gb.margen_pct, go.gastos,
       gb.ganancia - go.gastos                    AS resultado,       -- negativo = faltante
       go.gastos / gb.margen_pct                  AS ventas_equilibrio,
       go.gastos / gb.margen_pct - gb.ventas      AS ventas_que_faltan,
       sc.ventas_sin_costo, sc.productos_sin_costo
FROM gb, go, sc;
```
La respuesta **siempre** aclara: "esto no incluye la carne, porque no tengo su costo (₡X en ventas)". Ese es el "no sé" parcial y honesto.

**P3b — ¿Por qué no me alcanza? (hipótesis que se confirman o se descartan)**
Plan fijo de 4 hipótesis, cada una con su plantilla, comparando `${MES}` con `${MES_ANT}`:
| Hipótesis | Plantilla | Se confirma si |
|---|---|---|
| H1 "Vendió menos" | `SUM(unidades)`, `SUM(ventas_netas)` por mes | unidades y ventas bajaron |
| H2 "Vendió más de lo que deja poco" | % de unidades y de ganancia de la canasta básica por mes | sube el % de unidades de canasta y baja el margen promedio |
| H3 "Subieron los gastos" | `gastos_mes` por rubro, diferencia entre meses | algún rubro sube > 5 % |
| H4 "Subió el costo del proveedor" | `costos` con `vigente_desde` en el mes + unidades vendidas de ese sku | hay alzas de costo sin alza de precio |

En los datos de ejemplo de agosto: **H1 se descarta en rojo** ("no vendió menos: vendió 4 % más"), y H2, H3 y H4 se confirman con su monto en ₡. El lane fiscal escribe el cierre ("lo que más pesó fue…") y lo apoya solo en los montos de las filas. Este es el corazón del Track 02: **explica por qué, con prueba**.

**P4 — Simulación de precio (sugerencia, decide el dueño)**
```sql
-- q4_candidatos: alto margen, buen volumen, no canasta básica
WITH c AS (
  SELECT sku, nombre, unidades, precio_promedio, costo_unitario, ganancia_bruta,
         (precio_promedio + ${ALZA} - costo_unitario) * unidades * (1 - ${CAIDA})
           - ganancia_bruta                               AS ganancia_extra
  FROM ${SEM}.margen_por_producto
  WHERE mes = '${MES}' AND falta_costo = false
    AND canasta_basica = false AND margen_pct >= 0.25 AND unidades >= 150
)
SELECT c.*,
       SUM(ganancia_extra) OVER (ORDER BY ganancia_extra DESC
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS extra_acumulada
FROM c ORDER BY ganancia_extra DESC LIMIT 20;
```
El código toma los primeros productos hasta que `extra_acumulada >= faltante` (de `q3_cobertura`). La frase: *"Si sube ₡100 estos 6 productos y vende 5 % menos de ellos, gana ₡X más al mes y cubre el faltante."* Los supuestos (₡100 y −5 %) salen como **supuestos**, en otra caja, y el dueño los puede cambiar ("¿y si bajo 10 %?"). "Poca sensibilidad al precio" se declara como supuesto (no es canasta básica), no como hecho medido.

### 6.4 El fiscal (lo que gana el Track 02)
Por cada frase de la respuesta:
1. **Re-ejecuta** en Zetaris cada SQL citado (conexión aparte) y compara el hash de las filas. Si cambió → frase fuera.
2. **Chequeo de números en código, sin LLM:** extrae cada número del texto (₡, %, enteros, "18 millones") y busca su valor citado; tolerancia solo de redondeo (lo que se muestra con 0 decimales ±0,5; los % ±0,05 puntos). Un número sin cita → frase fuera.
3. **Lane Nemotron fiscal:** recibe la frase y **solo** las filas citadas, y responde JSON `{"soportada": true/false, "motivo": "..."}`. Si dice false → frase fuera.
4. **Resultado:**
   - Pasa los 3 → sello **"✓ Verificado"** (hora de Zetaris + los dos modelos).
   - Frase eliminada → en la vista normal no se muestra; en "bajo el capó" aparece **tachada en rojo** con el motivo. (Para el video: se fuerza un caso con una frase inventada a propósito en un test visible, y el fiscal la borra.)
   - Si no queda ninguna frase → **"no sé"**.
5. **Opiniones sin número** (como "conviene tener el arroz porque atrae clientes") se permiten solo con el ícono "consejo" y sin sello. El fiscal rechaza cualquier consejo que traiga un número.

### 6.5 "No sé" (cuándo y cómo)
| Caso | Cómo se detecta | Qué dice |
|---|---|---|
| Falta el dato | `falta_costo = true` en lo que se pregunta (carne) | "No sé cuánto gana con la carne: no tengo el costo de compra. Si me pasa las facturas del proveedor, lo calculo." |
| Fuera del alcance | intención `fuera_de_alcance` (pronósticos, competencia, impuestos) | "Eso no lo puedo responder con sus datos. Sí puedo decirle…" + 2 preguntas que sí sabe |
| Sin filas | la plantilla devuelve 0 filas (mes que no existe) | "No tengo ventas de diciembre. Tengo julio a setiembre." |
| El fiscal borró todo | 0 frases sobreviven | "No pude comprobar una respuesta con los datos; prefiero no adivinar." |
| Zetaris caído | error o timeout | "No puedo consultar sus datos ahora; no le voy a dar números de memoria." |

### 6.6 Preguntas libres (stretch, no MVP)
Nemotron genera el SQL **solo** sobre las vistas `${SEM}.*`. `guardia_sql.py` (sqlglot) exige un único SELECT, solo tablas permitidas y `LIMIT 200`; si no pasa → "no sé". Pasa por el mismo fiscal. Si vamos atrasados, se recorta (sección 13).

---

## 7. Experiencia conversacional y voz mínima

**Principio:** la pantalla es una conversación. Nada de dashboards.

- **Una sola columna** tipo WhatsApp. Arriba, la franja "DATOS DE EJEMPLO · Súper La Esquina (ficticio)".
- **Primer mensaje del agente:** "Hola, Marta. Tengo sus ventas de julio a setiembre. Puede preguntarme:" + 3 botones (**¿Qué productos me dan la plata?** · **¿Me alcanza para los gastos?** · **¿Qué precio subo?**). En el demo los botones evitan errores de tipeo.
- **Respuesta:** 2-3 frases cortas + 1 recomendación. Cada frase con número lleva un **sello pequeño ✓**. Al tocarlo se abre el **recibo** (panel deslizable):
  - la frase,
  - el **SQL exacto** (con resaltado),
  - la fuente: vista `margen_por_producto` ← POS + ERP (+ gastos),
  - las **filas** (máx. 10 visibles, la fila citada resaltada),
  - la hora de la consulta en Zetaris y el hash,
  - "Redactó: <Nemotron …> · Verificó: <Nemotron …> · vía Meterless Nightshift · id …".
- **Botón "bajo el capó"** (para jueces y video): muestra los pasos en orden (intención → SQL → filas → fiscal), las hipótesis confirmadas en verde y descartadas en rojo, y las frases tachadas.
- **Decisión:** al final de una sugerencia, "¿Lo aplico como decisión?" → [Sí, lo hago] [No]. "Sí" la guarda en H-MEM (no toca ningún sistema; actuar dentro del ERP es "después").
- **Idioma:** variable `IDIOMA=es|en`. Los números y el SQL son los mismos; solo cambia la redacción. **Recomendación:** grabar el demo en **inglés** (jueces angloparlantes) y mostrar 5 segundos en español ("hecho para Doña Marta"). Lo decide Abdiel; el requisito exacto de idioma y subtítulos está **(sin verificar)** en HackOS.
- **Voz (si da tiempo, máx. 3 h el domingo):** Web Speech API del navegador.
  - Entrada: botón de micrófono → `SpeechRecognition` (`es-CR` / `en-US`) → texto en la caja → enviar.
  - Salida: `speechSynthesis` lee **solo** las frases verificadas, nunca las tachadas.
  - Funciona en Chrome/Edge; si el navegador no lo soporta, el botón se esconde. No gasta cupo NVIDIA.
- **Memoria en la conversación:** "Un mes después" es un selector de **fecha simulada** (`HOY=2026-10-01`), rotulado así en pantalla. Al preguntar "¿Cómo me fue con lo de la Coca?", H-MEM recupera la decisión y el agente **vuelve a consultar** Zetaris (setiembre vs agosto). La memoria aporta el **qué** y el **cuándo**; los números siempre salen de SQL nuevo.

---

## 8. Meterless Engine: H-MEM (recomendado) y la prueba

### 8.1 Por qué H-MEM
- Es la memoria jerárquica, justo lo que pide el producto: recordar hallazgos y decisiones del negocio.
- Sam Cummings (que probablemente esté detrás de los motores) valora "contexto y memoria".
- Da una escena fuerte en el video ("¿cómo me fue con lo de la Coca?").

### 8.2 Qué guarda (niveles)
- **Negocio** (largo plazo): "Súper La Esquina, datos jul-set 2026, carne sin costos".
- **Hallazgos:** `{tipo: "pareto", mes, resumen, consulta_id, hash_filas, fecha}`.
- **Decisiones del dueño:** `{tipo: "decision_precio", skus, alza, fecha_decision, consulta_origen}`.
- **Conversación** (corto plazo): últimas preguntas, para entender "¿y la de 600 ml?".

**Regla:** H-MEM **nunca** es fuente de un número en la respuesta. Recuerda qué se decidió; las cifras se vuelven a sacar de Zetaris. Esto se prueba (abajo).

### 8.3 Integración
- Instalar el motor según la documentación de Meterless e integrarlo con el prompt que traiga la guía (sirve en cualquier herramienta de código). Nombre del paquete, API y conformance suite: **(sin verificar)**. Confirmarlo el **jueves**, no el sábado.
- `app/memoria/hmem.py` es un adaptador delgado (`guardar_hallazgo`, `guardar_decision`, `recordar(pregunta)`), para que el resto del código no dependa de la API exacta.

### 8.4 Las pruebas que deben pasar (en pantalla)
1. **Conformance suite oficial de H-MEM** (si existe; **sin verificar**), corriendo verde con nuestro adaptador.
2. `test_hmem.py` (nuestras):
   - `test_guarda_y_recupera_decision`: guardar "subir Coca 3 L ₡100 el 2026-08-31" y recuperarla con "¿cómo me fue con lo de la Coca?".
   - `test_sobrevive_reinicio`: reiniciar el proceso y la decisión sigue ahí.
   - `test_no_mezcla_niveles`: un hallazgo no aparece como decisión.
   - `test_memoria_no_es_fuente_de_numeros`: si la memoria dice "ganó ₡500.000" pero Zetaris dice otra cosa, la respuesta usa Zetaris y el fiscal elimina la cifra de memoria.
   - `test_olvida_si_se_pide`: "olvide esa decisión" la borra.
3. Comando del video: `pytest -v tests/test_hmem.py` (+ conformance) → **todo verde** en pantalla.

### 8.5 Segundo motor (opcional, domingo)
**Markovian** para el flujo "¿por qué no me alcanza?": cada hipótesis es un paso con contexto acotado (pregunta + resumen del paso anterior + filas del paso actual). Solo si H-MEM ya está verde el sábado. Si no, se menciona como "siguiente paso", **no** como usado. Plan B si H-MEM no se puede integrar el sábado: cambiar a Markovian o Scout Intent (el que tenga la suite más simple). **Un motor con pruebas verdes es obligatorio.**

---

## 9. Tareas por persona y por día (con "listo cuando")

Check-in diario: **9:00 pm, 15 min** (videollamada o chat). Cada día tiene un **portón**: si no se pasa, se aplica la sección 13 esa misma noche.

### Mié 21-oct (6:00 pm - medianoche) — Fierros listos
| Quién | Tarea | Listo cuando |
|---|---|---|
| Abdiel | Docker Desktop (admin) + Ubuntu WSL + registro Zetaris + `docker compose pull` | `docker ps` muestra Zetaris arriba (o el pull terminó) |
| Abdiel | Leer la sección 06 de HackOS (requisitos de entrega) y anotar diferencias con este plan | Nota con 3-5 líneas en el chat del equipo |
| Josué | Nightshift instalado, llave NVIDIA en Providers, `/v1/models` | Lista de modelos Nemotron con nombres exactos, copiada en el chat |
| Josué | 1 llamada real con lane Nemotron fijo y los headers | Respuesta con `model` que contiene "nemotron" (guardada sin llaves) |
| Josué | Repo **público** nuevo (después de las 6 pm): `.gitignore`, `.env.example`, LICENSE, README en blanco, gitleaks como pre-commit | Primer commit visible en GitHub |

### Jue 22-oct — Inscripción + smoke test
| Quién | Tarea | Listo cuando |
|---|---|---|
| **Ambos** | **Equipo inscrito en HackOS, Track 02, una cuenta por persona — antes del mediodía** (cierra 5:59 pm) | Captura de la página del equipo |
| Abdiel | Zetaris verificado + API key + `curl` `SELECT 1` por REST | Devuelve 1 fila |
| Abdiel | `datos/generar.py` según la sección 3. Excel de control con las cifras clave | CSV generados; Excel con pareto, faltante de agosto, arroz vs helado y hipótesis H1-H4 |
| Abdiel | Marca: nombre público, 2 colores, tipografía | Decisión escrita |
| Josué | `conectores/zetaris.py`, `conectores/nightshift.py`, receipts, caché, tope | Tests unitarios con mocks pasan |
| Josué | Confirmar API e instalación de H-MEM y si hay conformance suite | Nota: paquete, comando de la suite, ejemplo mínimo corriendo |
| Josué | `scripts/smoke_test.py` | **3 PASS:** Zetaris `SELECT 1`, Nightshift Nemotron, consulta a una tabla cargada |

**Portón jueves 9 pm:** smoke test 3 PASS. Si no → se recorta todo lo que no sean las 3 preguntas (sección 13, nivel 1).

### Vie 23-oct — Datos federados + agente
| Quién | Tarea | Listo cuando |
|---|---|---|
| Abdiel (+ Josué 1 h) | Fuentes A y B en Postgres, C como CSV; las 3 registradas en Zetaris; `vistas.sql` aplicado | `margen_por_producto` devuelve las cifras del Excel (±₡1) |
| Abdiel | Set de prueba: 15 preguntas con su respuesta esperada (incluye 4 "no sé" y 2 trampas con números inventados) | `tests/golden.yaml` en el repo |
| Josué | `plantillas.py` (P1, P2, P3, P3b), `orquestador.py`, `redactor.py`, `fiscal.py`, `no_se.py` | Por CLI, las 3 preguntas responden con citas y sello |
| Josué | `POST /preguntar` devuelve JSON con frases, citas y recibos | `curl` muestra un recibo completo |
| Josué | `test_plantillas.py`, `test_fiscal.py`, `test_no_se.py` | ≥12 de 15 del set de prueba pasan |

**Portón viernes 9 pm:** P1, P2 y P3 responden de punta a punta contra Zetaris real.

### Sáb 24-oct — Memoria + interfaz (el día más importante)
| Quién | Tarea | Listo cuando |
|---|---|---|
| Josué | **H-MEM integrado + conformance + `test_hmem.py`** | `pytest -v` todo verde, con captura |
| Josué | `simulador.py` (P4) + decisión "Sí, lo hago" → H-MEM | "¿Qué precio subo?" devuelve los productos, la extra en ₡ y los supuestos |
| Josué | `guardia_sql.py` + `test_lane_nemotron.py` + `test_sin_llaves.py` | Tests verdes |
| Abdiel | `web/` (chat, botones, sello, recibo, "bajo el capó", franja de ejemplo) conectada a `/preguntar` | En el navegador: P1 → tocar el sello → se ven SQL, filas, hora y modelos |
| Abdiel | Logo y estilo aplicados | Captura que se pueda poner en el deck |

**Portón sábado 9 pm:** demo de punta a punta en la web, **en vivo**, con P1, P2, P3, P4, un "no sé" y H-MEM verde. **Si H-MEM no está verde, el domingo en la mañana se cambia de motor (8.5).**

### Dom 25-oct — Robustez + guion + voz
| Quién | Tarea | Listo cuando |
|---|---|---|
| Josué | P3b "por qué" con H1 descartada en rojo; fecha simulada para "un mes después" | La escena del video corre completa |
| Josué | Errores: Zetaris caído, 429 de NVIDIA, timeout, modelo no Nemotron (se cae a propósito) | Cada caso tiene test y un mensaje claro |
| Josué | Modo grabar/replay + `scripts/demo.py` | `MODO=replay python scripts/demo.py` corre el guion sin red |
| Josué | Instalación desde cero en otra carpeta siguiendo solo el README | Funciona; se corrige el README |
| Josué (stretch) | Markovian con su prueba | Solo si todo lo anterior está listo |
| Abdiel | Voz (máx. 3 h; si no sale a las 4 pm se deja) | Pregunta dicha → respuesta leída en voz alta |
| Abdiel | Guion final + diagrama + borrador del deck | Ensayo cronometrado ≤3:15 |
| Ambos | 2 ensayos completos en vivo, grabando en modo `grabar` | Grabación de respaldo lista |

**Congelar funciones: domingo 10 pm.** Desde ahí solo se arreglan errores.

### Lun 26-oct — Video, deck, README
| Quién | Tarea | Listo cuando |
|---|---|---|
| Abdiel | Grabar el video por escenas (OBS, 1080p, audio limpio), editar y subtitular | MP4 de 3:00-3:45, subido donde pida HackOS (formato **sin verificar**) |
| Abdiel | Slide deck final (sección 10.2) | PDF exportado + link |
| Abdiel | Parte visual del README (capturas, GIF del recibo) | Se ve bien en GitHub |
| Josué | `docs/como_usamos_sponsors.md` + sección en el README | Zetaris, Meterless (Nightshift + H-MEM), NVIDIA y "qué fue único" |
| Josué | Revisión de secretos: gitleaks + `git log -p | grep -iE "nvapi|sk-|token|bearer"` | 0 hallazgos |
| Josué | Tag `v1.0-rc` + clone limpio en otra máquina o carpeta | Corre siguiendo el README |
| Ambos | Revisar el video con la lista de no negociables (sección 1) | Los 5 aparecen en el video |

Nota: el juzgamiento abre el lunes a las 6 pm. Si HackOS deja **editar** la entrega (**sin verificar**), conviene subir una versión completa el lunes en la noche (por el desempate) y reemplazarla el martes si hace falta.

### Mar 27-oct — Entregar
| Quién | Tarea | Listo cuando |
|---|---|---|
| Ambos | Repaso final con el checklist (sección 10.1) | Todo marcado |
| Abdiel | **Entregar antes de las 12:00 m.d.** | Confirmación de HackOS (captura) |
| Josué | Tag `v1.0` + release en GitHub | Release visible |
| Ambos | Abrir todos los links en ventana privada (video, deck, repo) | Abren sin pedir permiso |
| Ambos | **No hacer más commits** después de entregar (por si la regla lo penaliza; **sin verificar**) | — |

---

## 10. Entrega

### 10.1 Checklist
**Reglas**
- [ ] Equipo en HackOS, Track 02, 2 cuentas (una por persona), antes del 22-oct 5:59 pm.
- [ ] Requisitos de la sección 06 de HackOS leídos y comparados con esta lista.
- [ ] Repo público, primer commit después del 21-oct 6:00 pm, nada privado ni del proyecto previo de Abdiel copiado.

**Video (1-4 min)**
- [ ] Duración entre 3:00 y 3:45 (dentro de 1-4 min).
- [ ] Muestra los 5 no negociables: recibo SQL, 3 fuentes + vista, 2 lanes Nemotron + receipt, H-MEM verde, cifra en ₡.
- [ ] Rótulo "datos de ejemplo" visible.
- [ ] Sin llaves, tokens ni `.env` en pantalla (revisar cuadro por cuadro las escenas de terminal y de Console).
- [ ] Subtítulos; idioma según la regla de HackOS.

**Slide deck**
- [ ] Todas las secciones de 10.2, incluyendo "qué fue único".
- [ ] Cada cifra con su fuente en letra pequeña.

**Repo y README**
- [ ] README: problema, usuario, demo (GIF), cómo correrlo (5 comandos), arquitectura, decisiones.
- [ ] Sección "How we used Zetaris / Meterless / NVIDIA" + "What's unique".
- [ ] Dónde está cada cosa en el código (rutas a `fiscal.py`, `hmem.py`, `vistas.sql`).
- [ ] `pytest -v` verde, con captura en el README.
- [ ] `evidencia/receipts.jsonl` (saneado) + capturas de Zetaris y de Nightshift Console.
- [ ] (Opcional) nota de cómo se construyó; Cursor no es obligatorio.
- [ ] Supuestos declarados (sin IVA, sin merma, carne sin costo a propósito, datos calibrados).
- [ ] `.env.example` sin valores reales; gitleaks en 0.
- [ ] Tag `v1.0`.

### 10.2 Esquema del slide deck (12 slides, en inglés)
1. **Portada:** nombre + "Stop making decisions blind." + "Track 02 · The Agent That Can Explain Why" + equipo.
2. **El problema:** las 3 cifras (47 % por intuición — H&R Block; 1 de cada 3 no sabe su margen — YouGov/FreeAgent; 50 % de las empresas de CR cierra antes de 5 años — BCCR) + "2.1 % net margin in grocery" (FMI).
3. **Doña Marta:** persona, un día de trabajo, la frase "trabaja 12 horas y no sabe qué producto le paga el salario".
4. **La solución:** sin interfaz, solo conversación. 3 preguntas. "Every claim has a receipt. No proof, no answer."
5. **El momento "aha":** arroz vs helado (puesto en volumen vs puesto en ganancia) + el % de unidades vs el % de ganancia.
6. **Explica por qué:** las hipótesis H1-H4, con H1 descartada en rojo; el recibo abierto.
7. **Zetaris (data harness):** 3 fuentes → federado, sin ETL → vista semántica `margen_por_producto` → SQL por REST. Captura.
8. **Meterless + NVIDIA:** Nightshift como proveedor único; lane rápido Nemotron redacta, lane fiscal Nemotron verifica y borra; receipt; caché, tope y replay. Captura de la Console.
9. **H-MEM:** qué recuerda y la regla "la memoria no es fuente de números" + captura de las pruebas en verde.
10. **(Opcional) Cómo se construyó:** herramienta de código usada (Cursor no es obligatorio ni da créditos).
11. **Impacto:** la cifra en ₡ (datos de ejemplo) + mercado (97,4 % de las empresas de CR son pyme — MEIC) + competencia y hueco (dashboards en inglés atados a Shopify/Square vs conversación en español con prueba).
12. **Visión y cierre:** recordatorios de recompra, clientes fieles, el agente actuando en el ERP **con aprobación**. "The interface disappears; the conversation stays." Links: repo, video.

**Qué fue único (texto para el README y el slide 8):** "Nemotron doesn't just chat: one lane decides and writes, a second lane audits every sentence against Zetaris rows and deletes what it can't prove. All math happens in governed SQL over federated sources; memory (H-MEM) remembers decisions but is never allowed to be a source of numbers."

---

## 11. Guion del demo (3 min, video)

Narración en inglés (aquí en español para Abdiel). Las cifras son de **calibración**; se usan las que devuelva Zetaris el día de la grabación.

| Tiempo | Imagen | Voz / texto en pantalla |
|---|---|---|
| **0:00-0:20** El dolor | Doña Marta (ilustración o actriz) cerrando caja. Texto: "DATOS DE EJEMPLO" | "Marta sold 18 million colones this month. She works 12 hours a day. And she doesn't know why the money doesn't cover the bills." Cifra: **47 % of small business owners run mostly on gut feeling** (H&R Block). |
| **0:20-0:50** Pregunta 1 | Chat (o voz): "Which products actually make me money?" | Respuesta: "23 of your 214 products make 80 % of your profit. Rice is your #1 seller, but #41 in profit." Tocar el sello → recibo: SQL, vista `margen_por_producto`, filas, hora, "Written by Nemotron · Verified by Nemotron · via Meterless Nightshift". |
| **0:50-1:30** "Aha" + por qué | "Why don't I have enough this month?" → se abre "bajo el capó" | Hipótesis: **H1 "you sold less" → REJECTED en rojo** ("you sold 4 % more units"). H2 confirmada: más canasta básica (31 % de unidades, 5 % de la ganancia). H3: la luz subió ₡X. H4: el aceite subió ₡Y sin cambiar el precio. Una frase con número inventado aparece **tachada por el fiscal**. |
| **1:30-2:05** ¿Me alcanza? + precio | "Do I cover my expenses?" → "You're short ₡180,000 this month." "What price should I raise?" | "Raise these 6 high-margin items by ₡100. Assuming you sell 5 % less of them, you gain ₡X a month and close the gap." Supuestos en su caja. Botón "Yes, I'll do it" → guardado en memoria. |
| **2:05-2:20** "No sé" | "How much do I make on fresh meat?" | "I don't know. I don't have the purchase cost for meat. Send me the supplier invoices and I'll tell you." |
| **2:20-2:35** Memoria | Rótulo "One month later (simulated date)". "How did the Coke price change go?" | H-MEM recuerda la decisión; nueva consulta: "You sold 6 % fewer units and made 9 % more on them." Con recibo. |
| **2:35-2:55** Bajo el capó | Diagrama (5 s) → Zetaris con 3 fuentes y la vista (4 s) → Nightshift Console con el lane Nemotron (4 s) → terminal `pytest -v` verde, H-MEM incluido (7 s) | "Three separate sources federated in Zetaris, no ETL. Two fixed Nemotron lanes through Meterless Nightshift. H-MEM memory inside the product, tested." |
| **2:55-3:10** Cierre | Pantalla negra, cifra grande | "In this sample store: **₡2.16 million a year** was slipping away, and Marta never knew why. Now she does, with proof." (= faltante mensual × 12; usar la cifra real de Zetaris y decir "sample data"). **"Stop deciding blind."** |

Consejos de grabación: se graba por escenas, en vivo, con 2 tomas de cada una. Tener el modo replay grabado como respaldo. Cursor del mouse grande. Zoom al recibo. Nada de terminales con variables de entorno visibles.

---

## 12. Riesgos y planes B

| # | Riesgo | Señal temprana | Plan B |
|---|---|---|---|
| 1 | Docker/Zetaris no levanta en la PC de Abdiel | Miércoles 11 pm sin `docker ps` | Jueves temprano: Zetaris en AWS (costo **sin verificar**) |
| 2 | Zetaris no federa Postgres o CSV | Viernes 2 pm sin las 3 fuentes registradas | Plan C: 3 datasets separados dentro de Zetaris + la vista que los une; decirlo con honestidad en el README |
| 3 | SQL de Zetaris sin alguna función de ventana | Error en P1/P2 | Reescribir con subconsultas; último recurso: el acumulado se calcula en Python **sobre filas de Zetaris**, y se documenta en el recibo |
| 4 | Cupo NVIDIA agotado | Tope al 80 % antes de las 6 pm | Caché + replay + intención por palabras clave; pausar el otro proyecto |
| 5 | Nightshift enruta a un modelo que no es Nemotron | `test_lane_nemotron` falla | Fijar el id exacto; la app se cae en vez de responder con otro modelo |
| 6 | H-MEM no se puede integrar o no tiene suite | Sábado 2 pm sin verde | Cambiar a Markovian o Scout Intent; un motor verde es obligatorio |
| 7 | El LLM inventa números | El fiscal borra muchas frases | Bajar a frases fijas tipo plantilla rellenadas con los valores (el LLM solo elige cuál); se pierde naturalidad pero no confianza |
| 8 | Datos poco creíbles | Abdiel o el amigo dueño lo nota | Ajustar los rangos; pedirle al amigo que valide la **estructura** (no sus datos) |
| 9 | La voz se come el tiempo | Domingo 4 pm sin voz | Se recorta; el chat con botones alcanza |
| 10 | Fuga de llaves | gitleaks o una revisión del video | Rotar la llave de inmediato, limpiar el historial y volver a grabar la escena |
| 11 | Algo se cae durante la grabación | — | Tomas por escena + replay rotulado |
| 12 | Uno de los dos se enferma o no puede | — | Este plan está escrito para que el otro siga; prioridades en la sección 13 |
| 13 | Problema con la marca "Jarvis" | — | Nombre público alternativo desde el jueves |

---

## 13. Qué recortar si vamos atrasados (en este orden)

**Nivel 1 (primero en salir):**
1. Voz.
2. Markovian (segundo motor).
3. Preguntas libres con SQL generado.
4. Selector de idioma (dejar solo inglés en la UI del video o solo español con subtítulos).

**Nivel 2:**
5. Escena "un mes después" con datos de setiembre (H-MEM se demuestra solo con la prueba y un recuerdo simple dentro de la misma conversación).
6. P4 simulación: queda solo como frase con 1 producto ("si sube ₡100 la Coca 3 L, gana ₡X más").
7. Panel "bajo el capó" bonito → lista simple de pasos en texto.

**Nunca se recorta (son los no negociables):**
- Recibo SQL por frase con sello.
- 3 fuentes en Zetaris + `margen_por_producto`.
- 2 lanes Nemotron (redactor + fiscal que borra) con receipt.
- Un motor Meterless con pruebas verdes.
- "No sé" con el caso de la carne.
- La cifra en ₡ sobre datos de ejemplo rotulados.
- Video + deck + README.

---

## 14. Pendiente de verificar (lista corta para el jueves)
- [ ] Sección 06 de HackOS: formato del video, idioma y subtítulos, si se puede editar la entrega, commits después de entregar.
- [ ] Nombres exactos de los modelos Nemotron en Nightshift y si existe el concepto de "lane" con nombre.
- [ ] URL base de Nightshift, si pide token y qué receipt o id devuelve.
- [ ] Formato exacto del REST de Zetaris (auth y cuerpo) y cómo se nombran las tablas federadas.
- [ ] Si Zetaris lee CSV como fuente y si tiene capa semántica (USL) usable en local.
- [ ] Paquete, API y conformance suite de H-MEM.
- [ ] ~~Premio de Cursor~~: resuelto 2026-10-22, Cursor es opcional y no da créditos.
- [ ] Salarios y tarifas de ejemplo razonables para CR 2026 (solo para que los datos se vean creíbles; siguen siendo ficticios).
