from agent_state import AgentState
from logger_code import get_logger

langgraph_logger = get_logger("langgraph_logger", "langgraph_logger.log")

def file_content(state: AgentState):

    langgraph_logger.info('Started file_content step')
    
    file_name = state["current_filename"]
    langgraph_logger.info(f"Current file name in file_content is {file_name}")

    file_index = state["filenames"].index(file_name)
    file_content = state["files"][file_index]

    langgraph_logger.info('Finished file_content step')

    return {"current_file": file_content}