# Ollama 发行版安装包

本软件包包含将 Ollama 安装并作为 systemd 服务运行所需的一切。

## 包内容

- `install.sh`: 安装脚本。
- `ollama.service.template`: systemd 服务的模板文件。
- `ollama-linux-arm64.tgz`: 用于 ARM64 系统的 Ollama 二进制文件。

## 先决条件

- 一个使用 `systemd` 的 Linux 系统。
- `sudo` 权限。
- 已安装 `curl` 和 `tar`。

## 安装步骤

1.  **解压软件包：**

    ```bash
    tar -xzf ollama_dist.tar.gz
    cd ollama_dist
    ```

2.  **运行安装脚本：**

    您需要使用 `sudo` 来运行此脚本。

    ```bash
    sudo ./install.sh
    ```

    该脚本将会：
    -   检测您的系统架构。
    -   将 `ollama` 二进制文件安装到 `/usr/bin`。
    -   创建一个 `ollama` 用户和用户组。
    -   为 Ollama 设置并启动 `systemd` 服务。
    -   默认的模型存储目录将是 `/usr/share/ollama`。

### 自定义安装

您可以通过向 `install.sh` 脚本提供命令行选项来自定义安装。

- `--install-dir <path>`: 设置 `ollama` 二进制文件的安装目录。
- `--models-dir <path>`: 设置 Ollama 模型的基础目录。实际模型将存储在 `<path>/.ollama/models`。
- `--host <ip:port>`: 设置 Ollama 服务监听的地址。

**示例：**

```bash
sudo ./install.sh --install-dir /opt/ollama/bin --models-dir /opt/ollama/models
```

这将把 `ollama` 二进制文件安装到 `/opt/ollama/bin`，并将模型存储在 `/opt/ollama/models`。

## 验证安装

您可以使用以下命令检查 Ollama 服务的状态：

```bash
sudo systemctl status ollama
```

您也可以检查 Ollama 的版本：

```bash
ollama -v
```

## 卸载

要卸载 Ollama，请使用 `--uninstall` 标志运行安装脚本：

```bash
sudo ./install.sh --uninstall
```

这将停止并禁用服务，移除 `ollama` 二进制文件，并删除 `ollama` 用户和用户组。
注意：模型目录不会被自动删除。如果您需要，可以手动删除它。 