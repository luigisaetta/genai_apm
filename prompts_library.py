"""
prompt library

this has been modified, different from the one in the workshop
"""

from langchain_core.prompts import (
    ChatPromptTemplate,
)

#
# The prompt for the answer from the LLM
#
QA_SYSTEM_PROMPT = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Don't add sentences like: According to the provided context.

{context}"""

QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", QA_SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)

#
# prompt for italian language
#

QA_SYSTEM_PROMPT_IT = """Sei un assistente per task di domanda-risposta. \
Utilizza i frammenti seguenti di testo per rispondere alla domanda. \
Se non conosci la risposta, dici semplicemente che non conosci la risposta. \
Non aggiungere frasi tipo: In base al contesto fornito.

{context}"""

QA_PROMPT_IT = ChatPromptTemplate.from_messages(
    [
        ("system", QA_SYSTEM_PROMPT_IT),
        ("human", "{question}"),
    ]
)
