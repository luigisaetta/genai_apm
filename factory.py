"""
factory.py

integrated with APM tracing
"""

from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from py_zipkin.zipkin import zipkin_span

# these are the extension to add APM tracing
from oci_embeddings_4_apm import OCIGenAIEmbeddingsWithBatch
from chatocigenai_4_apm import ChatOCIGenAI4APM
from factory_vector_store import get_vector_store
from prompts_library import CONTEXT_Q_PROMPT, QA_PROMPT
from utils import load_configuration, get_console_logger

from config_private import COMPARTMENT_ID

config = load_configuration()

SERVICE_NAME = "Factory"
VERBOSE = config["general"]["verbose"]

logger = get_console_logger()


def get_embed_model():
    """
    get the Embeddings Model
    """

    embed_model = OCIGenAIEmbeddingsWithBatch(
        auth_type="API_KEY",
        model_id=config["embeddings"]["oci"]["embed_model"],
        service_endpoint=config["embeddings"]["oci"]["embed_endpoint"],
        compartment_id=COMPARTMENT_ID,
    )

    return embed_model


def get_llm():
    """
    Build and return the LLM client
    """

    model_id = config["llm"]["oci"]["llm_model"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]

    if VERBOSE:
        logger.info("%s as ChatModel...", model_id)

    llm = ChatOCIGenAI4APM(
        # this example uses api_key
        auth_type="API_KEY",
        model_id=model_id,
        service_endpoint=config["llm"]["oci"]["endpoint"],
        compartment_id=COMPARTMENT_ID,
        is_stream=True,
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens},
    )

    return llm


@zipkin_span(service_name=SERVICE_NAME, span_name="build_rag_chain")
def build_rag_chain():
    """
    build the entire rag chain with Langchain LCEL
    """
    embed_model = get_embed_model()

    v_store = get_vector_store(vector_store_type="23AI", embed_model=embed_model)

    # num of docs returned from semantic search
    top_k = config["retriever"]["top_k"]

    retriever = v_store.as_retriever(search_kwargs={"k": top_k})

    chat_model = get_llm()

    # using prompt defined in prompt_library
    # 3/07 modified for chat interface
    history_aware_retriever = create_history_aware_retriever(
        chat_model, retriever, CONTEXT_Q_PROMPT
    )
    question_answer_chain = create_stuff_documents_chain(chat_model, QA_PROMPT)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain
