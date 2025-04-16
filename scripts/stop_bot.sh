#!/bin/bash

SERVICE_NAME="telegram_bot"

echo "🔹 Stopping the Telegram bot service..."
sudo systemctl stop ${SERVICE_NAME}
echo "✅ Service ${SERVICE_NAME} stopped successfully!"