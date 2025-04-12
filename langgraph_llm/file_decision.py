#from typing import Literal
from agent_state import AgentState

def decide_file(state: AgentState): #-> Literal["continue", "end"]:
    """Conditional routing function that checks remaining files"""

    remaining_file = "None"
    #decision = None
    for file in state["filenames"]:
        if file not in state["processed_filenames"]:
            remaining_file = file
            #print(remaining_file)
            #decision = "continue"
            break


    #state["current_filename"] = remaining_file
    return {"current_filename": remaining_file} #, decision

    #remaining_files = [f for f in state["filenames"] if f not in state["processed_filenames"]]
    #return "continue" if remaining_files else "end"