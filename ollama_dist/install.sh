#!/bin/bash
#
# install.sh: A script to install Ollama from a distributable package.
#

set -e
set -u

# Default values
INSTALL_DIR="/usr/bin"
MODELS_DIR="/usr/share/ollama"
SERVICE_USER="ollama"
OLLAMA_HOST="0.0.0.0:11434"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

# --- Helper functions ---

# Print usage information
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --install-dir <path>   Set the installation directory for the ollama binary."
    echo "                         (default: ${INSTALL_DIR})"
    echo "  --models-dir <path>    Set the directory to store Ollama models."
    echo "                         (default: ${MODELS_DIR})"
    echo "  --host <host:port>     Set the host and port for Ollama to listen on."
    echo "                         (default: ${OLLAMA_HOST})"
    echo "  --uninstall              Uninstall Ollama."
    echo "  -h, --help             Display this help message."
    echo ""
    echo "Example:"
    echo "  sudo ./install.sh --install-dir /usr/local/bin"
}

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

# --- Main logic ---

uninstall() {
    log_info "Uninstalling Ollama..."
    if systemctl is-active --quiet ollama; then
        log_info "Stopping ollama service..."
        systemctl stop ollama
    fi
    if systemctl is-enabled --quiet ollama; then
        log_info "Disabling ollama service..."
        systemctl disable ollama
    fi

    log_info "Removing ollama service file..."
    rm -f /etc/systemd/system/ollama.service
    systemctl daemon-reload

    OLLAMA_BINARY_PATH=$(which ollama || true)
    if [ -n "${OLLAMA_BINARY_PATH}" ]; then
        log_info "Removing ollama binary from ${OLLAMA_BINARY_PATH}..."
        rm -f "${OLLAMA_BINARY_PATH}"
    fi

    if id -u "${SERVICE_USER}" &>/dev/null; then
        log_info "Removing user '${SERVICE_USER}'..."
        userdel -r "${SERVICE_USER}"
    fi
    if getent group "${SERVICE_USER}" &>/dev/null; then
        log_info "Removing group '${SERVICE_USER}'..."
        groupdel "${SERVICE_USER}"
    fi

    log_info "Ollama uninstalled successfully."
    exit 0
}

