"""
For integration with APM
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
    Extension for integration with Application Performance Monitoring (APM).
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
        """
        Invokes the ChatOCIGenAI model with APM integration.

        Args:
            input (LanguageModelInput): The input for the language model.
            config (RunnableConfig, optional): Configuration for the run. Defaults to None.
            stop (List[str], optional): List of stop words. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            BaseMessage: The output from the language model.
        """
        output = super().invoke(input, config=config, stop=stop, **kwargs)

        if self.app_config["general"]["verbose"]:
            # Log input and output messages for debugging purposes
            for msg in input.messages:
                logger.info("Input: %s", msg.content)
            logger.info("Output: %s", output.content)

        return output
