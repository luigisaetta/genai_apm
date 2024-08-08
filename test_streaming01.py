"""
To test streaming
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from chatocigenai_4_apm import ChatOCIGenAI4APM

from utils import load_configuration

from config_private import COMPARTMENT_ID

config = load_configuration()

model_id = config["llm"]["oci"]["llm_model"]
max_tokens = config["llm"]["max_tokens"]
temperature = config["llm"]["temperature"]

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
    HumanMessage(content="Who is larry Ellison?"),
]

response = llm.stream(messages)

for chunk in response:
    print(chunk.content, end="", flush=True)
