import base64
import hashlib
import struct
import time
import xml.etree.ElementTree as ET
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class WXBizMsgCrypt:
    """企业微信消息加解密"""

    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        self.token = token
        self.corp_id = corp_id
        self.aes_key = base64.b64decode(encoding_aes_key + "=")
        if len(self.aes_key) != 32:
            raise ValueError("EncodingAESKey 长度不正确")

    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        """URL验证: 解密echostr返回明文"""
        signature = self._get_signature(timestamp, nonce, echostr)
        if signature != msg_signature:
            raise ValueError("签名验证失败")
        return self._decrypt(echostr)

    def decrypt_msg(self, msg_signature: str, timestamp: str, nonce: str, xml_body: str) -> str:
        """解密消息"""
        root = ET.fromstring(xml_body)
        encrypt = root.find("Encrypt").text
        signature = self._get_signature(timestamp, nonce, encrypt)
        if signature != msg_signature:
            raise ValueError("签名验证失败")
        return self._decrypt(encrypt)

    def encrypt_msg(self, reply_xml: str, nonce: str, timestamp: str = None) -> str:
        """加密回复"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        ciphertext = self._encrypt(reply_xml)
        signature = self._get_signature(timestamp, nonce, ciphertext)
        return (
            f'<xml>'
            f'<Encrypt><![CDATA[{ciphertext}]]></Encrypt>'
            f'<MsgSignature><![CDATA[{signature}]]></MsgSignature>'
            f'<TimeStamp>{timestamp}</TimeStamp>'
            f'<Nonce><![CDATA[{nonce}]]></Nonce>'
            f'</xml>'
        )

    def _get_signature(self, timestamp: str, nonce: str, encrypt: str) -> str:
        items = sorted([self.token, timestamp, nonce, encrypt])
        return hashlib.sha1("".join(items).encode()).hexdigest()

    def _decrypt(self, ciphertext: str) -> str:
        raw = base64.b64decode(ciphertext)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        plaintext = cipher.decrypt(raw)
        pad = plaintext[-1]
        plaintext = plaintext[:-pad]
        content_len = struct.unpack("!I", plaintext[16:20])[0]
        msg = plaintext[20:20 + content_len].decode("utf-8")
        received_corpid = plaintext[20 + content_len:].decode("utf-8")
        if received_corpid != self.corp_id:
            raise ValueError(f"CorpID不匹配: {received_corpid}")
        return msg

    def _encrypt(self, text: str) -> str:
        random_bytes = get_random_bytes(16)
        text_bytes = text.encode("utf-8")
        msg_len = struct.pack("!I", len(text_bytes))
        corp_id_bytes = self.corp_id.encode("utf-8")
        plaintext = random_bytes + msg_len + text_bytes + corp_id_bytes
        pad_len = 32 - len(plaintext) % 32
        plaintext += bytes([pad_len] * pad_len)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        return base64.b64encode(cipher.encrypt(plaintext)).decode()