main() {
    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --models-dir)
            MODELS_DIR="$2"
            shift 2
            ;;
        --host)
            OLLAMA_HOST="$2"
            shift 2
            ;;
        --uninstall)
            uninstall
            ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
        esac
    done

    log_info "Starting Ollama installation with the following settings:"
    log_info "  - Installation directory: ${INSTALL_DIR}"
    log_info "  - Models directory:       ${MODELS_DIR}"
    log_info "  - Service Listen Address: ${OLLAMA_HOST}"
    echo ""

    # 1. Check for root privileges
    if [ "$(id -u)" -ne 0 ]; then
        log_error "This script must be run as root. Please use sudo."
        exit 1
    fi

    # 2. Check dependencies
    for cmd in curl tar; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "'$cmd' is not installed. Please install it first."
            exit 1
        fi
    done

    if ! command -v systemctl &>/dev/null; then
        log_error "'systemctl' not found. This script requires systemd."
        exit 1
    fi

    # 3. Detect architecture
    ARCH=$(uname -m)
    case "$ARCH" in
    x86_64)
        OLLAMA_ARCH="amd64"
        ;;
    aarch64 | arm64)
        OLLAMA_ARCH="arm64"
        ;;
    *)
        log_error "Unsupported architecture '$ARCH'."
        exit 1
        ;;
    esac
    log_info "Detected architecture: ${OLLAMA_ARCH}"

    # 4. Download and install ollama binary
    OLLAMA_TGZ="ollama-linux-${OLLAMA_ARCH}.tgz"
    OLLAMA_URL="https://ollama.com/download/${OLLAMA_TGZ}"

    if [ -f "${SCRIPT_DIR}/${OLLAMA_TGZ}" ]; then
        log_info "Found local Ollama package: ${SCRIPT_DIR}/${OLLAMA_TGZ}"
        TMP_DIR=$(mktemp -d)
        tar -C "${TMP_DIR}" -xzf "${SCRIPT_DIR}/${OLLAMA_TGZ}"
    else
        log_info "Downloading Ollama from ${OLLAMA_URL}..."
        TMP_DIR=$(mktemp -d)
        curl -L "${OLLAMA_URL}" -o "${TMP_DIR}/${OLLAMA_TGZ}"
        tar -C "${TMP_DIR}" -xzf "${TMP_DIR}/${OLLAMA_TGZ}"
    fi

    log_info "Installing ollama binary to ${INSTALL_DIR}"
    mkdir -p "${INSTALL_DIR}"

    FOUND_OLLAMA_BINARY=$(find "${TMP_DIR}" -name ollama -type f | head -n 1)

    if [ -z "${FOUND_OLLAMA_BINARY}" ]; then
        log_error "Could not find 'ollama' binary in the archive."
        log_info "Contents of the temporary directory:"
        ls -R "${TMP_DIR}"
        rm -rf "${TMP_DIR}"
        exit 1
    fi

    mv "${FOUND_OLLAMA_BINARY}" "${INSTALL_DIR}/ollama"
    rm -rf "${TMP_DIR}"

    # 5. Create user and group
    if ! getent group "${SERVICE_USER}" >/dev/null; then
        log_info "Creating group '${SERVICE_USER}'..."
        groupadd -r "${SERVICE_USER}"
    else
        log_info "Group '${SERVICE_USER}' already exists."
    fi

    if ! id -u "${SERVICE_USER}" &>/dev/null; then
        log_info "Creating user '${SERVICE_USER}'..."
        useradd -r -s /bin/false -g "${SERVICE_USER}" -d "${MODELS_DIR}" -m "${SERVICE_USER}"
    else
        log_info "User '${SERVICE_USER}' already exists."
    fi

    # Add the user who invoked sudo to the ollama group
    if [ -n "${SUDO_USER}" ]; then
        log_info "Adding user '${SUDO_USER}' to the '${SERVICE_USER}' group..."
        usermod -a -G "${SERVICE_USER}" "${SUDO_USER}"
    else
        log_info "Not running under sudo, cannot determine user to add to group."
    fi

    # 6. Create and configure systemd service
    log_info "Creating systemd service file..."
    TEMPLATE_PATH="${SCRIPT_DIR}/ollama.service.template"
    if [ ! -f "${TEMPLATE_PATH}" ]; then
        log_error "Service template not found at ${TEMPLATE_PATH}"
        exit 1
    fi

    SERVICE_FILE_CONTENT=$(cat "${TEMPLATE_PATH}")
    SERVICE_FILE_CONTENT=${SERVICE_FILE_CONTENT//"{{OLLAMA_BINARY_PATH}}"/"${INSTALL_DIR}/ollama"}
    SERVICE_FILE_CONTENT=${SERVICE_FILE_CONTENT//"{{OLLAMA_USER}}"/"${SERVICE_USER}"}
    SERVICE_FILE_CONTENT=${SERVICE_FILE_CONTENT//"{{OLLAMA_GROUP}}"/"${SERVICE_USER}"}
    SERVICE_FILE_CONTENT=${SERVICE_FILE_CONTENT//"{{PATH}}"/"${PATH}"}
    SERVICE_FILE_CONTENT=${SERVICE_FILE_CONTENT//"{{OLLAMA_MODELS_DIR}}"/"${MODELS_DIR}/.ollama/models"}
    SERVICE_FILE_CONTENT=${SERVICE_FILE_CONTENT//"{{OLLAMA_HOST}}"/"${OLLAMA_HOST}"}

    echo "${SERVICE_FILE_CONTENT}" >/etc/systemd/system/ollama.service

    # 7. Reload systemd, enable and start service
    log_info "Reloading systemd daemon..."
    systemctl daemon-reload
    log_info "Enabling ollama service to start on boot..."
    systemctl enable ollama.service
    log_info "Starting ollama service..."
    systemctl start ollama.service

    log_info "Ollama installation completed successfully!"
    log_info "You can check the service status with: systemctl status ollama"
}

# Run the main function
main "$@"
