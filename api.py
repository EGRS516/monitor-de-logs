import os
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import docker
import pymongo
from dotenv import load_dotenv

# Cargar variables de entorno (útil para desarrollo local fuera de Docker)
load_dotenv()

app = FastAPI(
    title="Docker Monitor API", 
    description="API para recolectar, almacenar y visualizar el estado de contenedores Docker"
)

# Servir archivos estáticos (CSS, JS) para la interfaz visual
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de MongoDB
# En Docker, la URI apunta al nombre del servicio 'mongodb' definido en docker-compose
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:adminpassword@localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "infra_monitor")
COLLECTION_NAME = "container_status"

try:
    # Conexión persistente a MongoDB
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]
    mongo_client.server_info() # Validación de conexión inmediata
except Exception as e:
    print(f"⚠️ Alerta: No se pudo conectar a MongoDB. La persistencia no estará disponible: {e}")
    db = None

# Configuración del cliente Docker
# Accede al Docker Engine a través del socket montado /var/run/docker.sock
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"⚠️ Alerta: Error al conectar con el socket de Docker: {e}")
    docker_client = None

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Sirve el Dashboard visual principal."""
    return FileResponse("static/index.html")

@app.post("/collect")
def collect_docker_stats():
    """
    Escanea el estado actual de todos los contenedores en el host.
    Guarda un 'snapshot' de la información en MongoDB.
    """
    if not docker_client:
        raise HTTPException(status_code=500, detail="El cliente Docker no está disponible (revisa el socket).")
    if db is None:
        raise HTTPException(status_code=500, detail="La base de datos MongoDB no está disponible.")

    try:
        # Listamos todos los contenedores (activos e inactivos)
        containers = docker_client.containers.list(all=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicar con Docker Daemon: {str(e)}")

    snapshot_time = datetime.datetime.utcnow()
    records = []

    for c in containers:
        # Extraemos etiquetas de imagen o ID si no tiene tags
        tags = c.image.tags if hasattr(c.image, "tags") and c.image.tags else [c.image.id]
        records.append({
            "container_id": c.short_id,
            "name": c.name,
            "image": tags[0],
            "status": c.status, # 'running', 'exited', 'paused', etc.
            "state_dict": c.attrs.get("State", {}), # Detalles técnicos (exit codes, OOM)
            "timestamp": snapshot_time
        })
    
    if records:
        try:
            collection.insert_many(records)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al persistir datos en MongoDB: {str(e)}")

    return {
        "message": "Snapshot de infraestructura guardado exitosamente.",
        "containers_processed": len(records),
        "timestamp": snapshot_time
    }

@app.get("/stats")
def get_docker_stats(limit: int = 50):
    """
    Recupera los registros históricos de la base de datos.
    Ordenados por fecha descendente (más recientes primero).
    """
    if db is None:
        raise HTTPException(status_code=500, detail="La conexión a MongoDB no está disponible.")
    
    try:
        # Excluimos el ID de Mongo para la respuesta JSON
        cursor = collection.find({}, {"_id": 0}).sort("timestamp", pymongo.DESCENDING).limit(limit)
        results = list(cursor)
        return {
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el historial de MongoDB: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Arranque del servidor ASGI
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
