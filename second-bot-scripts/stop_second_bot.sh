#!/bin/bash

SERVICE_NAME="second_bot"

echo "🔹 Stopping the Second bot service..."
sudo systemctl stop ${SERVICE_NAME}
echo "✅ Service ${SERVICE_NAME} stopped successfully!"