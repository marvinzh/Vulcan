from typing import Union
from nodes.node.start import Start
from nodes.node.end import End
from nodes.node.llm import LLM
from nodes.node.memory import Memory
from nodes.node.node_base import NodeBase


class NodeManager:
    @staticmethod
    def get_node(node_name, next: NodeBase, config: dict):
        if node_name == "Start":
            return Start(next, config)
        elif node_name == "End":
            return End(next, config)
        elif node_name == "LLM":
            return LLM(next, config)
        elif node_name == "Memory":
            return Memory(next, config)
        else:
            raise ValueError("unknown node name: " + node_name)
