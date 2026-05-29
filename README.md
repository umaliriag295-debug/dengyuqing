# 企业微信 × Codex 桥接

将 Codex AI 接入企业微信，实现 AI 聊天机器人。

## 架构

`
用户 → 企业微信 → 回调URL → Flask服务器 → OpenAI API → 回复
`

## 部署步骤

### 1. 企业微信后台配置

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin)
2. 应用管理 → 创建自建应用
3. 记录: 企业ID、AgentId、Secret
4. 接收消息 → 设置API接收
   - URL: https://你的域名/wechat
   - Token: 随机字符串 (自己填)
   - EncodingAESKey: 随机生成
   - 先保存Token和Key,后续填入 config.py

### 2. 配置

编辑 config.py:

`
CORP_ID = "ww1234567890abcdef"        # 企业ID
CORP_SECRET = "your_secret_here"       # 应用Secret
AGENT_ID = 1000002                     # 应用AgentId
TOKEN = "your_random_token"            # 接收消息Token
ENCODING_AES_KEY = "your_aes_key"      # 接收消息EncodingAESKey
OPENAI_API_KEY = "sk-..."              # OpenAI API Key
`

### 3. 启动

`ash
pip install -r requirements.txt
python server.py
`

### 4. 暴露公网

使用 ngrok 或 frp 将本地 8080 端口暴露到公网:

`ash
ngrok http 8080
`

将 ngrok 提供的 HTTPS 地址填入企业微信回调 URL。

### 5. 验证

企业微信后台点击「保存」会发送验证请求。server.py 启动后会自动处理。

## 功能

- 多用户独立会话上下文 (每人独立对话)
- 发送 /clear 清空对话历史
- 自动消息加解密
