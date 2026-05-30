# TPO VetSalud — Base de Datos II

Trabajo Práctico Obligatorio — Base de Datos II — ITBA — 2026 1C.

Sistema de gestión para la clínica veterinaria VetSalud S.A. con persistencia políglota sobre dos motores NoSQL de paradigmas distintos.

## Motores

- **MongoDB 7** — modelo documental para las entidades del dominio (pacientes, propietarios, veterinarios, consultas, vacunaciones, cirugías, stock farmacéutico).
- **Neo4j 5** — modelo de grafo para representar las relaciones entre entidades (propietario→paciente, paciente→consulta, vet→sucursal, etc.) y resolver las consultas que se expresan naturalmente como traversals.

## Consultas y servicios

| # | Descripción | Motor |
|---|---|---|
| Q1 | Pacientes activos de un propietario | Neo4j |
| Q2 | Consultas en estado seguimiento | MongoDB |
| Q3 | Historial clínico unificado de un paciente | MongoDB |
| Q4 | Propietarios con más de un paciente | Neo4j |
| Q5 | Veterinarios con consultas en los últimos 60 días | MongoDB |
| Q6 | Pacientes con vacunas vencidas | MongoDB |
| Q7 | Top 5 diagnósticos más frecuentes | MongoDB |
| Q8 | Productos con menos de 50 unidades en stock | MongoDB |
| Q9 | Consultas de control con costo menor a $5.000 | MongoDB |
| Q10 | Pacientes atendidos por sucursal | Neo4j |
| Q11 | Ingresos por veterinario en el mes actual | MongoDB |
| Q12 | Propietarios sin consultas en el último año | Neo4j |
| Q13 | ABM de propietarios | Mongo + Neo4j |
| Q14 | Alta de consulta | Mongo + Neo4j |
| Q15 | Descuento de stock farmacéutico | MongoDB |

Cada consulta vive en su propio módulo `src/consultas/qNN_*.py` y expone una función `ejecutar(args=None)` que devuelve el resultado como `list[dict]` o `dict`.

## Datos

- Datasets originales de la cátedra en `datasets_vetsalud/`.
- Diez registros adicionales por colección en `data/extras/`.
- Dataset propio de cirugías (entidad mencionada en el enunciado sin CSV provisto) en `data/cirugias.csv` y `data/extras/cirugias_extras.csv`.

---

## Guía de Instalación y Ejecución desde Cero

A continuación se detallan los pasos para configurar, inicializar y ejecutar todo el entorno de la aplicación.

### 1. Requisitos Previos

Asegúrate de tener instalados los siguientes componentes:
- [Docker y Docker Desktop](https://www.docker.com/) (para levantar las bases de datos NoSQL).
- [Python 3.10+](https://www.python.org/) (se recomienda Python 3.11).
- Un cliente de Git (opcional, para clonar el repositorio).

---

### 2. Levantar las Bases de Datos (Docker)

La persistencia de datos utiliza MongoDB 7 y Neo4j 5. Contamos con una configuración automatizada mediante Docker Compose.

Para levantar ambos motores, ejecuta el siguiente comando en la raíz del proyecto:

```bash
docker-compose up -d
```

Esto descargará e iniciará los contenedores necesarios en segundo plano. Puedes verificar que estén corriendo con:
```bash
docker compose ps
```

---

### 3. Configurar el Entorno Virtual de Python

Es buena práctica utilizar un entorno virtual para aislar las dependencias del proyecto.

1. **Crear el entorno virtual:**
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual:**
   - **En Windows (PowerShell / CMD):**
     ```powershell
     venv\Scripts\activate
     ```
   - **En Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

### 4. Configurar las Variables de Entorno

El proyecto lee la configuración de conexión de un archivo `.env`. 

Copia el archivo de ejemplo para crear tu archivo `.env`:
```bash
cp .env.example .env
```
*(En Windows, si usas PowerShell/CMD clásico, puedes hacer: `copy .env.example .env`)*

El archivo `.env` por defecto viene preconfigurado para conectarse localmente a los puertos mapeados por Docker:
```ini
MONGO_URI=mongodb://localhost:27017
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=vetsalud123
```

---

### 5. Cargar y Poblar Datos Iniciales (Seed / ETL)

Contamos con un script orquestador que realiza la ingesta, limpieza e interconexión de datos desde los archivos CSV originales hacia MongoDB y Neo4j de manera idempotente.

Con el entorno virtual activo, ejecuta:
```bash
python -m src.etl.seed
```

Esto poblará ambas bases de datos con los datasets originales y las extensiones adicionales.

---

### 6. Ejecutar el Servidor Web (FastAPI)

Una vez que las bases de datos estén activas y los datos cargados, puedes iniciar el servidor web utilizando Uvicorn:

```bash
uvicorn api:app --reload
```

El servidor web se levantará en: **http://127.0.0.1:8000**

---

### 7. Acceso a la Documentación Interactiva

Una vez encendido el servidor, abre tu navegador y dirígete a:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Aquí encontrarás la interfaz interactiva de **Swagger UI** donde podrás probar cada una de las consultas del sistema en tiempo real.

