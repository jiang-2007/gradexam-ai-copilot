# 飞书机器人配置指南

## 第一步：创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn/)，登录
2. 点击「创建企业自建应用」
3. 填写应用名称（如：考研AIGC助手）、描述、图标
4. 创建后进入应用后台，记下 **App ID** 和 **App Secret**

## 第二步：开启机器人能力

1. 左侧菜单 →「应用能力」→「机器人」
2. 开启机器人，配置机器人名称和头像

## 第三步：配置权限

左侧菜单 →「权限管理」，搜索并开通以下权限：

- `im:message` — 发送消息
- `im:message.receive_v1` — 接收消息事件
- `im:resource` — 上传资源（如需）

## 第四步：配置事件订阅

1. 左侧菜单 →「事件订阅」
2. 请求地址（Webhook URL）填写：`http://你的服务器地址:8000/feishu/webhook`
3. **订阅事件**：添加「接收消息」(`im.message.receive_v1`)
4. 记下 **Verification Token** 和 **Encrypt Key**

> 本地开发可用 [ngrok](https://ngrok.com/) 或 [cpolar](https://www.cpolar.com/) 做内网穿透：
> ```bash
> ngrok http 8000
> # 把 https://xxx.ngrok.io/feishu/webhook 填入飞书后台
> ```

## 第五步：配置 .env

```env
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=
```

## 第六步：发布应用

1. 左侧菜单 →「版本管理与发布」→ 创建版本
2. 提交审核（企业自建应用通常自动通过）
3. 把机器人添加到你的群里，@机器人 即可使用

## 指令示例

| 指令 | 效果 |
|------|------|
| `@机器人 什么是认知失调？` | RAG 知识库问答 |
| `/essay 英语二大作文：科技与生活 \n 你的作文...` | 英语作文批改 |
| `/politics 用矛盾普遍性原理分析... \n 你的答案...` | 政治题批改 |
| `/plan 复旦 \| 应用心理 \| 一般 \| 12 \| 8` | 生成复习计划 |
| `/school 双非 \| 应用心理 \| 370 \| 上海 \| 专硕` | 择校推荐 |
| `/flashcard 弗洛伊德的人格结构理论包括本我自我超我...` | 生成背诵闪卡 |
| `/tuition 复旦大学 \| 应用心理` | 学费情报检索 |
| `/ratio 复旦大学 \| 应用心理` | 报录比/分数线检索 |
| `/compare 应用心理` | 专硕学硕对比 |
| `/report 复旦大学 \| 应用心理` | 一键深度分析报告 |
| `/help` | 查看帮助 |
