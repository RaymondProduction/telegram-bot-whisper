#!/bin/bash

SERVICE_NAME="second_bot"

echo "🔹 Restarting the Second bot service..."
sudo systemctl restart ${SERVICE_NAME}
echo "✅ Service ${SERVICE_NAME} restarted successfully!"