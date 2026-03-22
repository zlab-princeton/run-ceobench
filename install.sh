#!/bin/bash
# NovaMind Bench — Install
#
# Checks Python version, installs dependencies, and makes scripts executable.
#
# Usage:
#   bash install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "NovaMind Bench — Install"
echo "========================"

# ── Step 1: Check Python version (need 3.13+) ──
PYTHON=""
for candidate in python3.13 python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major=$("$candidate" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
        minor=$("$candidate" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
        if [ "$major" -eq 3 ] && [ "$minor" -ge 13 ]; then
            PYTHON="$candidate"
            echo "✅ Python $version found: $(command -v "$candidate")"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.13+ is required but not found."
    echo ""
    echo "   Install Python 3.13:"
    echo "   • macOS:   brew install python@3.13"
    echo "   • Ubuntu:  sudo apt install python3.13"
    echo "   • conda:   conda create -n novamind python=3.13"
    echo "   • pyenv:   pyenv install 3.13"
    exit 1
fi

# ── Step 2: Install Python dependencies ──
echo ""
echo "Installing dependencies..."
"$PYTHON" -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo "✅ Dependencies installed"

# ── Step 3: Make scripts executable ──
chmod +x "$SCRIPT_DIR/novamind-operation"
chmod +x "$SCRIPT_DIR/novamind-server"
echo "✅ Scripts ready"

# ── Done ──
echo ""
echo "========================"
echo "✅ Installation complete!"
echo ""
echo "Quick start:"
echo "  cd $SCRIPT_DIR"
echo "  ./novamind-operation new-session --days 365 --seed 42"
echo "  ./novamind-operation next-day"
