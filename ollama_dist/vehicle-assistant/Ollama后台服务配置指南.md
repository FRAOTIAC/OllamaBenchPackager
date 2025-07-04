# Ollama 后台服务配置指南

## 1. Ollama OpenAI API 兼容性

Ollama 提供完整的 OpenAI 兼容 API，支持：
- `/v1/chat/completions` 端点
- 流式响应
- 标准 OpenAI 格式的请求和响应

### API 端点对比
```bash
# Ollama 原生 API
http://localhost:11434/api/generate

# OpenAI 兼容 API
http://localhost:11434/v1/chat/completions
```

## 2. 启动后台服务

### 2.1 基本启动
```bash
# 启动 Ollama 服务
ollama serve

# 后台运行（Linux/macOS）
nohup ollama serve > ollama.log 2>&1 &
```

### 2.2 系统服务配置（推荐）

#### Linux (systemd)
```bash
# 编辑服务配置
sudo systemctl edit ollama.service

# 添加以下内容
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
Environment="OLLAMA_MODELS=/usr/share/ollama/.ollama/models"

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl enable ollama
```

#### macOS
```bash
# 设置环境变量
launchctl setenv OLLAMA_HOST "0.0.0.0"
launchctl setenv OLLAMA_ORIGINS "*"

# 重启 Ollama 应用
```

#### Windows
```bash
# 在系统环境变量中添加：
OLLAMA_HOST=0.0.0.0
OLLAMA_ORIGINS=*

# 重启 Ollama 应用
```

## 3. 网络访问配置

### 3.1 CORS 配置
```bash
# 允许所有来源
OLLAMA_ORIGINS="*"

# 允许特定域名
OLLAMA_ORIGINS="http://localhost:3000,https://yourdomain.com"

# 验证 CORS 设置
curl -X OPTIONS http://localhost:11434 \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" -I
```

### 3.2 网络绑定
```bash
# 绑定到所有网络接口
OLLAMA_HOST="0.0.0.0"

# 绑定到特定 IP
OLLAMA_HOST="192.168.1.100"

# 验证绑定
netstat -an | grep 11434
```

## 4. 前端集成示例

### 4.1 JavaScript (原生)
```javascript
// 配置 OpenAI 兼容客户端
const client = {
  baseURL: 'http://localhost:11434/v1',
  apiKey: 'ollama' // 必需但不使用
};

// 发送请求
async function chatWithOllama(message) {
  const response = await fetch(`${client.baseURL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${client.apiKey}`
    },
    body: JSON.stringify({
      model: 'vehicle-assistant',
      messages: [
        { role: 'user', content: message }
      ],
      stream: false
    })
  });
  
  const data = await response.json();
  return data.choices[0].message.content;
}
```

### 4.2 React 集成
```jsx
import React, { useState } from 'react';

function ChatComponent() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    setLoading(true);
    try {
      const result = await fetch('http://localhost:11434/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'vehicle-assistant',
          messages: [{ role: 'user', content: message }],
          stream: false
        })
      });
      
      const data = await result.json();
      setResponse(data.choices[0].message.content);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="输入消息..."
      />
      <button onClick={sendMessage} disabled={loading}>
        {loading ? '发送中...' : '发送'}
      </button>
      <div>{response}</div>
    </div>
  );
}
```

### 4.3 Vue.js 集成
```vue
<template>
  <div>
    <input v-model="message" placeholder="输入消息..." />
    <button @click="sendMessage" :disabled="loading">
      {{ loading ? '发送中...' : '发送' }}
    </button>
    <div>{{ response }}</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      response: '',
      loading: false
    }
  },
  methods: {
    async sendMessage() {
      this.loading = true;
      try {
        const result = await fetch('http://localhost:11434/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'vehicle-assistant',
            messages: [{ role: 'user', content: this.message }],
            stream: false
          })
        });
        
        const data = await result.json();
        this.response = data.choices[0].message.content;
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

## 5. 流式响应处理

### 5.1 JavaScript 流式处理
```javascript
async function streamChat(message) {
  const response = await fetch('http://localhost:11434/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'vehicle-assistant',
      messages: [{ role: 'user', content: message }],
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        
        try {
          const parsed = JSON.parse(data);
          const content = parsed.choices[0].delta.content;
          if (content) {
            console.log(content); // 处理流式内容
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    }
  }
}
```

## 6. 使用 OpenAI 官方库

### 6.1 Python
```python
from openai import OpenAI

# 配置客户端
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 必需但不使用
)

# 发送请求
response = client.chat.completions.create(
    model="vehicle-assistant",
    messages=[
        {"role": "user", "content": "帮我打开空调"}
    ]
)

print(response.choices[0].message.content)
```

### 6.2 Node.js
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'http://localhost:11434/v1',
  apiKey: 'ollama'
});

const completion = await openai.chat.completions.create({
  model: 'vehicle-assistant',
  messages: [
    { role: 'user', content: '帮我打开空调' }
  ],
});

console.log(completion.choices[0].message.content);
```

## 7. 服务健康检查

### 7.1 健康检查脚本
```bash
#!/bin/bash
# health_check.sh

# 检查服务状态
check_service() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags)
    if [ "$response" = "200" ]; then
        echo "✅ Ollama 服务正常"
        return 0
    else
        echo "❌ Ollama 服务异常 (HTTP $response)"
        return 1
    fi
}

# 检查模型状态
check_model() {
    local model_name="$1"
    response=$(curl -s http://localhost:11434/api/generate -d "{\"model\":\"$model_name\",\"prompt\":\"test\",\"stream\":false}")
    if echo "$response" | grep -q "response"; then
        echo "✅ 模型 $model_name 正常"
        return 0
    else
        echo "❌ 模型 $model_name 异常"
        return 1
    fi
}

# 执行检查
check_service
check_model "vehicle-assistant"
```

### 7.2 监控脚本
```python
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_ollama():
    while True:
        try:
            # 检查服务状态
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama 服务正常")
            else:
                logger.error(f"❌ Ollama 服务异常: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"❌ 连接失败: {e}")
            
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    monitor_ollama()
```

## 8. 性能优化配置

### 8.1 环境变量配置
```bash
# 模型存储路径
export OLLAMA_MODELS="/path/to/models"

# 最大并发连接数
export OLLAMA_MAX_LOADED_MODELS=3

# 内存使用限制
export OLLAMA_MAX_VRAM=8GB

# 日志级别
export OLLAMA_LOG_LEVEL=INFO
```

### 8.2 反向代理配置 (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 支持流式响应
        proxy_buffering off;
        proxy_cache off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## 9. 故障排除

### 9.1 常见问题
```bash
# 端口被占用
sudo lsof -i :11434
sudo kill -9 <PID>

# 权限问题
sudo chown -R $USER:$USER ~/.ollama

# 模型加载失败
ollama pull <model-name>
ollama list
```

### 9.2 日志查看
```bash
# Linux 系统日志
sudo journalctl -u ollama -f

# macOS 日志
tail -f ~/Library/Logs/Ollama/ollama.log

# Windows 日志
# 查看 Windows 事件查看器
```

## 10. 安全建议

### 10.1 网络安全
```bash
# 使用防火墙限制访问
sudo ufw allow from 192.168.1.0/24 to any port 11434

# 使用 SSL/TLS
# 配置 HTTPS 反向代理
```

### 10.2 访问控制
```bash
# 限制 CORS 来源
OLLAMA_ORIGINS="https://yourdomain.com"

# 使用 API 网关进行认证
# 如 Kong, Traefik 等
```

这样配置后，您的前端应用就可以像使用 OpenAI API 一样使用 Ollama 了！ 