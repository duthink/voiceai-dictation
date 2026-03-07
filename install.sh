#!/usr/bin/env bash
set -euo pipefail

# ─── VoiceAI Dictation Installer ────────────────────────────────────────────
# Installs system dependencies and the Python package.
#
# Usage:
#   ./install.sh              # install into current Python env
#   ./install.sh --dev        # install with dev dependencies (pytest, ruff)
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}ℹ  $1${NC}"; }
ok()    { echo -e "${GREEN}✓  $1${NC}"; }
fail()  { echo -e "${RED}✗  $1${NC}"; exit 1; }

echo ""
echo "  ┌──────────────────────────────────────────┐"
echo "  │  VoiceAI Dictation — Installer            │"
echo "  └──────────────────────────────────────────┘"
echo ""

# ── 1. Check prerequisites ──────────────────────────────────────────────────

info "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || fail "Python 3 not found"
command -v pip3 >/dev/null 2>&1    || fail "pip3 not found"

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    fail "Python >= 3.10 required (found $PYTHON_VERSION)"
fi
ok "Python $PYTHON_VERSION"

# Check for NVIDIA GPU
if command -v nvidia-smi >/dev/null 2>&1; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    ok "GPU: $GPU_NAME"
else
    echo -e "${RED}⚠  nvidia-smi not found. GPU acceleration won't work.${NC}"
    echo "   Install NVIDIA drivers first: https://docs.nvidia.com/cuda/"
fi

# ── 2. System dependencies ──────────────────────────────────────────────────

info "Installing system dependencies (may need sudo)..."

PACKAGES="ffmpeg portaudio19-dev libsndfile1"

# Check for xdotool or ydotool
if ! command -v xdotool >/dev/null 2>&1 && ! command -v ydotool >/dev/null 2>&1; then
    PACKAGES="$PACKAGES xdotool"
    info "Adding xdotool (text injection)"
fi

sudo apt install -y $PACKAGES >/dev/null 2>&1 && ok "System packages installed" \
    || echo -e "${RED}⚠  apt install failed. Install manually: sudo apt install $PACKAGES${NC}"

# ── 3. Python package ───────────────────────────────────────────────────────

info "Installing voiceai-dictation..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--dev" ]]; then
    pip install -e "$SCRIPT_DIR[dev]" 2>&1 | tail -1
    ok "Installed in dev mode (with pytest + ruff)"
else
    pip install -e "$SCRIPT_DIR" 2>&1 | tail -1
    ok "Installed"
fi

# ── 4. Download model ───────────────────────────────────────────────────────

info "Pre-downloading Whisper model (distil-large-v3)..."
python3 -c "
from faster_whisper import WhisperModel
import sys
try:
    m = WhisperModel('distil-large-v3', device='cuda', compute_type='float16')
    del m
    print('\033[92m✓  Model cached\033[0m')
except Exception as e:
    print(f'\033[93m⚠  GPU load failed ({e}), trying CPU...\033[0m')
    m = WhisperModel('distil-large-v3', device='cpu', compute_type='float32')
    del m
    print('\033[92m✓  Model cached (CPU fallback)\033[0m')
"

# ── 5. Verify ───────────────────────────────────────────────────────────────

echo ""
if command -v voiceai >/dev/null 2>&1; then
    ok "Installation complete!"
    echo ""
    echo "  Quick start:"
    echo "    voiceai-selftest     # verify everything works"
    echo "    voiceai              # start dictating (F9 to toggle)"
    echo ""
    # Detect if running inside micromamba/conda and show run-without-activate tip
    if [ -n "${CONDA_PREFIX:-}" ]; then
        ENV_NAME=$(basename "$CONDA_PREFIX")
        echo "  Run without activating (micromamba/conda):"
        echo "    micromamba run -n $ENV_NAME voiceai"
        echo ""
    fi
else
    ok "Package installed. Run with: python -m voiceai"
    echo ""
fi
