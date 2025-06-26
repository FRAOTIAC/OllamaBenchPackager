#!/bin/bash
#
# run_benchmark.sh: A script to install llm-benchmark using uv and run benchmarks
#                   with qwen2:0.5b and qwen3:0.6b models.
#

set -e
set -u

# Configuration
BENCHMARK_MODELS=(
    "qwen2.5:0.5b"
    "deepseek-r1:1.5b"
    "deepseek-r1:7b"
)
CUSTOM_BENCHMARK_FILE="custom_benchmark_models.yml"
VENV_DIR=".venv"
LLM_BENCHMARK_VERSION="0.4.6"

# Allow custom Python path through environment variable
PYTHON_PATH="${PYTHON_PATH:-python3.9}"

# --- Helper functions ---

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

check_command() {
    command -v "$1" &>/dev/null
}

check_python_dev() {
    if [ -f "/usr/include/python3.9/Python.h" ] || [ -f "/usr/local/include/python3.9/Python.h" ]; then
        return 0
    fi
    return 1
}

check_gcc() {
    check_command gcc
}

install_uv() {
    log_info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if ! check_command uv; then
        log_error "Failed to install uv. Please install it manually."
        exit 1
    fi
    log_info "uv installed successfully."
}

install_system_deps() {
    log_info "Installing system dependencies..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y gcc python3.9-dev
    elif command -v yum &>/dev/null; then
        sudo yum install -y gcc python3.9-devel
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y gcc python3.9-devel
    else
        log_error "Could not find a supported package manager (apt-get, yum, or dnf)."
        log_error "Please install gcc and python3.9-dev manually."
        exit 1
    fi
    log_info "System dependencies installed successfully."
}

setup_venv() {
    log_info "Setting up Python virtual environment..."

    # Check Python version
    if ! check_command "${PYTHON_PATH}"; then
        log_error "Python 3.9 is not found at '${PYTHON_PATH}'. Please install Python 3.9 or specify the correct path using PYTHON_PATH environment variable."
        log_info "Example: PYTHON_PATH=/usr/local/bin/python3.9 ./run_benchmark.sh"
        exit 1
    fi

    # Create and activate virtual environment
    uv venv "${VENV_DIR}" --python="${PYTHON_PATH}"
    source "${VENV_DIR}/bin/activate"
    log_info "Virtual environment created and activated using ${PYTHON_PATH}"
}

check_environment() {
    log_info "Checking environment requirements..."

    # Check Python
    if ! check_command "${PYTHON_PATH}"; then
        log_error "Python 3.9 is not found at '${PYTHON_PATH}'"
        return 1
    fi

    # Check uv
    if ! check_command uv; then
        log_info "uv is not installed"
        return 1
    fi

    # Check system dependencies
    if ! check_gcc || ! check_python_dev; then
        log_info "System dependencies (gcc or python3.9-dev) are missing"
        return 1
    fi

    # Check virtual environment
    if [ ! -d "${VENV_DIR}" ]; then
        log_info "Virtual environment not found"
        return 1
    fi

    # Check llm-benchmark
    if ! source "${VENV_DIR}/bin/activate" 2>/dev/null || ! command -v llm_benchmark &>/dev/null; then
        log_info "llm-benchmark is not installed in virtual environment"
        return 1
    fi

    log_info "All requirements are satisfied"
    return 0
}

# --- Main logic ---

main() {
    log_info "Starting benchmark setup and execution..."

    # Check if environment is ready
    if check_environment; then
        log_info "Environment is ready, proceeding with benchmark..."
    else
        log_info "Setting up environment..."

        # 1. Install uv if not present
        if ! check_command uv; then
            install_uv
        fi

        # 2. Install system dependencies if needed
        if ! check_gcc || ! check_python_dev; then
            install_system_deps
        fi

        # 3. Setup virtual environment
        setup_venv

        # 4. Create custom benchmark YAML file
        log_info "Creating custom benchmark configuration file..."
        cat >"${CUSTOM_BENCHMARK_FILE}" <<EOF
file_name: "${CUSTOM_BENCHMARK_FILE}"
version: 2.0.custom
models:
EOF

        for model in "${BENCHMARK_MODELS[@]}"; do
            echo "  - model: \"${model}\"" >>"${CUSTOM_BENCHMARK_FILE}"
        done

        # 5. Install llm-benchmark using uv
        log_info "Installing llm-benchmark version ${LLM_BENCHMARK_VERSION}..."
        uv pip install "llm-benchmark==${LLM_BENCHMARK_VERSION}"
    fi

    # 6. Run benchmark with custom models
    log_info "Running benchmark with custom models..."
    llm_benchmark run --custombenchmark="${CUSTOM_BENCHMARK_FILE}" --no-sendinfo

    log_info "Benchmark completed successfully!"
}

# Run the main function
main "$@"
