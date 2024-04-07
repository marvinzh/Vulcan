import logging
import json

from workflow.workflow import Workflow
from nodes.node_manager import NodeManager
from nodes.node.node_base import NodeBase
from dao.session import SessionDAO
from utils.util import get_session_id


class IWorkflowInstance:
    def load_nodes(self):
        raise NotImplementedError()

    def execute(self) -> dict:
        raise NotImplementedError()


class WorkflowInstance(IWorkflowInstance):
    def __init__(self, workflow: Workflow):
        self.global_variables = {}
        self.workflow = workflow
        self.load_nodes()
        self.session_dao = SessionDAO()

    def update_global_variables(
        self, variable_names: list, outputs: list, is_streaming_output=False
    ):
        """update output from node into global variables
        if output is from a streamer node, the output segment will be updated to `<node_name>#seg`
        and will be append to `<node_name>`

        Args:
            variable_names (list): list of variable name to be updated in global vars
            outputs (list): value of variables
            is_streaming_output (bool, optional): Defaults to False.
        """
        assert len(variable_names) == len(outputs)
        for var_name, output in zip(variable_names, outputs):
            if is_streaming_output:
                seg_var_name = "#".join([var_name, "seg"])
                self.global_variables[seg_var_name] = output
                self.global_variables[var_name] = (
                    self.global_variables.get(var_name, "") + output
                )
            else:
                self.global_variables[var_name] = output

    def execute(input: dict):
        raise NotImplementedError()

    def execute_as_stream(input: dict):
        raise NotImplementedError()


class SequentialWorkflowInstance(WorkflowInstance):
    def __init__(self, workflow: Workflow):
        super().__init__(workflow)

    def load_nodes(self):
        logging.info(
            "load node for workflow config: %s" % self.workflow.workflow_config
        )
        self.streamer_idx = None
        self.nodes = []
        for i, node_config in enumerate(self.workflow.workflow_config):
            assert len(node_config) == 1
            node_name, config = node_config.popitem()
            node = NodeManager.get_node(node_name, None, config)
            self.nodes.append(node)
            # connect each node
            if len(self.nodes) > 1:
                self.nodes[-2].next_node = self.nodes[-1]

            if node.as_streamer:
                logging.info(f"found streamer node: {node.node_name}, index: {i}")
                self.streamer_idx = i

    def execute_node(
        self, node: NodeBase, global_variables: dict, streaming_input: bool = False
    ):
        outputs = node.execute(global_variables, streaming_input=streaming_input)
        output_mappings = node.output_mappings
        logging.info(
            f"node: `{node.node_name}` update value to: {json.dumps(output_mappings)}"
        )

        assert len(output_mappings) == len(outputs)
        self.update_global_variables(output_mappings, outputs)

    def _execute(self, nodes: list, streaming_input: bool = False):
        for node in nodes:
            self.execute_node(
                node, self.global_variables, streaming_input=streaming_input
            )
            logging.info(
                f"node: `{node.node_name}` updated global_var: {self.global_variables}"
            )
        return self.global_variables

    def execute(self, input: dict) -> dict:
        logging.info(f"execute workflow `{self.workflow.id}`, input: {input}")
        self.global_variables.update(input)
        session_id = get_session_id("", input["kwargs"].get("timestamp"))
        self.global_variables.update({"session_id": session_id})
        self._execute(self.nodes)
        self.session_dao.save_session_message(
            session_id,
            self.global_variables["input"],
            "user",
            None,
        )
        self.session_dao.save_session_message(
            session_id,
            self.global_variables["final_output"],
            "ai",
            # todo, enable source
            "",
        )
        return self.global_variables

    def execute_as_stream(self, input: dict):
        if self.streamer_idx is None:
            raise RuntimeError("streamer node not found")

        nodes_before_streamer = self.nodes[: self.streamer_idx]
        nodes_after_streamer = self.nodes[self.streamer_idx + 1 :]
        streamer_node = self.nodes[self.streamer_idx]

        # obtain global variables before streamer node
        self.global_variables.update(input)
        self._execute(nodes_before_streamer)

        for streamer_output_list in streamer_node.execute_as_stream(
            self.global_variables
        ):
            self.update_global_variables(
                streamer_node.output_mappings,
                streamer_output_list,
                is_streaming_output=True,
            )
            self._execute(nodes_after_streamer, streaming_input=True)
            yield self.global_variables


class TreeWorkflowInstance(WorkflowInstance):
    pass
