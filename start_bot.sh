#!/bin/bash

SERVICE_NAME="telegram_bot"

echo "🔹 Starting the Telegram bot service..."
sudo systemctl start ${SERVICE_NAME}
echo "✅ Service ${SERVICE_NAME} started successfully!"