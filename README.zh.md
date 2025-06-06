# Ollama 发行包装包工具

本项目包含了创建一个可分发的、离线的 Ollama 安装包所需的所有文件。

## 如何构建软件包

项目根目录提供了一个辅助脚本 `package.sh`，用于自动创建分发压缩包。

要构建软件包，只需从项目根目录运行此脚本：
```bash
bash package.sh
```

该脚本将执行以下操作：
1.  下载最新 ARM64 版本的 Ollama 二进制文件 (`ollama-linux-arm64.tgz`)。
2.  将下载的二进制文件放入 `ollama_dist` 目录中。
3.  在根目录中创建一个新的 tar 压缩包 (例如, `ollama_dist_arm64_YYYYMMDD.tar.gz`)。

最终生成的压缩包就是完整的、自包含的、可以分发给最终用户的软件包。 