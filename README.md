# 📚 考研AIGC助手 (GradExam AI Copilot)

一个面向考研党的全栈 AI 辅助工具集，基于 LangChain + ChromaDB + 飞书机器人 + 全网情报检索，集成**八大核心功能**。

## ✨ 功能模块

| 模块 | 说明 |
|------|------|
| 🔍 **RAG 知识库问答** | 上传考研 PDF/笔记，本地向量库检索，精准回答你的知识点问题 |
| ✍️ **作文智能批改** | 英语作文按考研标准打分 + 语法标注 + 润色范文；政治论述题踩分点对照 |
| 📅 **复习规划 & 择校** | 根据目标院校/基础/剩余时间生成月度计划；按估分推荐冲/稳/保院校 |
| 🃏 **闪卡自动生成** | 粘贴笔记，AI 自动拆解成 Q&A 背诵卡片 |
| 💰 **学费情报检索** | 全网检索指定院校专业的学硕/专硕/非全学费与学制，已查证 vs 未提及分开标注 |
| 📊 **报录比/分数线检索** | 复试线、国家线对比、招生计划、录取人数、报录比、推免占比，区分官方与第三方来源 |
| ⚖️ **专硕 vs 学硕分析** | 8+ 维度对比表 + 最新缩招/扩招趋势 + 按人群选择建议（内置研招网权威口径） |
| 📑 **一键深度分析报告** | 输入院校+专业，全网检索并自动生成 Markdown 完整报告（学费/报录/竞争评估/风险/行动建议/来源） |

## 🛠 技术栈

- **后端**：FastAPI + Uvicorn
- **RAG**：LangChain + ChromaDB + BGE 中文 Embedding
- **大模型**：OpenAI 兼容接口（Ollama / DeepSeek / 千帆 / OpenAI 均可）
- **全网检索**：博查搜索 API（免费额度）
- **Web UI**：Streamlit
- **飞书**：lark-oapi SDK，群机器人直接 @ 使用

## 🚀 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env  # 编辑配置（含 BOCHA_API_KEY 可选）
python main.py              # API :8000
streamlit run streamlit_app.py  # Web UI :8501
```

**全网检索功能**：到 [博查开放平台](https://open.bochaai.com) 免费注册获取 API Key，填入 `.env` 的 `BOCHA_API_KEY`，学费/报录比/深度报告即可实时检索全网。不配置也不影响其他功能。

## 🤖 飞书指令

- 直接输入问题 → RAG 问答
- `/essay 题目 | 作文` → 英语作文批改
- `/politics 题目 | 答案` → 政治题批改
- `/plan 院校 | 专业 | 基础 | 月数 | 每日小时` → 复习计划
- `/school 本科 | 专业 | 估分 | 地域 | 学硕/专硕` → 择校推荐
- `/flashcard 笔记内容` → 生成闪卡
- `/tuition 院校 | 专业` → 学费情报
- `/ratio 院校 | 专业` → 报录比/分数线情报
- `/compare 专业` → 专硕 vs 学硕分析
- `/report 院校 | 专业` → 一键深度分析报告
- `/help` → 帮助

## 📁 项目结构

```
gradexam-ai-copilot/
├── main.py              # FastAPI 入口（API + 飞书 Webhook）
├── streamlit_app.py     # Web UI
├── config.py            # 全局配置
├── requirements.txt
├── .env.example
├── app/
│   ├── rag/             # RAG 问答
│   ├── essay/           # 作文批改
│   ├── planner/         # 规划择校
│   ├── flashcard/       # 闪卡生成
│   ├── research/        # 全网情报（学费/报录比/专硕学硕/深度报告）
│   └── feishu/          # 飞书机器人
├── data/
│   └── sample_report.md # 真实数据示例报告（复旦·应用心理）
└── docs/
    ├── DEPLOYMENT.md
    └── FEISHU_SETUP.md
```

## 📄 License

MIT
