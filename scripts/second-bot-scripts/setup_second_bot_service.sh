SERVICE_NAME="second_bot"
WORKING_DIR=$(pwd)
PYTHON_EXEC="$WORKING_DIR/venv/bin/python"
BOT_SCRIPT="$WORKING_DIR/second_bot.py"
LOG_FILE="/var/log/${SERVICE_NAME}.log"

echo "🔹 Creating systemd service for Second Bot..."

# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Second Bot Service
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=${WORKING_DIR}
ExecStart=/bin/bash -c 'source venv/bin/activate && ${PYTHON_EXEC} ${BOT_SCRIPT}'
StandardOutput=append:${LOG_FILE}
StandardError=append:${LOG_FILE}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "🔹 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "🔹 Enabling and starting the Second Bot service..."
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "✅ Service ${SERVICE_NAME} created and started successfully!"
echo "Logs can be found at ${LOG_FILE}"