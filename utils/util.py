import hashlib
import time


def _get_md5(plain_str: str):
    return hashlib.md5(plain_str.encode()).hexdigest().upper()


def get_session_id(client_ip: str, session_timestamp: str):
    plain_str = f"{client_ip}#{session_timestamp}"
    return "s-" + _get_md5(plain_str)


def get_message_id(session_id: str, content: str):
    plain_str = f"{session_id}#{content}#{str(time.time())}"
    return "msg-" + _get_md5(plain_str)
