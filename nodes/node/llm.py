from typing import Generator
import logging

from nodes.node.node_base import NodeBase
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import ChatPromptTemplate


class LLM(NodeBase):
    """LLM node
    it takes 2 inputs
    1. model_id
    2. prompts: list of prompt that injected to model before feed into user input

    Args:
        NodeBase (_type_): _description_
    """

    node_name = "LLM"
    as_streamer = True

    def __init__(self, next, config) -> None:
        super().__init__(next, config)

    def parse_node_config(self, config):
        model_id = config.get("model_id")
        prompts = config.get("prompts")
        assert model_id and prompts
        self.model_id = model_id
        self.prompts = prompts
        self.use_history = config.get("use_history")

    def get_model(self, model_id):
        llm = BedrockChat(model_id=model_id)
        return llm

    def get_prompts(self, prompts, history=None):
        prompt_messages = []
        for prompt_config in prompts:
            role = prompt_config.get("role")
            prompt = prompt_config.get("prompt")
            prompt_messages.append((role, prompt))

        if history:
            for message in history:
                role = message.get("role")
                content = message.get("content")
                prompt_messages.insert(-1, (role, content))

        return ChatPromptTemplate.from_messages(prompt_messages)

    def execute(self, global_variables: dict, streaming_input: bool = False) -> list:
        if streaming_input:
            return super().execute(global_variables, streaming_input)

        model_id = self._get_input(self.model_id, global_variables)
        llm = self.get_model(model_id)
        if self.use_history:
            prompt = self.get_prompts(self.prompts, global_variables.get("_history"))
        else:
            prompt = self.get_prompts(self.prompts)
        prompt_str = prompt.invoke(global_variables)
        logging.info(f"prompt: {prompt_str}")
        return [llm.invoke(prompt_str).content.strip()]

    def execute_as_stream(self, global_variables: dict) -> Generator:
        model_id = self._get_input(self.model_id, global_variables)
        llm = self.get_model(model_id)
        if self.use_history:
            prompt = self.get_prompts(self.prompts, global_variables.get("_history"))
        else:
            prompt = self.get_prompts(self.prompts)
        prompt_str = prompt.invoke(global_variables)
        logging.info(f"prompt: {prompt_str}")
        for message in llm.stream(prompt_str):
            yield [message.content]
