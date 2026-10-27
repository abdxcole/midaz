# 09 · Equipo y reparto (acuerdos del 2026-10-22)

Acuerdos tomados el **2026-10-22** por Abdiel. Este documento dice **quién hace qué y dónde**. Si choca con otro doc en reparto de tareas, manda este; en alcance técnico manda [`06-plan-midas.md`](06-plan-midas.md).

## Roles

| Quién | Rol | Tareas |
|---|---|---|
| **Abdiel** | Dueño y quien decide | Decide alcance, prioridades y desempates. Aprueba todo lo que sea en vivo, público o irreversible. |
| **VERA** | Coordinadora y auditora | Coordina el reparto y el checkpoint diario. Guion final de **2:30 en inglés con subtítulos** (tarea **#15**). **Auditoría final**, incluida la auditoría del **README** antes de la entrega. |
| **ARGOS** | Product manager + UX | UI de MIDAZ con **botones accionables** (#10); UX de los **recibos** (#6); flujo de **datos en vivo** (#8); número final **₡/mes** + golden set **X/15** (#19); esquema de las **3 fuentes** (#2); **datos de demo** (#5); casos de las **reglas de calidad** (#4); definiciones **USL** (#3); **README** (#13). Motor **H-MEM** (HU-15) junto con Josué. |
| **IRIS** | Dirección visual | Dirige y audita la identidad visual de MIDAZ (logo, mensaje) y el video. |
| **PIXEL** | Imágenes | Genera las imágenes que pida IRIS. |
| **MOTION** | Video | Edita el video del pitch (sobre el guion de VERA, con dirección de IRIS). |
| **Josué** | Backend | Zetaris / Nightshift + Nemotron; federar las **3 fuentes**; implementar las **reglas de calidad** en código; motor **H-MEM** Meterless (**HU-15**) junto con ARGOS. |

### Lo que NO se hace

- **No hay bot nuevo de datos** (ahorra créditos). Los datos los define ARGOS y los cablea Josué.
- **MIDAZ no tiene landing.** La demo es la app y el video.

## Fechas clave (hora de Costa Rica)

| Hito | Cuándo |
|---|---|
| Checkpoint diario | Todos los días, **9:00 PM** |
| **Code freeze** | **Lunes 26 de octubre, 12:00 PM** |
| Entrega interna (para auditoría de VERA) | **Martes 27 de octubre, 12:00 PM** |
| **Entrega oficial** | **Martes 27 de octubre, 5:45 PM** |

## Estado de HU-00 (Zetaris)

- Zetaris **corre localmente en la PC de Abdiel**: **4 servicios sanos**, UI en `http://localhost:3000`.
- **Pendiente:** un **token de API / ID de organización** para hacer el `SELECT` por REST. Sin eso, HU-00 no está cerrada.
- Pasos y detalles: [`08-hu00-zetaris.md`](08-hu00-zetaris.md).

## Para Josué: qué hacer y dónde

1. **Cerrar HU-00 (Zetaris REST).** Conseguir el token de API y el ID de organización y probar un `SELECT` por REST.
   - Dónde: [`scripts/zetaris-up.ps1`](../scripts/zetaris-up.ps1) y [`docs/08-hu00-zetaris.md`](08-hu00-zetaris.md).
   - Variables (solo nombres; valores en tu `.env` local, nunca en el repo): `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`, `MIDAZ_SCHEMA_MAP` (opcional). Ver [`.env.example`](../.env.example).
2. **Nightshift + Nemotron.** Dejar MIDAZ hablando con Nemotron vía Nightshift.
   - Variables: `NIGHTSHIFT_URL`, `NIGHTSHIFT_TOKEN`, `METERLESS_RUNTIME_TOKEN`. La llave NVIDIA va **solo** en Nightshift > Providers (regla 10 de [`AGENTS.md`](../AGENTS.md)).
3. **Federar las 3 fuentes.** Con el esquema que entrega ARGOS (#2) y los datos de demo (#5), unirlas en Zetaris.
   - Dónde: consultas en [`sql/`](../sql/) (ver [`sql/README.md`](../sql/README.md)); punto de entrada [`run.py`](../run.py).
4. **Reglas de calidad en código.** Implementar los casos que define ARGOS (#4), partiendo de [`sql/01_calidad_datos.sql`](../sql/01_calidad_datos.sql) y [`sql/02_sin_costo_detalle.sql`](../sql/02_sin_costo_detalle.sql).
5. **Motor H-MEM Meterless (HU-15), con ARGOS.** Historia y criterios en [`docs/06-plan-midas.md`](06-plan-midas.md) (HU-15); test `tests/test_hmem.py` corriendo en `python run.py test`.
6. **Antes del code freeze (lun 26, 12:00 PM CR)** todo lo anterior en `main`. Avisos y bloqueos por el canal interno del equipo; estado en el checkpoint de las 9:00 PM.

Reglas: nada de secretos en el repo; si algo no está verificado, marcarlo **(sin verificar)**.
