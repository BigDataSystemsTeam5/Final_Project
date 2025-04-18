from langgraph.graph import StateGraph, END
from git_ingest import repo_file_details
from current_file_content import file_content
from file_decision import decide_file
from router import decider_function
from readme import generate_project_overview
from summarize_file import generate_summary
from agent_state import AgentState
from IPython.display import Image

# Initialize graph with FileState
builder = StateGraph(AgentState)

#builder.add_node(START, "repo_file_details")
builder.add_node("repo_file_details", repo_file_details)
builder.add_node("decide_file", decide_file)
builder.add_node("file_content", file_content)
builder.add_node("generate_summary", generate_summary)
builder.add_node("generate_project_overview", generate_project_overview)

builder.set_entry_point("repo_file_details")

builder.add_edge("repo_file_details", "decide_file")

#builder.add_conditional_edges(
#    "decide_file",
#    decider_function,
#    {"continue": "file_content", "end": END}
#)
builder.add_edge("decide_file", "file_content")
builder.add_edge("file_content", "generate_summary")
builder.add_edge("generate_summary", "decide_file")

# Add conditional edges for file iteration
builder.add_conditional_edges(
    source="decide_file",
    path=decider_function,
    path_map={"continue": "file_content", "end": "generate_project_overview"}, 
)

# Final summary edge
builder.add_edge("generate_project_overview", END)

runnable = builder.compile()

#Image(runnable.get_graph().draw_png())

# Assuming runnable.get_graph().draw_png() generates the PNG data
png_data = runnable.get_graph().draw_png()

# Save the image to a file
with open("output_image.png", "wb") as file:
    file.write(png_data)

print("Image saved as output_image.png")


initial_state = {
    "repo": "https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions",
    "files": [], 
    "filenames": [],
    "processed_filenames": [],
    "summaries": [],
    "current_filename": None,
    "current_file": None
}

result_state = runnable.invoke(initial_state)

# mcp server integration
from contextlib import asynccontextmanager
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.graph import StateGraph
from langchain_mcp_adapters.client import MultiServerMCPClient

@asynccontextmanager
async def make_graph():
    async with MultiServerMCPClient({
        "autodoc": {
            "command": "python",
            "args": ["mcp_server/autodoc_mcp.py"],
            "transport": "stdio"
        }
    }) as client:
        tools = await client.get_tools()
        executor = ToolExecutor(tools=tools)
        model = ChatOpenAI(model="gpt-4o")

        builder = StateGraph()
        builder.add_node("planner", model)
        builder.add_node("tools", ToolNode(executor))
        builder.add_edge("planner", "tools")
        builder.add_edge("tools", "planner")
        builder.set_entry_point("planner")

        yield builder.compile()
