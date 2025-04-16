from langgraph.graph import StateGraph, END
from git_ingest import repo_file_details
from current_file_content import file_content
from file_decision import decide_file, decider_function
from snowflake_insert import snowflake_store_repo, snowflake_store_file
from repo_decision import decide_repo, fetch_repo
from readme import generate_project_overview
from summarize_file import generate_summary
from agent_state import AgentState
#from IPython.display import Image

# Initialize graph with FileState
builder = StateGraph(AgentState)

builder.add_node("fetch_repo", fetch_repo)
builder.add_node("repo_file_details", repo_file_details)
builder.add_node("snowflake_store_repo", snowflake_store_repo)
builder.add_node("decide_file", decide_file)
builder.add_node("file_content", file_content)
builder.add_node("generate_summary", generate_summary)
builder.add_node("snowflake_store_file", snowflake_store_file)
builder.add_node("generate_project_overview", generate_project_overview)

builder.set_entry_point("fetch_repo")

builder.add_conditional_edges(
    source="fetch_repo", 
    path=decide_repo,
    path_map={"continue": "repo_file_details", "end": END}
)

builder.add_edge("repo_file_details", "snowflake_store_repo")
builder.add_edge("snowflake_store_repo", "decide_file")
#builder.add_edge("decide_file", "file_content")

# Add conditional edges for file iteration
builder.add_conditional_edges(
    source="decide_file",
    path=decider_function,
    path_map={"continue": "file_content", "continue_final": "generate_project_overview"}, 
)

builder.add_edge("file_content", "generate_summary")
builder.add_edge("generate_summary", "snowflake_store_file")
builder.add_edge("snowflake_store_file", "decide_file")

# Final summary edge
builder.add_edge("generate_project_overview", END)

runnable = builder.compile()

#Image(runnable.get_graph().draw_png())
#Image(runnable.get_graph().draw_mermaid_png())

#png_data = runnable.get_graph().draw_png()
#png_data = runnable.get_graph().draw_mermaid_png()

# Save the image to a file
#with open("langgraph_workflow_2.png", "wb") as file:
#    file.write(png_data)

#print("Image saved as langgraph_workflow_2.png")


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