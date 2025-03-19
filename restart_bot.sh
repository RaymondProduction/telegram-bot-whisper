#!/bin/bash

SERVICE_NAME="telegram_bot"

echo "🔹 Restarting the Telegram bot service..."
sudo systemctl restart ${SERVICE_NAME}
echo "✅ Service ${SERVICE_NAME} restarted successfully!"