#from typing import Literal
from agent_state import AgentState
from logger_code import get_logger

langgraph_logger = get_logger("langgraph_logger", "langgraph_logger.log")

def decide_file(state: AgentState):
 
    langgraph_logger.info('Started decide_file step')

    remaining_file = "None"

    for file in state["filenames"]:
        if file not in state["processed_filenames"]:
            remaining_file = file

            break

    langgraph_logger.info(f"Current file name in decide_file is {remaining_file}")

    langgraph_logger.info('Finished decide_file step')

    #state["current_filename"] = remaining_file
    return {"current_filename": remaining_file} #, decision

    #remaining_files = [f for f in state["filenames"] if f not in state["processed_filenames"]]
    #return "continue" if remaining_files else "end"



def decider_function(state: AgentState):
    # Route based on the 'decision' value in the result tuple
    file = state["current_filename"]

    if file == "None":
        return "continue_final"
    else:
        return "continue"