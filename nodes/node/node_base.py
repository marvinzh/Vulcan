import json
from typing import Generator


class INode:
    def __init__(self, next, config) -> None:
        raise NotImplementedError()

    def execute(self, input: dict):
        raise NotImplementedError()

    def next(self):
        raise NotImplementedError()


class NodeBase(INode):
    node_name = "undefined"
    as_streamer = False

    def __init__(self, next_node, config) -> None:
        self.next_node = next_node
        self.config = json.dumps(config)
        self.parse_node_config(config)
        self.output_mappings = self.parse_node_output(config)

    def parse_node_config(self, config: dict) -> None:
        """read node configurations into attribute of node"""
        raise NotImplementedError()

    def parse_node_output(self, config) -> list:
        output_mappings = config.get("output_mappings")
        # `End` node does not have output mappings
        if self.node_name != "End":
            assert output_mappings
        return output_mappings

    def _get_input(self, var: str, global_variables: dict):
        if var.startswith("$"):
            var_name = var.lstrip("$")
            if var_name not in global_variables:
                raise RuntimeError(
                    f"variable `{var_name}` not found in global variables"
                )
            return global_variables.get(var_name)
        return var

    def execute(self, global_variables: dict, streaming_input: bool = False) -> list:
        raise NotImplementedError()

    def execute_as_stream(self, global_variables: dict) -> Generator:
        raise NotImplementedError()

    def next(self, global_variables: dict) -> INode:
        return self.next_node
