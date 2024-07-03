"""
for integration with APM
"""

from typing import Any, List

from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import BaseMessage
from langchain_core.language_models import LanguageModelInput
from langchain_community.chat_models import ChatOCIGenAI

from py_zipkin.zipkin import zipkin_span

from utils import load_configuration, get_console_logger


SERVICE_NAME = "ChatOCIGenaAI"

logger = get_console_logger()


class ChatOCIGenAI4APM(ChatOCIGenAI):
    """
    extension for integration with APM
    """

    app_config = load_configuration()

    @zipkin_span(service_name=SERVICE_NAME, span_name="invoke")
    def invoke(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        stop: List[str] | None = None,
        **kwargs: Any
    ) -> BaseMessage:
        # here we call the ChatModel
        output = super().invoke(input, config=config, stop=stop, **kwargs)

        if self.app_config["general"]["verbose"]:
            # logs input/output to/from LLM
            for msg in input.messages:
                logger.info("Input: %s", msg.content)
            logger.info("Output: %s", output.content)

        return output
