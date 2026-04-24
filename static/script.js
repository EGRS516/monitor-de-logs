/**
 * Lógica del Dashboard de Docker Monitor
 * Gestiona la comunicación con la API y la actualización dinámica de la UI.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const refreshBtn = document.getElementById('refreshBtn');
    const collectBtn = document.getElementById('collectBtn');
    const statsGrid = document.getElementById('statsGrid');
    const historyBody = document.getElementById('historyBody');
    const loadingOverlay = document.getElementById('loadingOverlay');

    /**
     * Muestra u oculta la capa de carga durante operaciones asíncronas.
     */
    const showLoading = (show) => {
        if (show) loadingOverlay.classList.add('active');
        else loadingOverlay.classList.remove('active');
    };

    /**
     * Formatea una cadena de fecha ISO a un formato legible en español.
     */
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    /**
     * Obtiene los datos históricos y actuales de la API.
     */
    const fetchStats = async () => {
        try {
            const response = await fetch('/stats?limit=30');
            const result = await response.json();
            
            if (result.data) {
                renderDashboard(result.data);
            }
        } catch (error) {
            console.error('Error al obtener estadísticas:', error);
            alert('Error de conexión con el servidor.');
        }
    };

    /**
     * Dispara una nueva recolección de datos en el servidor.
     */
    const collectData = async () => {
        showLoading(true);
        try {
            const response = await fetch('/collect', { method: 'POST' });
            const result = await response.json();
            
            if (response.ok) {
                // Si la recolección es exitosa, actualizamos la vista
                await fetchStats();
            } else {
                alert(`Error: ${result.detail || 'No se pudo recolectar la información'}`);
            }
        } catch (error) {
            console.error('Error en la recolección:', error);
            alert('Error al conectar con la API.');
        } finally {
            showLoading(false);
        }
    };

    /**
     * Renderiza las tarjetas de estado actual y la tabla de historial.
     * @param {Array} data - Lista de registros provenientes de MongoDB.
     */
    const renderDashboard = (data) => {
        // Limpiamos el contenido previo
        statsGrid.innerHTML = '';
        historyBody.innerHTML = '';

        if (data.length === 0) {
            statsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No hay datos disponibles. Haz clic en "Recolectar Ahora" para empezar.</p>';
            return;
        }

        // Extraemos los contenedores únicos del snapshot más reciente
        const latestTimestamp = data[0].timestamp;
        const latestContainers = data.filter(item => item.timestamp === latestTimestamp);

        // Renderizar tarjetas de estado actual
        latestContainers.forEach(container => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const statusClass = container.status === 'running' ? 'status-running' : 'status-exited';
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="container-name">${container.name}</span>
                    <span class="status-badge ${statusClass}">${container.status}</span>
                </div>
                <div class="card-body">
                    <div class="info-row">
                        <span class="info-label">ID</span>
                        <span class="info-value">${container.container_id}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Imagen</span>
                        <span class="info-value">${container.image}</span>
                    </div>
                </div>
                <div class="timestamp">Última actualización: ${formatDate(container.timestamp)}</div>
            `;
            statsGrid.appendChild(card);
        });

        // Rellenar tabla de historial
        data.forEach(item => {
            const tr = document.createElement('tr');
            const statusClass = item.status === 'running' ? 'status-running' : 'status-exited';
            
            tr.innerHTML = `
                <td style="font-weight: 600;">${item.name}</td>
                <td style="color: var(--text-secondary); font-size: 0.8rem;">${item.image}</td>
                <td><span class="status-badge ${statusClass}">${item.status}</span></td>
                <td style="font-family: monospace; font-size: 0.8rem;">${formatDate(item.timestamp)}</td>
            `;
            historyBody.appendChild(tr);
        });
    };

    // Listeners de eventos
    refreshBtn.addEventListener('click', fetchStats);
    collectBtn.addEventListener('click', collectData);

    // Carga inicial al abrir la página
    fetchStats();
});
