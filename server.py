import time, os, logging
import xml.etree.ElementTree as ET
from flask import Flask, request, Response
from config import TOKEN, ENCODING_AES_KEY, CORP_ID, SERVER_HOST, SERVER_PORT
from wx_crypt import WXBizMsgCrypt
from codex_bridge import session_manager

DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename=os.path.join(DIR, "debug.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)
log = logging.getLogger("wecom")

app = Flask(__name__)
crypt = WXBizMsgCrypt(TOKEN, ENCODING_AES_KEY, CORP_ID)

@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    if request.method == "GET":
        return _handle_verify()
    return _handle_message()

def _handle_verify():
    params = request.args
    log.info(f"VERIFY params: {dict(params)}")
    try:
        echostr = crypt.verify_url(
            params["msg_signature"],
            params["timestamp"],
            params["nonce"],
            params["echostr"],
        )
        log.info(f"VERIFY OK -> {echostr}")
        return Response(echostr, mimetype="text/plain")
    except Exception as e:
        log.error(f"VERIFY FAIL: {e}")
        return Response(f"verify failed: {e}", status=403)

def _handle_message():
    params = request.args
    xml_body = request.data.decode("utf-8")
    try:
        decrypted = crypt.decrypt_msg(
            params["msg_signature"],
            params["timestamp"],
            params["nonce"],
            xml_body,
        )
    except Exception as e:
        return Response(f"decrypt failed: {e}", status=403)

    root = ET.fromstring(decrypted)
    msg_type = root.find("MsgType").text
    user_id = root.find("FromUserName").text

    if msg_type != "text":
        return Response("", mimetype="application/xml")

    content = root.find("Content").text
    if content is None:
        return Response("", mimetype="application/xml")
    content = content.strip()

    if content.lower() in ("/clear", "/清空", "/重置"):
        session_manager.clear(user_id)
        reply = "对话上下文已清空。"
    else:
        reply = session_manager.get(user_id).send(content)

    reply_xml = (
        f"<xml>"
        f"<ToUserName><![CDATA[{user_id}]]></ToUserName>"
        f"<FromUserName><![CDATA[{root.find('ToUserName').text}]]></FromUserName>"
        f"<CreateTime>{int(time.time())}</CreateTime>"
        f"<MsgType><![CDATA[text]]></MsgType>"
        f"<Content><![CDATA[{reply}]]></Content>"
        f"</xml>"
    )
    encrypted = crypt.encrypt_msg(reply_xml, params["nonce"])
    return Response(encrypted, mimetype="application/xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", SERVER_PORT))
    app.run(host=SERVER_HOST, port=port, debug=False)
