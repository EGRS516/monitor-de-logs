import os
import datetime
from fastapi import FastAPI, HTTPException
import docker
import pymongo
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Docker Monitor API", 
    description="API para recolectar y mostrar logs/estado de contenedores de Docker"
)

# Configurar MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:adminpassword@localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "infra_monitor")
COLLECTION_NAME = "container_status"

try:
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]
    mongo_client.server_info() # Comprobar la conexión rápidamente
except Exception as e:
    print(f"Error conectando a MongoDB. Asegúrate de levantar el contenedor: {e}")
    db = None

# Configurar cliente Docker (usando el socket local por defecto del host)
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Error inicializando el cliente Docker: {e}")
    docker_client = None

@app.get("/")
def read_root():
    return {
        "message": "Docker Monitor API arriba.",
        "endpoints": {
            "Recolección Manual": "POST /collect",
            "Ver Historial/Logs": "GET /stats",
            "Documentación API": "GET /docs"
        }
    }

@app.post("/collect")
def collect_docker_stats():
    """Conecta a la API de Docker, recolecta el estado actual de los contenedores y lo guarda en MongoDB."""
    if not docker_client:
        raise HTTPException(status_code=500, detail="El cliente Docker no se pudo conectar al socket local.")
    if db is None:
        raise HTTPException(status_code=500, detail="La conexión a MongoDB no está disponible.")

    try:
        # Obtenemos todos (incluyendo parados/caídos) para monitoreo
        containers = docker_client.containers.list(all=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comunicando con Docker daemon: {str(e)}")

    snapshot_time = datetime.datetime.utcnow()
    records = []

    for c in containers:
        tags = c.image.tags if hasattr(c.image, "tags") and c.image.tags else [c.image.id]
        records.append({
            "container_id": c.short_id,
            "name": c.name,
            "image": tags[0],
            "status": c.status, # e.g. 'running', 'exited'
            "state_dict": c.attrs.get("State", {}), # Diccionario con exit codes, OOM killed, etc
            "timestamp": snapshot_time
        })
    
    if records:
        try:
            collection.insert_many(records)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error guardando logs en MongoDB: {str(e)}")

    return {
        "message": "Recolección de procesos Docker guardada en Base de Datos exitosamente.",
        "containers_processed": len(records),
        "timestamp": snapshot_time
    }

@app.get("/stats")
def get_docker_stats(limit: int = 50):
    """Obtiene los últimos estados registrados de los contenedores para su análisis."""
    if db is None:
        raise HTTPException(status_code=500, detail="La conexión a MongoDB no está disponible.")
    
    try:
        # Recuperamos con los más recientes primero
        cursor = collection.find({}, {"_id": 0}).sort("timestamp", pymongo.DESCENDING).limit(limit)
        results = list(cursor)
        return {
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo logs desde MongoDB: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Inicia el servidor
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
