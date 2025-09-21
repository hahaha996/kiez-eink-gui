#!/bin/bash

SERVICE_NAME="eink-service.service"
SERVICE_FILE="./$SERVICE_NAME"
SYSTEMD_PATH="/etc/systemd/system"
SCRIPT_NAME="run-eink.sh"

function start_service() {
    echo "Starting $SERVICE_NAME..."
    sudo systemctl start "$SERVICE_NAME"
}

function stop_service() {
    echo "Stopping $SERVICE_NAME..."
    sudo systemctl stop "$SERVICE_NAME"
}

function create_service() {
    echo "Creating and enabling $SERVICE_NAME..."

    if [[ ! -f "$SERVICE_FILE" ]]; then
        echo "❌ Error: $SERVICE_FILE not found in current directory."
        exit 1
    fi

    # Copy service file
    sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH/"

    # Ensure the run script is executable
    chmod +x "$SCRIPT_NAME"

    # Reload systemd and enable the service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"

    echo "✅ Service created and enabled."
}

# Main dispatcher
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    create)
        create_service
        ;;
    *)
        echo "Usage: $0 {start|stop|create}"
        exit 1
        ;;
esac
