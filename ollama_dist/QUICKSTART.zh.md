# 快速入门：使用 Ollama 运行大语言模型

本指南将引导您在安装后使用 Ollama 的基本命令。

## 1. 拉取模型

在运行模型之前，您需要从 Ollama 模型库中拉取它。让我们来拉取 `qwen2:0.5b`，这是由阿里巴巴通义千问团队开发的一个轻量级、快速的模型，非常适合算力有限的边缘设备。

打开您的终端并运行：
```bash
ollama pull qwen2:0.5b
```
这会将模型下载到您的机器上。首次下载可能需要一些时间，具体取决于您的网络速度。

## 2. 运行模型 (交互式聊天)

模型拉取后，您可以直接在终端中运行它以进行聊天会话。

```bash
ollama run qwen2:0.5b
```

现在您可以开始提问了。要退出聊天，请输入 `/bye`。

## 3. 列出您的本地模型

要查看您在本地下载的所有模型，请使用 `list` 命令：

```bash
ollama list
```
这将显示一个包含所有可用模型、它们的大小以及最后修改时间的表格。

## 4. 移除模型

如果您不再需要某个模型并希望释放磁盘空间，可以将其移除。

```bash
ollama rm qwen2:0.5b
```

## 5. 使用 REST API (高级)

Ollama 还提供了一个用于程序化交互的 REST API。服务运行后，您可以使用例如 `curl` 与之交互。

以下是如何向 `qwen2:0.5b` 模型发送请求的示例：

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2:0.5b",
  "prompt": "天空为什么是蓝色的？",
  "stream": false
}'
```
这使您可以将 Ollama 集成到自己的应用程序中。有关更多详细信息，请参阅 [Ollama 官方 API 文档](https://github.com/ollama/ollama/blob/main/docs/api.md)。 