"""
Author: Luigi Saetta
Date created: 2024-05-20
Date last modified: 2024-05-23

Usage:
    This module handles the creation of the Vector Store 
    used in the RAG chain, based on config

Python Version: 3.11
"""

import logging
import oracledb

from py_zipkin.zipkin import zipkin_span

from langchain_community.vectorstores.utils import DistanceStrategy

from oraclevs_4_apm import OracleVS4APM
from utils import load_configuration

from config_private import (
    DB_USER,
    DB_PWD,
    DB_HOST_IP,
    DB_SERVICE,
)

#
# Configs
#
config = load_configuration()
SERVICE_NAME = "Factory Vector Store"


@zipkin_span(service_name=SERVICE_NAME, span_name="get_connection")
def get_connection():
    """
    get a DB connection
    """
    dsn = f"{DB_HOST_IP}:1521/{DB_SERVICE}"

    conn = oracledb.connect(user=DB_USER, password=DB_PWD, dsn=dsn, retry_count=3)

    return conn


@zipkin_span(service_name=SERVICE_NAME, span_name="get_vector_store")
def get_vector_store(vector_store_type, embed_model):
    """
    vector_store_type: can be 23AI
    embed_model an object wrapping the model used for embedings
    return a Vector Store Object
    """

    logger = logging.getLogger("ConsoleLogger")

    v_store = None

    if vector_store_type == "23AI":
        try:
            connection = get_connection()

            v_store = OracleVS4APM(
                client=connection,
                table_name=config["vector_store"]["collection_name"],
                distance_strategy=DistanceStrategy.COSINE,
                embedding_function=embed_model,
            )
        except oracledb.Error as e:
            err_msg = "An error occurred in get_vector_store: " + str(e)
            logger.error(err_msg)

    return v_store
