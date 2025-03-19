#!/bin/bash

SERVICE_NAME="telegram_bot"

echo "🔹 Showing logs for the Telegram bot service..."
sudo journalctl -u ${SERVICE_NAME} -f