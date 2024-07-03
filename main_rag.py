"""
RAG REST API

to test APM integration
"""

from typing import List, Dict
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from factory import build_rag_chain

# customized transport
from transport import http_transport
from utils import load_configuration, get_console_logger

# constants
MEDIA_TYPE_NOSTREAM = "text/plain"
MEDIA_TYPE_NOSTREAM_JSON = "application/json"

#
# Main
#
app = FastAPI()

# global Object to handle conversation history
# key is conv_id
conversations: Dict[str, List[BaseMessage]] = {}

config = load_configuration()
SERVICE_NAME = "DemoGenAIAPM"

logger = get_console_logger()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvokeInput(BaseModel):
    """
    class for the body of the request

    query: the request from the user
    """

    query: str


#
# supporting functions to manage the conversation
# history (add, get)
#
def add_message(conv_id, msg):
    """
    add a msg to a conversation.
    If the conversation doesn't exist create it

    msg: can be HumanMessage, AIMessage
    """

    if conv_id not in conversations:
        # create it
        conversations[conv_id] = []

    # identify the conversation
    conversation = conversations[conv_id]
    # add the msg
    conversation.append(msg)


def get_conversation(v_conv_id):
    """
    return a conversation as List[BaseMessage]
    """
    if v_conv_id not in conversations:
        conversation = []
    else:
        conversation = conversations[v_conv_id]

    return conversation


def handle_request(request: InvokeInput, conv_id: str):
    """
    handle the request from invoke
    """
    # build_rag_chain mark a span (see: factory)
    chain = build_rag_chain()

    # to give more fine grained info, mark another span
    with zipkin_span(
        service_name=SERVICE_NAME,
        span_name="chain_invoke",
        transport_handler=http_transport,
        encoding=Encoding.V2_JSON,
    ):
        # get the chat history
        conversation = get_conversation(conv_id)

        #
        # call the RAG chain
        #
        ai_msg = chain.invoke({"input": request.query, "chat_history": conversation})

        # update the conversation
        add_message(conv_id, HumanMessage(content=request.query))
        # output is an AI message
        add_message(conv_id, AIMessage(content=ai_msg["answer"]))

    return ai_msg


#
# HTTP API methods
#
@app.post("/invoke/", tags=["V1"])
def invoke(request: InvokeInput, conv_id: str):
    """
    This function handle the HTTP request

    conv_id: the id of the conversation, to handle chat_history
    """

    detailed_tracing = config["apm_tracing"]["detailed_tracing"]

    #
    # This starts the APM trace
    #
    with zipkin_span(
        service_name=SERVICE_NAME,
        span_name="rag_invoke",
        transport_handler=http_transport,
        encoding=Encoding.V2_JSON,
        binary_annotations={"conv_id": conv_id},
        sample_rate=100,
    ) as span:
        logger.info("Conversation id: %s", conv_id)

        if detailed_tracing:
            # add input
            span.update_binary_annotations({"genai-chat-input": request.query})

        response = handle_request(request, conv_id)
        # only the text of the response
        answer = response["answer"]

        if detailed_tracing:
            # add output
            span.update_binary_annotations({"genai-chat-output": answer})

    return Response(content=answer, media_type=MEDIA_TYPE_NOSTREAM)


# to clean up a conversation
@app.delete("/delete/", tags=["V1"])
def delete(conv_id: str):
    """
    delete a conversation
    """
    logger.info("Called delete, conv_id: %s...", conv_id)

    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found!")

    del conversations[conv_id]
    return {"conv_id": conv_id, "messages": []}


if __name__ == "__main__":
    if config["apm_tracing"]["enable_tracing"]:
        logger.info("APM tracing is enabled!")

    uvicorn.run(host="0.0.0.0", port=config["general"]["api_port"], app=app)
