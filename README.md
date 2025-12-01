# ETL: PokeAPI → MongoDB (RAW) → MySQL (SQL)

Proyecto educativo con ETL claramente separado en tres etapas:

- **EXTRACT**: consume PokeAPI y guarda JSON crudo (raw) en MongoDB.
- **TRANSFORM**: lee el raw desde MongoDB, estandariza campos y genera un CSV "transformado".
- **LOAD**: carga el CSV transformado en una base de datos MySQL (SQL).

## Estructura del proyecto

```text
etl/
  common/
    config.py
    db.py
  extract/
    extract.py
  transform/
    transform.py
  load/
    load.py
main.py
requirements.txt
.env.example
```

## Prerrequisitos

- Python 3.9+
- MongoDB en local (o una URI accesible)
- MySQL en local (usuario con permisos para crear base de datos) o una instancia accesible

## Preparación rápida

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Opcional: editar .env para ajustar variables
```

Asegúrate de que MongoDB está corriendo (por defecto en `mongodb://localhost:27017`).
Configura `DATABASE_URL` para MySQL en `.env`. La base de datos indicada en la URL se creará automáticamente si no existe.

## Ejecución

- Solo extracción (RAW a MongoDB):
  
  ```bash
  python main.py extract
  ```

- Solo transformación (MongoDB RAW → CSV transformado):
  
  ```bash
  python main.py transform
  ```

- Solo carga (CSV transformado → MySQL):
  
  ```bash
  python main.py load
  ```

- Pipeline completo:
  
  ```bash
  python main.py run
  ```

## Qué hace cada etapa (en esta aplicación)

- **EXTRACT**
  - Llama a `GET /pokemon?limit=N` de PokeAPI para obtener la lista inicial.
  - Recupera el detalle de cada Pokémon con su `url` individual.
  - Guarda el JSON crudo (sin transformar) en MongoDB colección `pokemon_raw`, usando `id` como clave natural (upsert con `replace_one`).
  - Propósito: persistir la fuente original tal cual, para auditoría y reprocesos.

- **TRANSFORM**
  - Lee documentos RAW desde MongoDB (excluyendo `_id`).
  - Proyecta y estandariza a un esquema tabular simple:
    - `id`: entero del PokeAPI.
    - `name`: convertido a MAYÚSCULAS.
    - `height` en metros (dm → m), `weight` en kilogramos (hg → kg), `base_experience` numérico.
    - `types`: lista aplanada a texto separado por comas.
    - `primary_type`: primer elemento de `types` (si existe).
    - `abilities`: lista aplanada a texto separado por comas.
  - Escribe el resultado en `data/transformed/pokemon.csv` con cabecera consistente.
  - Propósito: generar una vista limpia y homogénea lista para cargas analíticas/relacionales.

- **LOAD**
  - Asegura que la base de datos MySQL exista (la crea si no está).
  - Crea la tabla `POKEMON` si no existe (InnoDB, utf8mb4). Columnas `height DECIMAL(5,2)`, `weight DECIMAL(7,2)`.
  - Inserta/actualiza filas desde el CSV con `INSERT ... ON DUPLICATE KEY UPDATE` usando `id` como clave primaria.
  - Propósito: disponibilizar datos estandarizados en SQL para consultas y reporting.

## Resultados

- RAW en MongoDB: colección `pokemon_raw` (por defecto en DB `etl_demo`).
- Transformado en archivo: `data/transformed/pokemon.csv`.
- SQL en MySQL: base de datos (tomada de `DATABASE_URL`), tabla `POKEMON`.

Nota: Los archivos CSV generados están ignorados por `.gitignore` y no se versionan.

### Verificación en MySQL

```sql
-- Desde cliente MySQL:
USE pokemon; -- o la base definida en la URL
SELECT COUNT(*) FROM POKEMON;
SELECT id, name, primary_type FROM POKEMON ORDER BY id LIMIT 10;
```

## EDA (Jupyter Notebook)

- **Ubicación**: carpeta `EDA/`, notebook `RAW_EDA.ipynb`.
- **Objetivo**: análisis exploratorio de datos RAW desde MongoDB.
- **Visualizaciones**: barras y torta (tipos primarios), histogramas de `height`, `weight`, `base_experience`, y dispersión altura vs. peso con ajuste lineal.
- **Cómo correrlo (mismo entorno del proyecto)**:
  
  ```bash
  # en la raíz del proyecto
  source .venv/bin/activate
  pip install -r requirements.txt 
  jupyter notebook EDA/RAW_EDA.ipynb
  ```
  
- **Salida**: los gráficos se muestran inline en el notebook. Si necesitas archivos, puedes usar `plt.savefig(...)` en las celdas.
- **Notas**: asegúrate de tener `.env` con `MONGO_URI`, `MONGO_DB`, `MONGO_RAW_COLLECTION`.
- Comentarios y logs en inglés para buenas prácticas.
- Cada etapa está aislada en su propia carpeta y módulo.

## Notas didácticas

- Código breve y fácil de leer.
- Comentarios y logs en inglés para buenas prácticas.
- Cada etapa está aislada en su propia carpeta y módulo.
