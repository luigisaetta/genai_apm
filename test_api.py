"""
Test API
"""

import time
from typing import Any, Dict, Optional
import requests


class FastAPIClient:
    """
    Cleint for test of API
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    def invoke(self, conv_id: str, query: str) -> Dict[str, Any]:
        """
        test invoke
        """
        url = f"{self.base_url}/invoke/"
        params = {"conv_id": conv_id}
        json_data = {"query": query}
        response = requests.post(url, params=params, json=json_data, timeout=10)
        response.raise_for_status()

        return response.text

    def count_conversations(self) -> Dict[str, Any]:
        """
        test count conversations
        """
        url = f"{self.base_url}/count_conversations/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def delete(self, conv_id: str) -> Dict[str, Any]:
        """
        test delete conversation
        """
        url = f"{self.base_url}/delete/"
        params = {"conv_id": conv_id}
        response = requests.delete(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":

    base_url = "http://130.61.180.31:8888"

    client = FastAPIClient(base_url)

    # chiamata al metodo invoke
    conv_id = "luigi04"

    queries = [
        "What is Oracle AI Vector Search?",
        "Has it do do with AI and LLM?",
        "Is it a feature of Oracle Database?",
        "What is RAG?",
        "and, tell me, What is HyDE?",
    ]

    try:
        for query in queries:
            response = client.invoke(conv_id, query)

            print("Query:", query)
            print("Response: ", response)
            print("\n\n")

            time.sleep(1)

    except requests.HTTPError as e:
        print(f"Errore durante la chiamata a invoke: {e}")
