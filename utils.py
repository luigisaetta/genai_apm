"""
Utils
"""

import re
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


def sanitize_parameter(param):
    """
    the function sanitize the params input to the REST API

    for now used for conv_id

    could we make it better?
    """
    # Whitelist: alphanumeric characters and a few special characters
    whitelist = re.compile(r"[^a-zA-Z0-9._\-]")
    # Replace any character not in the whitelist with an empty string
    sanitized_param = re.sub(whitelist, "", param)

    return sanitized_param
