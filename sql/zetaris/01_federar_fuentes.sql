-- HU-04: federar las 3 fuentes SEPARADAS en Zetaris. La opcion A se corrio en la PC de Abdiel el 2026-10-22; la opcion B sigue sin verificar.
-- Sintaxis tomada de zetaris/getting-started docs/guides/zetaris-lightning-sql-commands.md (5.2, 5.3, 4.x).
-- Requiere usuario administrador. Correr una sentencia por vez (SQL Editor o python -m midas.zetaris_client "...").
-- Ningun usuario/contrasena va en este archivo: se escriben solo en el SQL Editor de la PC de Abdiel.
-- Los CSV tienen que estar en una ruta que vea el contenedor `driver` (montaje o volumen) (sin verificar cual).

-- Opcion A (simple, recomendada para el gate): 3 Lightning DB de archivos, una por fuente.
CREATE LIGHTNING DATABASE midaz_pos DESCRIBE BY "MIDAZ_ventas_POS_SAMPLE_DATA";
CREATE LIGHTNING FILESTORE TABLE ventas_pos FROM midaz_pos FORMAT CSV OPTIONS (
  path "/home/zetaris/customer-data/shared/ventas_pos.csv", header "true", delimiter ",", inferSchema "true");

CREATE LIGHTNING DATABASE midaz_inventario DESCRIBE BY "MIDAZ_costos_inventario_SAMPLE_DATA";
CREATE LIGHTNING FILESTORE TABLE costos_inventario FROM midaz_inventario FORMAT CSV OPTIONS (
  path "/home/zetaris/customer-data/shared/costos_inventario.csv", header "true", delimiter ",", inferSchema "true");

CREATE LIGHTNING DATABASE midaz_finanzas DESCRIBE BY "MIDAZ_gastos_operativos_SAMPLE_DATA";
CREATE LIGHTNING FILESTORE TABLE gastos_operativos FROM midaz_finanzas FORMAT CSV OPTIONS (
  path "/home/zetaris/customer-data/shared/gastos_operativos.csv", header "true", delimiter ",", inferSchema "true");

-- Con la opcion A: MIDAZ_SCHEMA_MAP=pos=midaz_pos,inventario=midaz_inventario,finanzas=midaz_finanzas
-- (Zetaris consulta file tables como <database>.<table>.)

-- Opcion B (lo propuesto en #003): ventas en un Postgres propio, registrado como datasource.
-- CREATE DATASOURCE pg_pos DESCRIBE BY "PostgreSQL" OPTIONS (
--   jdbcdriver "org.postgresql.Driver", jdbcurl "jdbc:postgresql://<host>:5432/<db>",
--   username "<usuario>", password "<se escribe en el editor, nunca aca>");
-- Con la opcion B: MIDAZ_SCHEMA_MAP=pos=pg_pos.public,inventario=midaz_inventario,finanzas=midaz_finanzas (sin verificar)

-- Prueba de cada fuente por separado (deben dar 1 fila cada una):
-- SELECT COUNT(*) FROM midaz_pos.ventas_pos;
-- SELECT COUNT(*) FROM midaz_inventario.costos_inventario;
-- SELECT COUNT(*) FROM midaz_finanzas.gastos_operativos;
-- Y despues, desde la raiz del repo: MIDAZ_ENGINE=zetaris python run.py check
