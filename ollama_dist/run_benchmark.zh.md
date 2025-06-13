# 运行 Ollama 性能测试

本指南将帮助您使用 `llm-benchmark` 工具来测试 Ollama 的性能。

## 前提条件

- 已安装 Ollama
- 已安装 Python 3.9 或更高版本
- 具有 sudo 权限（用于安装系统依赖）

## 使用方法

1. 直接运行测试脚本：
   ```bash
   ./run_benchmark.sh
   ```

   该脚本将：
   - 检查环境是否满足所有要求
   - 如果环境不满足要求，自动安装缺失的组件：
     - 检查并安装 `uv`（如果尚未安装）
     - 安装必要的系统依赖（gcc 和 python3.9-dev）
     - 创建并激活 Python 3.9+ 的虚拟环境
     - 安装 `llm-benchmark` 0.4.6 版本
   - 使用 `qwen2:0.5b` 和 `qwen3:0.6b` 模型运行性能测试

2. 如果您想使用系统中特定的 Python 3.9 安装路径，可以通过环境变量指定：
   ```bash
   PYTHON_PATH=/path/to/your/python3.9 ./run_benchmark.sh
   ```
   例如：
   ```bash
   PYTHON_PATH=/usr/local/bin/python3.9 ./run_benchmark.sh
   ```

## 环境检查

脚本会自动检查以下组件：
- Python 3.9 是否可用
- `uv` 是否已安装
- 系统依赖（gcc 和 python3.9-dev）是否已安装
- 虚拟环境是否存在
- `llm-benchmark` 是否已安装在虚拟环境中

只有在缺少必要组件时，脚本才会执行安装步骤。

## 测试结果

测试完成后，您将看到每个模型的性能指标，包括：
- 吞吐量（每秒处理的 token 数）
- 延迟（每个请求的响应时间）
- 内存使用情况

## 注意事项

- 测试过程可能需要一些时间，具体取决于您的硬件配置。
- 确保您的系统有足够的内存来运行这些模型。
- 测试结果不会发送到远程服务器（使用了 `--no-sendinfo` 选项）。
- 脚本会自动创建并使用虚拟环境（`.venv`），无需手动管理 Python 环境。
- 如果系统中安装了多个 Python 3.9 版本，可以使用 `PYTHON_PATH` 环境变量指定要使用的版本。
- 脚本会自动安装必要的系统依赖（gcc 和 python3.9-dev），需要 sudo 权限。
- 如果您的系统使用不同的包管理器（如 yum 或 dnf），脚本会自动适配。 