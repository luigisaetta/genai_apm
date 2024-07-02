"""
Test prompt
"""

from langchain import hub
from prompts_library import QA_PROMPT

PROMPTH = hub.pull("rlm/rag-prompt")

print(PROMPTH)
print(type(PROMPTH))

print(QA_PROMPT)
print(type(QA_PROMPT))
