from agent_state import AgentState


def decider_function(state: AgentState):
    # Route based on the 'decision' value in the result tuple
    file = state["current_filename"]
    print(file)
    if file == "None":
        return "end"
    else:
        return "continue"