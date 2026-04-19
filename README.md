# Docker Infrastructure & Logs Monitor

Una herramienta interna para la observabilidad y monitoreo escrita en Python. Este proyecto extrae el ciclo de vida y los metadatos de los contenedores Docker en el host y utiliza MongoDB para el almacenamiento en series de tiempo para su posterior procesamiento, todo auto-orquestado en segundo plano usando Cron Jobs tradicionales adaptados a un ambiente moderno.

## Funcionalidades
1. **API con FastAPI**: Proporciona endpoints limpios y documentados.
2. **Conexividad con Docker Daemon**: Extrae el estado, ciclo de vida e imagen de todos los contenedores actuantes en la infraestructura.
3. **Persistencia de Eventos**: Usa MongoDB para almacenar cada snapshot y crear un registro histórico real.
4. **Programación Automática**: Tareas en segundo plano confiables auto-inyectadas en el crontab del sistema.

## Pasos Rápidos

### 1. Activar tu ecosistema y Base de Datos

Puedes usar el archivo docker-compose suministrado para levantar rápidamente la instancia de guardado en el puerto `27017` por defecto.

```bash
docker-compose up -d
```

### 2. Configurar el Entorno de Python

Crea y accede un entorno virtual con las versiones en aislamiento y lanza el servidor.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py
```
> La API quedará escuchando en `http://localhost:8000`

### 3. Ejecutar y Consultar

Para comprobar en el instante el funcionamiento interactuando con la API y los servicios de infraestructura bajo cubiertas:
- Para pedir a los procesos Python que hablen con Docker y Mongo para recolectar data: `curl -X POST http://localhost:8000/collect`
- Para ver los registros y auditoría: `curl http://localhost:8000/stats`
- Tienes interfaz **Swagger** de prueba en `http://localhost:8000/docs`

### 4. Automatizar la Recolección (Cron)

Para conseguir el poder de monitoreo donde el programa opera transparentemente haciendo recortes del rendimiento a lo largo del tiempo, instala el demonizador.

Ejecuta en otra terminal:
```bash
chmod +x setup_cron.sh
./setup_cron.sh
```
> Esto añadirá un trabajo de fondo que le indicará a tu sistema operativo host que pingue ininterrumpidamente a la API cada 5 minutos mediante el endpoint de recolección (`/collect`), manteniendo tu base guardada con métricas actualizadas, demostrando una comprensión de cómo auto-operar la infraestructura de servidor de backend.
