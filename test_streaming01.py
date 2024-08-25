"""
To test streaming
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span
from transport import http_transport

from chatocigenai_4_apm import ChatOCIGenAI4APM
from utils import load_configuration

from config_private import COMPARTMENT_ID

config = load_configuration()

model_id = config["llm"]["oci"]["llm_model"]
max_tokens = config["llm"]["max_tokens"]
temperature = config["llm"]["temperature"]


def test_stream(the_llm, messages):
    """
    Call the chat model in streaming mode

    return: generator
    """

    with zipkin_span(
        service_name="test_streaming01",
        span_name="test_streaming",
        transport_handler=http_transport,
        encoding=Encoding.V2_JSON,
        binary_annotations={"conv_id": "test01"},
        sample_rate=100,
    ) as span:
        response = the_llm.stream(messages)

        print("")
        for chunk in response:
            print(chunk.content, end="", flush=True)


#
# Main test
#
llm = ChatOCIGenAI4APM(
    model_id=model_id,
    service_endpoint=config["llm"]["oci"]["endpoint"],
    compartment_id=COMPARTMENT_ID,
    is_stream=True,
    model_kwargs={"temperature": temperature, "max_tokens": max_tokens},
)

messages = [
    SystemMessage(content="your are an AI assistant."),
    AIMessage(content="Hi there human!"),
    HumanMessage(content="Who is Larry Ellison?"),
]

test_stream(llm, messages)
