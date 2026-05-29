import time
import requests
from config import CORP_ID, CORP_SECRET, AGENT_ID


class WeComAPI:
    """企业微信 API 客户端"""

    BASE = "https://qyapi.weixin.qq.com/cgi-bin"

    def __init__(self):
        self._token: str = None
        self._expires_at: float = 0

    def _get_token(self) -> str:
        now = time.time()
        if self._token and now < self._expires_at - 300:
            return self._token
        resp = requests.get(
            f"{self.BASE}/gettoken",
            params={"corpid": CORP_ID, "corpsecret": CORP_SECRET},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode") != 0:
            raise RuntimeError(f"获取access_token失败: {data}")
        self._token = data["access_token"]
        self._expires_at = now + data["expires_in"]
        return self._token

    def send_text(self, user_id: str, content: str):
        return self._send({
            "touser": user_id,
            "msgtype": "text",
            "agentid": AGENT_ID,
            "text": {"content": content},
        })

    def _send(self, body: dict) -> dict:
        token = self._get_token()
        resp = requests.post(
            f"{self.BASE}/message/send",
            params={"access_token": token},
            json=body,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


wecom = WeComAPI()
