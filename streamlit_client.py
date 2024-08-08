"""
Streamlit client for RAG API integrated with APM
"""

import streamlit as st
import requests
from langchain_core.messages import HumanMessage, AIMessage

# Configura la tua API endpoint
INVOKE_URL = "http://130.61.180.31:8888/invoke/"
DELETE_URL = "http://130.61.180.31:8888/delete/"

# Constant
USER = "user"
ASSISTANT = "assistant"


def reset_conversation():
    """
    when push the button reset the chat_history
    """
    # chat_history is per session
    st.session_state.chat_history = []

    st.session_state.request_count = 0


def display_msg_on_rerun(chat_hist):
    """
    display all the msgs on rerun
    """
    for msg in chat_hist:
        # transform a msg in a dict
        if isinstance(msg, HumanMessage):
            the_role = USER
        else:
            the_role = ASSISTANT

        message = {"role": the_role, "content": msg.content}

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Funzione per invocare l'API
def invoke_api(conv_id, query):
    """
    invoke the API (RAG)
    """
    response = requests.post(
        INVOKE_URL, params={"conv_id": conv_id}, json={"query": query}, timeout=60
    )
    return response.text


def delete_conversation(conv_id):
    """
    delete a conversation
    """
    response = requests.delete(DELETE_URL, params={"conv_id": conv_id}, timeout=60)
    return response.json()


#
# Main
#
st.title("AI Assistant")

# Sidebar per gestire la conversazione
conv_id = st.sidebar.text_input("Conversation ID", value="0001")

# Inizializza la lista per la cronologia della conversazione
# Initialize chat history
if "chat_history" not in st.session_state:
    reset_conversation()

# Display chat messages from history on app rerun
display_msg_on_rerun(st.session_state.chat_history)

if question := st.chat_input("Hello, how can I help you?"):
    # Display user message in chat message container
    st.chat_message(USER).markdown(question)

    # Add user message to chat history
    st.session_state.chat_history.append(HumanMessage(content=question))

    ai_response = invoke_api(conv_id, question)

    with st.chat_message(ASSISTANT):
        # show output
        st.markdown(ai_response)

        # Add assistant response to chat history
        st.session_state.chat_history.append(AIMessage(content=ai_response))
