#!/bin/bash
#
# package.sh: A script to download the latest Ollama arm64 binary
#             and package the distribution directory.
#

set -e
set -u

# Configuration
DIST_DIR="ollama_dist"
ARCH="arm64"
OLLAMA_TGZ="ollama-linux-${ARCH}.tgz"
OLLAMA_URL="https://ollama.com/download/${OLLAMA_TGZ}"
DOWNLOAD_PATH="${DIST_DIR}/${OLLAMA_TGZ}"

echo "[INFO] Starting packaging process..."

# 1. Download the latest Ollama arm64 binary
echo "[INFO] Downloading latest Ollama for ${ARCH} from ${OLLAMA_URL}..."
curl -L --progress-bar "${OLLAMA_URL}" -o "${DOWNLOAD_PATH}"

if [ ! -f "${DOWNLOAD_PATH}" ]; then
    echo "[ERROR] Failed to download Ollama package." >&2
    exit 1
fi

echo "[INFO] Download complete: ${DOWNLOAD_PATH}"

# 2. Package the entire distribution
TIMESTAMP=$(date +%Y%m%d)
OUTPUT_TARBALL="ollama_dist_${ARCH}_${TIMESTAMP}.tar.gz"

echo "[INFO] Creating distribution tarball: ${OUTPUT_TARBALL}..."
tar -czf "${OUTPUT_TARBALL}" "${DIST_DIR}"

echo ""
echo "[SUCCESS] Packaging complete!"
echo "Distribution package created at: $(pwd)/${OUTPUT_TARBALL}"
