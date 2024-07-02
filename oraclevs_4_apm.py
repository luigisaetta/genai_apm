"""
OracleVS + extension for APM integration
"""

from typing import Dict, List, Any

from langchain_core.documents.base import Document
from langchain_community.vectorstores.oraclevs import OracleVS

from py_zipkin.zipkin import zipkin_span

from utils import load_configuration


SERVICE_NAME = "OracleVS"


class OracleVS4APM(OracleVS):
    """
    Extension to add tracing vs APM
    """

    config = load_configuration()

    @zipkin_span(service_name=SERVICE_NAME, span_name="similarity_search")
    def similarity_search(
        self, query: str, k: int = 4, filter: Dict[str, Any] | None = None, **kwargs
    ) -> List[Document]:
        """
        to add tracing
        """
        return super().similarity_search(query, k=k, filter=filter, **kwargs)
