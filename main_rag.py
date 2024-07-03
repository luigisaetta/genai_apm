"""
RAG REST API

to test APM integration
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span

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


def handle_request(request: InvokeInput, conv_id: str):
    """
    handle the request from answer
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
        output = chain.invoke(request.query)

    return output


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

        if detailed_tracing:
            # add output
            span.update_binary_annotations({"genai-chat-output": response})

    return Response(content=response, media_type=MEDIA_TYPE_NOSTREAM)


if __name__ == "__main__":
    if config["apm_tracing"]["enable_tracing"]:
        logger.info("APM tracing is enabled!")

    uvicorn.run(host="0.0.0.0", port=config["general"]["api_port"], app=app)
