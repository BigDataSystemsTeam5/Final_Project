from typing import TypedDict, List, Annotated
import operator
#from langchain_core.agents import AgentAction
#from langchain_core.messages import BaseMessage
#from langgraph.store.memory import InMemoryStore


class AgentState(TypedDict):
    repo: str
    structure: str
    snowflake_repo: str
    #chat_history: list[BaseMessage]
    #intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    #count: int  # Tracks number of processed files
    files: List[str]
    filenames: List[str]
    processed_filenames: Annotated[List[str],  operator.add]
    summaries: Annotated[List[str],  operator.add]
    current_filename: str
    current_file: str


#store = InMemoryStore()
#namespace = ("user123", "correlated_files")  # Custom namespace for isolation

