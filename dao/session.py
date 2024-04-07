import logging
import time
import uuid
from typing import List
from azure.cosmos import CosmosClient
from configs.constants import cosmos_url, cosmos_credential
from utils.util import get_message_id


class SessionDAO:
    def __init__(self) -> None:
        self.client = CosmosClient(url=cosmos_url, credential=cosmos_credential)
        self.database = self.client.get_database_client("vulcan")
        self.session_container = self.database.get_container_client("SessionMessages")

    def save_session_message(
        self, session_id: str, msg: str, role: str, source: str
    ) -> None:
        data = {
            "session_id": session_id,
            "timestamp": time.time(),
            "message_id": get_message_id(session_id, msg),
            "content": msg,
            "role": role,
            "type": "text",
            "source": source,
        }
        logging.info(f"Saving session message: {data}")
        self.session_container.create_item(data, enable_automatic_id_generation=True)

    def get_session(self, session_id: str) -> List[dict]:
        iterative_rst = self.session_container.query_items(
            f"SELECT * FROM c WHERE c.session_id = '{session_id}'"
        )
        rst = list(iterative_rst)
        rst.sort(key=lambda x: x["timestamp"])
        logging.info(f"Got session messages: {rst} id: {session_id}")
        return list(rst)

    def get_latest_n_messages(self, session_id: str, n: int) -> List[str]:
        dialog_history = self.get_session(session_id)
        last_n_messages = list(
            map(
                lambda x: {"content": x["content"], "role": x["role"]},
                dialog_history[-n:],
            )
        )
        logging.info(f"Got last n messages: {last_n_messages}")
        return last_n_messages
