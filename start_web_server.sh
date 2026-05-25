#!/bin/bash
# ============================================================================
# PostgreSQL Memory System v2.3.0 - Web Server Control Script
# Usage: ./start_web_server.sh {start|stop|restart|status|log}
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_FILE="$SCRIPT_DIR/scripts/visualization/server.py"
CONFIG_FILE="$SCRIPT_DIR/config.json"
PID_FILE="/tmp/pg_memory_viz.pid"
LOG_FILE="$SCRIPT_DIR/viz_server.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

_detect_python() {
    local candidates=(
        "/home/linuxbrew/.linuxbrew/bin/python3.14"
        "/home/linuxbrew/.linuxbrew/bin/python3.13"
        "/home/linuxbrew/.linuxbrew/bin/python3.12"
        "/home/linuxbrew/.linuxbrew/bin/python3"
    )
    for p in "${candidates[@]}"; do
        if [ -x "$p" ]; then echo "$p"; return 0; fi
    done
    if command -v python3 &>/dev/null; then echo "python3"; return 0; fi
    return 1
}

_config_val() {
    local section="$1" key="$2" default="$3"
    if [ -f "$CONFIG_FILE" ] && command -v python3.14 &>/dev/null; then
        local val=$(python3.14 -c "import json;c=json.load(open('$CONFIG_FILE'));v=c.get('$section',{}).get('$key','$default');print(v)" 2>/dev/null)
        [ -n "$val" ] && { echo "$val"; return; }
    fi
    echo "$default"
}

load_env() {
    CFG_DB_HOST="${MEMORY_DB_HOST:-$(_config_val database host 10.10.10.131)}"
    CFG_DB_PORT="${MEMORY_DB_PORT:-$(_config_val database port 5432)}"
    CFG_DB_NAME="${MEMORY_DB_NAME:-$(_config_val database database memory_graph)}"
    CFG_DB_USER="${MEMORY_DB_USER:-$(_config_val database user pgsql)}"
    CFG_DB_PASS="${MEMORY_DB_PASSWORD:-$(_config_val database password '')}"
    CFG_HOST="${MEMORY_SERVER_HOST:-$(_config_val server host 0.0.0.0)}"
    CFG_PORT="${MEMORY_SERVER_PORT:-$(_config_val server port 8000)}"
    CFG_TIMEOUT="${MEMORY_SESSION_TIMEOUT:-$(_config_val server session_timeout 300)}"
}

get_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then echo "$pid"; return 0; fi
        rm -f "$PID_FILE"
    fi
    pgrep -f "visualization/server.py" 2>/dev/null | head -1
}

is_running() { local pid=$(get_pid); [ -n "$pid" ]; }

