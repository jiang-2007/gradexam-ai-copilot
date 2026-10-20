# 部署指南

## 本地开发

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd gradexam-ai-copilot

# 2. 创建虚拟环境（可选）
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env

# 5. 启动
python main.py              # API 服务 :8000
streamlit run streamlit_app.py  # Web UI :8501
```

## 本地大模型推荐（Ollama）

```bash
# 安装 Ollama 后拉取模型
ollama pull deepseek-r1:7b      # 问答/批改，效果好
ollama pull qwen2.5:7b          # 通义千问，中文友好
```

## 云端部署（Docker 可选）

本项目未提供 Dockerfile，但可通过以下方式部署：

1. **Render / Railway / Fly.io**：直接部署 Python 服务
2. **阿里云/腾讯云 ECS**：
   ```bash
   pip install -r requirements.txt
   nohup python main.py &
   ```
3. **Streamlit Cloud**：直接关联 GitHub 仓库，自动部署 Web UI

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LLM_BASE_URL | 大模型 API 地址 | http://localhost:11434/v1 |
| LLM_API_KEY | API Key | ollama |
| LLM_MODEL | 模型名称 | deepseek-r1:7b |
| EMBEDDING_MODEL | Embedding 模型 | BAAI/bge-small-zh-v1.5 |
| CHUNK_SIZE | 文档切分大小 | 500 |
| VECTOR_STORE_PATH | 向量库存储路径 | ./data/chroma_db |
| BOCHA_API_KEY | 博查搜索 Key（全网情报功能，免费注册） | 空 |
| PORT | API 端口 | 8000 |

## 全网情报功能启用（学费/报录比/深度报告）

1. 访问 [博查开放平台](https://open.bochaai.com) 注册账号（新用户有免费搜索额度）
2. 在控制台创建应用，获取 API Key
3. 填入 `.env`：
   ```env
   BOCHA_API_KEY=sk-xxxxxxxx
   ```
4. 重启服务。之后 `/tuition`、`/ratio`、`/compare`、`/report` 指令和 Web 端「全网情报」页即实时检索全网数据。
5. 未配置 Key 时，这些功能会返回配置指引，不会伪造数据。
