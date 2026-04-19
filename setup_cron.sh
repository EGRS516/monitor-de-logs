#!/bin/bash

# Este script programa de forma automática (Cron job) la recolección de logs en segundo plano.
# Por defecto se programará para que haga un POST a la API local cada 5 minutos.

echo ">>> Configurando Cronjob para el Monitor de Infraestructura..."

# Asegurarse de que curl o wget están disponibles
if ! command -v curl &> /dev/null; then
    echo "ERROR: 'curl' no pudo ser encontrado. Por favor instálalo para que el cronjob funcione o asegúrate de que esté en tu PATH"
    exit 1
fi

# Creamos el comando que llamará al endpoint de la API
CRON_CMD="curl -X POST http://localhost:8000/collect -s > /dev/null 2>&1"
# Expresión cron: cada 5 minutos
CRON_JOB="*/5 * * * * $CRON_CMD"

# Comprobamos si ya existe el cronjob para este comando para no duplicarlo
(crontab -l 2>/dev/null | grep -F "$CRON_CMD") > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ El cronjob ya está configurado en tu sistema. Se omiten los cambios."
else
    # Añadimos el nuevo cronjob concatenando los registros del cron antiguo
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cronjob añadido exitosamente. Se ejecutará cada 5 minutos."
    echo "Comando programado: $CRON_CMD"
fi

echo "Para revisar tus Cron Jobs activos puedes escribir: crontab -l"
echo "¡Completado!"