do_status() {
    load_env
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  PostgreSQL Memory System v2.3.0${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    if is_running; then
        echo -e "  Status:  ${GREEN}RUNNING${NC} (PID: $(get_pid))"
    else
        echo -e "  Status:  ${RED}STOPPED${NC}"
    fi
    echo ""
    echo -e "  Host:    ${CFG_HOST:-0.0.0.0}"
    echo -e "  Port:    ${CFG_PORT:-8000}"
    echo -e "  DB:      ${CFG_DB_HOST}:${CFG_DB_PORT}/${CFG_DB_NAME}"
    echo -e "  Timeout: ${CFG_TIMEOUT:-300}s"
    echo -e "  Log:     $LOG_FILE"
    echo ""
}

do_start() {
    load_env
    if is_running; then
        echo -e "${YELLOW}Server already running (PID: $(get_pid))${NC}"
        exit 0
    fi

    PYTHON=$(_detect_python)
    if [ -z "$PYTHON" ]; then
        echo -e "${RED}Error: No suitable Python 3 found${NC}"
        exit 1
    fi

    if ! $PYTHON -c "import psycopg2" 2>/dev/null; then
        echo -e "${YELLOW}psycopg2 not installed for $PYTHON, installing...${NC}"
        $PYTHON -m pip install psycopg2-binary -q 2>/dev/null || { echo -e "${RED}Failed${NC}"; exit 1; }
    fi

    if [ ! -f "$SERVER_FILE" ]; then
        echo -e "${RED}Error: Server file not found: $SERVER_FILE${NC}"
        exit 1
    fi

    if ss -tlnp 2>/dev/null | grep -q ":${CFG_PORT} "; then
        echo -e "${YELLOW}Port $CFG_PORT in use, freeing...${NC}"
        pkill -f "visualization/server.py" 2>/dev/null || true
        sleep 2
    fi

    export MEMORY_DB_HOST="$CFG_DB_HOST"
    export MEMORY_DB_PORT="$CFG_DB_PORT"
    export MEMORY_DB_NAME="$CFG_DB_NAME"
    export MEMORY_DB_USER="$CFG_DB_USER"
    export MEMORY_DB_PASSWORD="$CFG_DB_PASS"
    export MEMORY_SERVER_HOST="$CFG_HOST"
    export MEMORY_SERVER_PORT="$CFG_PORT"
    export MEMORY_SESSION_TIMEOUT="$CFG_TIMEOUT"

    echo -e "${BLUE}Starting PostgreSQL Memory Web Server${NC}"
    echo -e "  Python: $PYTHON  Host: ${GREEN}$CFG_HOST${NC}  Port: ${GREEN}$CFG_PORT${NC}  DB: $CFG_DB_HOST:$CFG_DB_PORT/$CFG_DB_NAME"

    nohup $PYTHON -u "$SERVER_FILE" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    for i in $(seq 1 30); do
        sleep 1
        if ! kill -0 "$pid" 2>/dev/null; then
            echo -e "${RED}Server exited unexpectedly${NC}"
            tail -20 "$LOG_FILE" 2>/dev/null
            rm -f "$PID_FILE"; exit 1
        fi
        if ss -tlnp 2>/dev/null | grep -qE ":${CFG_PORT}\b"; then
            local ip=$(hostname -I 2>/dev/null | awk '{print $1}')
            echo -e "${GREEN}Server started! (PID: $pid)${NC}"
            echo -e "  URL: ${GREEN}http://${ip:-localhost}:$CFG_PORT${NC}"
            echo -e "  Login: ${YELLOW}admin / admin123${NC}"
            return 0
        fi
    done
    echo -e "${YELLOW}Port not listening after 30s. Check: tail -f $LOG_FILE${NC}"
    exit 1
}

do_stop() {
    if ! is_running; then echo -e "${YELLOW}Server not running${NC}"; rm -f "$PID_FILE"; return 0; fi
    local pid=$(get_pid)
    echo -e "${YELLOW}Stopping (PID: $pid)...${NC}"
    kill "$pid" 2>/dev/null || true
    for i in $(seq 1 10); do
        sleep 1
        if ! kill -0 "$pid" 2>/dev/null; then echo -e "${GREEN}Stopped${NC}"; rm -f "$PID_FILE"; return 0; fi
    done
    kill -9 "$pid" 2>/dev/null || true; sleep 1; rm -f "$PID_FILE"
    echo -e "${GREEN}Killed${NC}"
}

do_restart() { do_stop; sleep 1; do_start; }

do_log() {
    if [ -f "$LOG_FILE" ]; then tail -50 "$LOG_FILE"; else echo -e "${YELLOW}No log file${NC}"; fi
}

PYTHON=$(_detect_python || echo "")
load_env

case "${1:-}" in
    start)   do_start ;;
    stop)    do_stop ;;
    restart) do_restart ;;
    status)  do_status ;;
    log)     do_log ;;
    *)
        echo "PostgreSQL Memory System v2.3.0 - Web Server Control"
        echo ""
        echo "Usage: ${0##*/} {start|stop|restart|status|log}"
        echo ""
        echo "Configuration: Edit config.json or set environment variables:"
        echo "  MEMORY_DB_HOST, MEMORY_DB_PORT, MEMORY_DB_NAME, MEMORY_DB_USER, MEMORY_DB_PASSWORD"
        echo "  MEMORY_SERVER_HOST, MEMORY_SERVER_PORT, MEMORY_SESSION_TIMEOUT"
        exit 1
        ;;
esac
