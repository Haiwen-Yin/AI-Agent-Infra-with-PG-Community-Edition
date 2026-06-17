#!/bin/bash
# AI Agent Infra v3.6.1 - Community Edition (PG) - Web Server Start Script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

export PYTHONPATH="${SCRIPT_DIR}/scripts:${PYTHONPATH}"

CONFIG_FILE="${SCRIPT_DIR}/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[ERROR] config.json not found at ${CONFIG_FILE}"
    exit 1
fi

SERVER_PORT=$(python3 -c "import json; c=json.load(open('${CONFIG_FILE}')); print(c.get('server_port', 18080))")

echo "============================================"
echo " AI Agent Infra v3.6.1 - Community Edition (PG)"
echo " Visualization Server"
echo "============================================"
echo " Config:  ${CONFIG_FILE}"
echo " Port:    ${SERVER_PORT}"
echo "============================================"

cd "${SCRIPT_DIR}/scripts/visualization"

exec python3 server.py
