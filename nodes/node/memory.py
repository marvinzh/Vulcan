from nodes.node.node_base import NodeBase
from dao.session import SessionDAO


class Memory(NodeBase):
    node_name = "memory"

    def __init__(self, next_node, config) -> None:
        super().__init__(next_node, config)
        self.session_dao = SessionDAO()

    def parse_node_config(self, config):
        self.mode = config["mode"]
        self.n = config["n"]
        assert self.n >= 0, "# of historical message should >= 0"

    def parse_node_output(self, config) -> list:
        return ["_history"]

    def execute(self, global_variables: dict, streaming_input: bool = False) -> list:
        if streaming_input:
            return super().execute(global_variables, streaming_input)

        session_id = global_variables.get("session_id")
        chat_history = self.session_dao.get_latest_n_messages(session_id, self.n)
        return [chat_history]
