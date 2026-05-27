#!/usr/bin/env bash
# Build and run Linux verification in Docker (Ubuntu-based image).
set -euo pipefail
cd "$(dirname "$0")/.."
IMAGE="${IMAGE:-lcms-calculator-verify}"

echo "==> Building ${IMAGE}"
docker build -t "${IMAGE}" .

echo "==> Running smoke tests"
docker run --rm "${IMAGE}"

echo "==> Optional: run Streamlit (Ctrl+C to stop)"
echo "    docker run --rm -p 8501:8501 ${IMAGE} streamlit run pfas_lcmsms_calculator_app.py --server.headless=true --server.address=0.0.0.0 --server.port=8501 --browser.gatherUsageStats=false"
