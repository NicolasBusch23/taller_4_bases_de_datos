# ETL: FreeToGame API → MongoDB (RAW) → MySQL (SQL)

Proyecto académico propuesto por la materia Bases de Datos que implementa un proceso ETL (Extract, Transform, Load) a partir de datos obtenidos desde una API pública de videojuegos gratuitos, con almacenamiento intermedio en MongoDB y carga final en una base de datos relacional MySQL.

Se tomó como guía el repositorio https://github.com/mframosg/Python---III compartido por el profesor de la asignatura

## Estructura del proyecto

El proyecto sigue una arquitectura ETL claramente separada en tres etapas:

- EXTRACT: consumo de la API FreeToGame y almacenamiento de los datos crudos (RAW) en MongoDB.
- TRANSFORM: limpieza, selección y estandarización de variables relevantes, con generación de un archivo CSV.
- LOAD: carga de los datos transformados en una base de datos MySQL para análisis estructurado.

## API Utilizada

- Nombre: FreeToGame API
- URL base: https://www.freetogame.com/api/games
- Descripción: API pública que provee información sobre videojuegos gratuitos, incluyendo género, plataforma, desarrollador y fecha de lanzamiento.
- Formato de respuesta: JSON


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
# Se sugiere crear un archivo .env para ajustar variables. Debe seguir el formato de .env.example
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
  - Consume la API FreeToGame.
  - Recupera un conjunto limitado de videojuegos según configuración.
  - Almacena los datos crudos en MongoDB sin modificaciones.
  - Objetivo: Conservar la fuente original para trazabilidad y reprocesamiento.

- **TRANSFORM**
  - Lee los datos RAW desde MongoDB.
  - Selecciona las variables:
      title
      genre
      platform
      developer
      release_date
      short_description
  - Objetivo: Generar un archivo CSV con 190 registros en data/transformed/juegos.csv. siguiendo las especificaciones anteriores

- **LOAD**
  - Crea la tabla juegos en MySQL si no existe.
  - Inserta los datos desde el CSV.
  - Convierte la fecha de lanzamiento a tipo DATE para mayor comodidad en MySQL.
  - Objetivo: disponibilizar los datos en un sistema relacional para consultas SQL.

## Resultados
  - MongoDB: colección con datos crudos (RAW).
  - CSV transformado: data/transformed/juegos.csv.
  - MySQL: tabla juegos con datos estructurados.

Nota: Los archivos CSV generados están ignorados por `.gitignore`.

### Verificación en MySQL

```sql
-- Desde cliente MySQL:
USE juegos_db; -- o la base definida en la URL
SELECT COUNT(*) FROM JUEGOS;
```

## EDA (Jupyter Notebook)

- **Ubicación**: carpeta `EDA/`, notebook `analisis.ipynb`.
- **Objetivo**: Realizar un análisis exploratorio de los datos transformados entregados en el archivo .csv
- **Visualizaciones**: Gráfico de Torta, Barras y de Tendencia.
- **Cómo correrlo (mismo entorno del proyecto)**:
  
  ```bash
  # en la raíz del proyecto
  source .venv/bin/activate
  pip install -r requirements.txt 
  jupyter notebook EDA/analisis.ipynb
  ```
  
- **Salida**: los gráficos se muestran inline en el notebook. Si necesitas archivos, puedes usar `plt.savefig(...)` en las celdas.
- **Notas**: asegúrate de tener `.env` con `MONGO_URI`, `MONGO_DB`, `MONGO_RAW_COLLECTION`.
- Comentarios y logs en inglés para buenas prácticas.
- Cada etapa está aislada en su propia carpeta y módulo.

## Notas didácticas

- Código breve y fácil de leer.
- Comentarios y logs en inglés para buenas prácticas.
- Cada etapa está aislada en su propia carpeta y módulo.
