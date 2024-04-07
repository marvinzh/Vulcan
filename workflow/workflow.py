from typing import Union
from enum import Enum, unique, auto
import logging


@unique
class WorkflowType(Enum):
    SEQUENTIAL = auto()
    TREE = auto()


class Workflow:
    def __init__(self, workflow_config: Union[list, dict], id: str = None) -> None:
        self._load_workflow_config(workflow_config)
        self.id = id
        logging.info("initialize workflow with config: %s" % self.workflow_config)

    def _load_workflow_config(self, workflow_config: Union[list, dict]):
        self.workflow_config = workflow_config
        if isinstance(workflow_config, list):
            self.workflow_type = WorkflowType.SEQUENTIAL
        elif isinstance(workflow_config, dict):
            self.workflow_type = WorkflowType.TREE
        else:
            raise TypeError(
                "Workflow config must be a list or dict! while workflow_config in type `%s`"
                % type(workflow_config)
            )

    def build(self):
        if self.workflow_type == WorkflowType.SEQUENTIAL:
            from workflow.workflow_instance import SequentialWorkflowInstance

            return SequentialWorkflowInstance(self)
        else:
            raise ValueError()
