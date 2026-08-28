#!/usr/bin/env bash
# Activate the Pi 5 Python virtual environment.
# This file must be sourced so the venv stays active in your current shell:
#   source activate_venv.sh
#   . activate_venv.sh

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "This script must be sourced, not run:"
    echo "  source $0"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || return 1

if [[ -f "$SCRIPT_DIR/venv/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$SCRIPT_DIR/venv/bin/activate"
elif [[ -d "$SCRIPT_DIR/venv" ]]; then
    echo "Found pi5/venv, but it has no bin/activate."
    echo "That usually means this folder was created on Windows and will not work on Raspberry Pi OS."
    echo "Remove pi5/venv, then source this script again, or run:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  python -m pip install -r requirements.txt"
    return 1
else
    echo "No virtual environment found. Creating venv..."
    if ! python3 -m venv venv; then
        echo "Failed to create the virtual environment."
        echo "On Raspberry Pi OS install: sudo apt install python3-venv python3-pip"
        return 1
    fi
    # shellcheck source=/dev/null
    source "$SCRIPT_DIR/venv/bin/activate"
    if ! python -m pip install -r requirements.txt; then
        echo "Failed to install requirements."
        return 1
    fi
fi

echo "Virtual environment activated."
echo "Python: $(command -v python)"
