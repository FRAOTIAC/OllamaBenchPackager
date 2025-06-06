# Quickstart: Running LLMs with Ollama

This guide will walk you through the basic commands to get started with Ollama after installation.

## 1. Pulling a Model

Before you can run a model, you need to pull it from the Ollama model library. Let's pull `qwen2:0.5b`, a lightweight and fast model from Alibaba Cloud, well-suited for devices with limited computational power.

Open your terminal and run:
```bash
ollama pull qwen2:0.5b
```
This will download the model to your machine. The first download may take some time depending on your network speed.

## 2. Running a Model (Interactive Chat)

Once the model is pulled, you can run it directly in your terminal for a chat session.

```bash
ollama run qwen2:0.5b
```

You can now start asking questions. To exit the chat, type `/bye`.

## 3. Listing Your Local Models

To see all the models you have downloaded locally, use the `list` command:

```bash
ollama list
```
This will show you a table of all available models, their sizes, and when they were last modified.

## 4. Removing a Model

If you no longer need a model and want to free up disk space, you can remove it.

```bash
ollama rm qwen2:0.5b
```

## 5. Using the REST API (Advanced)

Ollama also provides a REST API for programmatic interaction. Once the service is running, you can interact with it, for example, using `curl`.

Here's an example of how to send a request to the `qwen2:0.5b` model:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2:0.5b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```
This allows you to integrate Ollama into your own applications. For more details, refer to the [official Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md). 