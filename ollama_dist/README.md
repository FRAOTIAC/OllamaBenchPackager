# Ollama Distribution Package

This package contains everything needed to install and run Ollama as a systemd service.

## Contents

- `install.sh`: The installation script.
- `ollama.service.template`: A template for the systemd service file.
- `ollama-linux-arm64.tgz`: The Ollama binary for ARM64 systems.

## Prerequisites

- A Linux system with `systemd`.
- `sudo` privileges.
- `curl` and `tar` installed.

## Installation

1.  **Extract the package:**

    ```bash
    tar -xzf ollama_dist.tar.gz
    cd ollama_dist
    ```

2.  **(Optional) Download the Ollama binary:**

    If the `ollama-linux-*.tgz` file for your architecture is not included in this package, the installation script will download it from the official Ollama website. If you see the binary for your architecture in the `Contents` list above, you can perform a fully offline installation.

    For AMD64:
    ```bash
    curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz
    ```

    For ARM64:
    ```bash
    curl -L https://ollama.com/download/ollama-linux-arm64.tgz -o ollama-linux-arm64.tgz
    ```

3.  **Run the installation script:**

    You need to run the script with `sudo`.

    ```bash
    sudo ./install.sh
    ```

    The script will:
    - Detect your system's architecture.
    - Install the `ollama` binary to `/usr/bin`.
    - Create an `ollama` user and group.
    - Set up and start a `systemd` service for Ollama.
    - The default model directory will be `/usr/share/ollama`.

### Customizing the installation

You can customize the installation by providing command-line options to the `install.sh` script.

- `--install-dir <path>`: Sets the installation directory for the `ollama` binary.
- `--models-dir <path>`: Sets the base directory for Ollama models. The actual models will be stored in `<path>/.ollama/models`.
- `--host <ip:port>`: Sets the listen address for the Ollama service.

**Example:**

```bash
sudo ./install.sh --install-dir /opt/ollama/bin --models-dir /opt/ollama/models
```

This will install the `ollama` binary to `/opt/ollama/bin` and store models in `/opt/ollama/models`.

## Verifying the installation

You can check the status of the Ollama service with:

```bash
sudo systemctl status ollama
```

You can also check the version of Ollama:

```bash
ollama -v
```

## Uninstalling

To uninstall Ollama, run the installation script with the `--uninstall` flag:

```bash
sudo ./install.sh --uninstall
```

This will stop and disable the service, remove the `ollama` binary, and delete the `ollama` user and group.
Note: The models directory will not be removed automatically. You can remove it manually if you wish. 