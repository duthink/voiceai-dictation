#!/usr/bin/env bash
# Convenience launcher for micromamba/conda environments.
# Usage: ./scripts/start.sh [--key f9] [--chunk 4] ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Try micromamba, then conda, then bare python
if command -v micromamba >/dev/null 2>&1; then
    eval "$(micromamba shell hook --shell bash)"
    micromamba activate voiceai 2>/dev/null || true
elif command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.bash hook)"
    conda activate voiceai 2>/dev/null || true
fi

exec python -m voiceai "$@"
