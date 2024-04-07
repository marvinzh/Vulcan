from nodes.node.node_base import NodeBase


class End(NodeBase):
    """End Node will always be the last node of a Vulcan workflow
    it takes a mandatory parameter `final_output` as input

    """

    node_name = "End"

    def __init__(self, next: NodeBase, config: dict) -> None:
        super().__init__(next, config)

    def parse_node_config(self, config):
        final_output = config.get("final_output")
        assert final_output
        self.final_output = final_output

    def parse_node_output(self, config):
        return ["final_output"]

    def execute(self, global_variables: dict, streaming_input=False) -> list:
        if streaming_input:
            final_output = "#".join([final_output, "seg"])

        final_output_val = self._get_input(self.final_output, global_variables)
        return [final_output_val]
