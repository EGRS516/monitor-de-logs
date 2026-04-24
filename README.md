# 🐳 Docker Monitor Dashboard

Una solución elegante y moderna para monitorear el estado de tus contenedores Docker en tiempo real. Este proyecto recolecta métricas de tus contenedores locales y las almacena en una base de datos MongoDB para su análisis histórico, presentándolas en un Dashboard visual de alta fidelidad.

## 🚀 Inicio Rápido

Todo el sistema está contenedorizado. Solo necesitas tener **Docker** y **Docker Compose** instalados.

1. **Clonar y Levantar:**
   ```bash
   docker compose up -d --build
   ```

2. **Acceder al Dashboard:**
   Abre tu navegador en: [http://localhost:8000](http://localhost:8000)

## 🛠️ Arquitectura del Sistema

El proyecto se compone de tres piezas fundamentales trabajando en armonía:

1.  **Dashboard Visual (Frontend)**: Interfaz moderna construida con HTML5, CSS3 (Glassmorphism) y Vanilla JS. Permite visualizar el estado actual y el historial de eventos.
2.  **API de Monitoreo (FastAPI)**: El cerebro que interactúa con el Docker Engine de tu host a través del socket `/var/run/docker.sock`.
3.  **Base de Datos (MongoDB)**: Almacena de forma persistente cada "snapshot" de tus contenedores, permitiendo auditoría y seguimiento histórico.

## 📊 Endpoints de la API

Si prefieres interactuar con la API directamente:

*   `GET /`: Carga el Dashboard visual.
*   `POST /collect`: Realiza un escaneo inmediato de Docker y guarda los resultados en Mongo.
*   `GET /stats`: Recupera los últimos registros históricos (soporta el parámetro `?limit=N`).
*   `GET /docs`: Documentación interactiva (Swagger UI).

## 💡 ¿Por qué MongoDB?

A diferencia de un simple comando `docker ps`, este sistema utiliza MongoDB para:
*   **Historial**: Saber qué pasó con tus servicios mientras no estabas mirando.
*   **Auditoría**: Registrar códigos de salida y errores.
*   **Persistencia**: Los datos sobreviven a reinicios de la aplicación.

---
Desarrollado con ❤️ para un monitoreo de infraestructura más limpio y visual.
