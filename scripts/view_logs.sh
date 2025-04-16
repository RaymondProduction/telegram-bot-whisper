#!/bin/bash

SERVICE_NAME="telegram_bot"
LOG_FILE="/var/log/${SERVICE_NAME}.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

echo "🔹 Showing logs for ${SERVICE_NAME}..."
tail -f "$LOG_FILE"