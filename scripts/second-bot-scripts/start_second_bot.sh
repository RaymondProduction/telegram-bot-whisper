#!/bin/bash

SERVICE_NAME="second_bot"

echo "🔹 Starting the Second Bot service..."
sudo systemctl start ${SERVICE_NAME}
echo "✅ Service ${SERVICE_NAME} started successfully!"