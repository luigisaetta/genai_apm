"""
Utils
"""

import re
import logging
from typing import List
import toml
from langchain_core.documents.base import Document

CONFIG_FILE = "config.toml"


def format_docs(docs: List[Document]) -> str:
    """
    Format documents to be nicely presented in the prompt.

    Args:
        docs (List[Document]): List of Document objects to format.

    Returns:
        str: A string with the formatted content of the documents.
    """
    return "\n\n".join(doc.page_content for doc in docs)


def get_console_logger():
    """
    Get a logger that prints to the console.

    Returns:
        logging.Logger: Configured logger for console output.
    """
    logger = logging.getLogger("ConsoleLogger")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(levelname)s:\t  %(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False

    return logger


def load_configuration(config_file: str = CONFIG_FILE) -> dict:
    """
    Read the configuration from a TOML file.

    Args:
        config_file (str): Path to the TOML configuration file. Defaults to CONFIG_FILE.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = toml.load(file)
    except (FileNotFoundError, toml.TomlDecodeError) as e:
        logging.error("Error loading configuration: %s", e)
        raise

    return config


def sanitize_parameter(param: str) -> str:
    """
    Sanitize the parameter input for a REST API.

    Args:
        param (str): The parameter to sanitize.

    Returns:
        str: The sanitized parameter.
    """
    # Whitelist: alphanumeric characters and a few special characters
    whitelist = re.compile(r"[^a-zA-Z0-9._\-]")
    # Replace any character not in the whitelist with an empty string
    sanitized_param = re.sub(whitelist, "", param)

    return sanitized_param
