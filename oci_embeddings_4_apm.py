"""
Author: Luigi Saetta
Date created: 2024-04-27
Date last modified: 2024-06-27

This version has been instrumented with zipkin for APM integration
Python Version: 3.11

License: MIT
"""

from tqdm.auto import tqdm
from langchain_community.embeddings import OCIGenAIEmbeddings

from py_zipkin.zipkin import zipkin_span

from utils import load_configuration

# convention: the name of the superclass
SERVICE_NAME = "OCIGenAIEmbeddings"


#
# extend OCIGenAIEmbeddings adding batching
#
class OCIGenAIEmbeddingsWithBatch(OCIGenAIEmbeddings):
    """
    in addition to  integration with APM
    add batching to OCIEmebeddings
    with Cohere max # of texts is: 96
    """

    config = load_configuration()

    # instrumented for integration with APM
    @zipkin_span(service_name=SERVICE_NAME, span_name="embed_documents")
    def embed_documents(self, texts):
        """
        in addition to  integration with APM it also add batching
        """
        batch_size = self.config["embeddings"]["oci"]["embed_batch_size"]
        embeddings = []

        if len(texts) > batch_size:
            # do in batch
            for i in tqdm(range(0, len(texts), batch_size)):
                batch = texts[i : i + batch_size]

                embeddings_batch = super().embed_documents(batch)

                # add to the final list
                embeddings.extend(embeddings_batch)
        else:
            # this way we don't display progress bar when we embed a query
            embeddings = super().embed_documents(texts)

        return embeddings
