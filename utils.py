"""
Utils
"""

import logging
import toml


def format_docs(docs):
    """
    to add docs nicely formatted in the prompt
    """
    return "\n\n".join(doc.page_content for doc in docs)


def get_console_logger():
    """
    To get a logger to print on console
    """
    logger = logging.getLogger("ConsoleLogger")

    # to avoid duplication of logging
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(levelname)s:\t  %(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False

    return logger


CONFIG_FILE = "config.toml"


def load_configuration():
    """
    read the configuration from toml file
    """
    with open(CONFIG_FILE, "r") as file:
        config = toml.load(file)

    return config
