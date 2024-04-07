from nodes.node.node_base import NodeBase


class Start(NodeBase):
    node_name = "Start"

    def __init__(self, next: NodeBase, config: dict) -> None:
        super().__init__(next, config)

    def parse_node_config(self, config: dict):
        output_mappings = config.get("output_mappings")
        assert output_mappings
        return {"output_mappings": output_mappings}

    def execute(self, global_variables: dict, streaming_input=False):
        output_mappings = self.output_mappings
        return [global_variables.get(field) for field in output_mappings]
