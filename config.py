import os

# 企业微信
CORP_ID = os.environ.get("CORP_ID", "ww273722755ad6c0a5")
CORP_SECRET = os.environ.get("CORP_SECRET", "MC4bSEcvs_4VWuoLBjdogPyMQPQWZ7XJkHSsrdc6HlA")
AGENT_ID = int(os.environ.get("AGENT_ID", "1000002"))
TOKEN = os.environ.get("TOKEN", "d763625beefd05e0")
ENCODING_AES_KEY = os.environ.get("ENCODING_AES_KEY", "E2GFaD4WqbibdHPu1oOsPlHQYhvZCPS5TSfbD124mi0")

# DeepSeek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-fec4cf14d09b4b968e75ecf6c0fc450f")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_SYSTEM_PROMPT = os.environ.get("DEEPSEEK_SYSTEM_PROMPT", "你是一个有用的AI助手，通过企业微信与用户对话。请用中文回复。回复简洁。")

# 服务器
SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get("PORT", "8080"))
