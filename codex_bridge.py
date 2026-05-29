import threading
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, DEEPSEEK_SYSTEM_PROMPT

# 全局 session，绕过系统代理
_session = requests.Session()
_session.trust_env = False


class ChatSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.history = [{"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT}]
        self.lock = threading.Lock()

    def send(self, message: str) -> str:
        with self.lock:
            self.history.append({"role": "user", "content": message})
            resp = _session.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": DEEPSEEK_MODEL, "messages": self.history},
                timeout=120,
            )
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply

    def clear(self):
        with self.lock:
            self.history = [{"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT}]


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, ChatSession] = {}
        self._lock = threading.Lock()

    def get(self, user_id: str) -> ChatSession:
        with self._lock:
            if user_id not in self._sessions:
                self._sessions[user_id] = ChatSession(user_id)
            return self._sessions[user_id]

    def clear(self, user_id: str):
        with self._lock:
            if user_id in self._sessions:
                self._sessions[user_id].clear()


session_manager = SessionManager()
