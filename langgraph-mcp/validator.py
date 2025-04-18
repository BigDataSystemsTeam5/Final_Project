import os
import sys
import json
import re
import requests
from typing import Dict, List, Any, Tuple, Optional, Literal, TypedDict, Union, Annotated
from enum import Enum
import asyncio
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import LangGraph components
from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.graph.message import ChatMessage, AIMessage, HumanMessage

# Import Claude and OpenAI clients
from anthropic import Anthropic
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize API clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define state models with Pydantic
class FileContent(BaseModel):
    filename: str
    content: str

class ProjectData(BaseModel):
    repo_url: str
    repo_summary: str
    readme: Optional[FileContent] = None
    codelab: Optional[FileContent] = None

class ValidationFeedback(BaseModel):
    accuracy_issues: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)

class ValidationResults(BaseModel):
    readme_feedback: Optional[ValidationFeedback] = None
    codelab_feedback: Optional[ValidationFeedback] = None

class RegeneratedFiles(BaseModel):
    readme: Optional[str] = None
    codelab: Optional[str] = None

class GraphState(BaseModel):
    project_data: ProjectData
    validation_results: Optional[ValidationResults] = None
    regenerated_files: Optional[RegeneratedFiles] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    current_file: Literal["readme", "codelab", None] = None
    error: Optional[str] = None

# GitHub API helpers
def fetch_github_repo_summary(repo_url: str) -> str:
    """Fetch summary information about a GitHub repository"""
    # Extract owner and repo name from URL
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, repo_url)
    
    if not match:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    owner, repo = match.groups()
    
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if github_token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {github_token}"
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    repo_data = response.json()
    
    # Fetch README content
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    readme_response = requests.get(readme_url, headers=headers)
    readme_content = ""
    if readme_response.status_code == 200:
        readme_data = readme_response.json()
        import base64
        readme_content = base64.b64decode(readme_data["content"]).decode("utf-8")
    
    # Construct summary
    summary = f"""
    Repository: {repo_data['full_name']}
    Description: {repo_data['description'] or 'No description provided'}
    Stars: {repo_data['stargazers_count']}
    Forks: {repo_data['forks_count']}
    Language: {repo_data['language']}
    Topics: {', '.join(repo_data.get('topics', ['None']))}
    
    README Preview:
    {readme_content[:500]}{'...' if len(readme_content) > 500 else ''}
    """
   
    return summary

# Node implementations
def initialize_validation(state: GraphState) -> GraphState:
    """Initialize the validation process"""
    # Create messages list with initial instruction
    messages = [
        HumanMessage(content=f"""
        I need you to validate and improve documentation files for the following GitHub repository:
        {state.project_data.repo_url}
        
        Repository Summary:
        {state.project_data.repo_summary}
        
        I'll provide the generated README and Codelab files for validation.
        """)
    ]
    
    return GraphState(
        project_data=state.project_data,
        messages=messages
    )

def validate_with_claude(state: GraphState) -> GraphState:
    if state.current_file == "readme" and state.project_data.readme:
        file_content = state.project_data.readme.content
        file_type = "README"
    elif state.current_file == "codelab" and state.project_data.codelab:
        file_content = state.project_data.codelab.content
        file_type = "Codelab"
    else:
        return GraphState(
            **state.model_dump(),
            error=f"Missing content for {state.current_file}"
        )
    
    messages = state.messages.copy()
    messages.append(HumanMessage(content=f"""
    Please validate this generated {file_type} file against the repository summary:
    
    ```
    {file_content}
    ```
    
    Provide feedback in these categories:
    1. Accuracy Issues - Any information that contradicts or misrepresents the project
    2. Missing Information - Important details from the repository that should be included
    3. Improvement Suggestions - Ways to make the documentation more helpful
    
    Format your response as JSON with these categories.
    """))
    
    
    response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        messages=messages
    )
    

    claude_content = response.content[0].text
    feedback_json = extract_json_from_text(claude_content)
    

    feedback = ValidationFeedback(
        accuracy_issues=feedback_json.get("accuracy_issues", []),
        missing_information=feedback_json.get("missing_information", []),
        improvement_suggestions=feedback_json.get("improvement_suggestions", [])
    )
    

    validation_results = state.validation_results or ValidationResults()
    
    if state.current_file == "readme":
        validation_results.readme_feedback = feedback
    elif state.current_file == "codelab":
        validation_results.codelab_feedback = feedback
    

    messages.append(AIMessage(content=claude_content))
    
    return GraphState(
        **state.model_dump(),
        validation_results=validation_results,
        messages=messages
    )

def validate_with_openai(state: GraphState) -> GraphState:
    """Use OpenAI to validate the README and Codelab files"""
    # Prepare the prompt for OpenAI
    if state.current_file == "readme" and state.project_data.readme:
        file_content = state.project_data.readme.content
        file_type = "README"
    elif state.current_file == "codelab" and state.project_data.codelab:
        file_content = state.project_data.codelab.content
        file_type = "Codelab"
    else:
        return GraphState(
            **state.model_dump(),
            error=f"Missing content for {state.current_file}"
        )
    

    openai_messages = [
        {"role": "system", "content": """You are a documentation expert who validates technical documentation for accuracy and completeness.
        Provide specific, actionable feedback to improve documentation quality."""},
        {"role": "user", "content": f"""
        Repository Information:
        {state.project_data.repo_summary}
        
        Please validate this generated {file_type} file against the repository summary:
        
        ```
        {file_content}
        ```
        
        Provide feedback in these categories:
        1. Accuracy Issues - Any information that contradicts or misrepresents the project
        2. Missing Information - Important details from the repository that should be included
        3. Improvement Suggestions - Ways to make the documentation more helpful
        
        Format your response as JSON with these categories.
        """}
    ]
    

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=openai_messages,
        temperature=0,
        response_format={"type": "json_object"}
    )
    

    openai_content = response.choices[0].message.content
    feedback_json = json.loads(openai_content)
    

    feedback = ValidationFeedback(
        accuracy_issues=feedback_json.get("accuracy_issues", []),
        missing_information=feedback_json.get("missing_information", []),
        improvement_suggestions=feedback_json.get("improvement_suggestions", [])
    )
    

    validation_results = state.validation_results or ValidationResults()
    
    if state.current_file == "readme":
        # Merge with Claude's feedback if it exists
        if validation_results.readme_feedback:
            feedback.accuracy_issues = list(set(feedback.accuracy_issues + validation_results.readme_feedback.accuracy_issues))
            feedback.missing_information = list(set(feedback.missing_information + validation_results.readme_feedback.missing_information))
            feedback.improvement_suggestions = list(set(feedback.improvement_suggestions + validation_results.readme_feedback.improvement_suggestions))
        validation_results.readme_feedback = feedback
    elif state.current_file == "codelab":
        # Merge with Claude's feedback if it exists
        if validation_results.codelab_feedback:
            feedback.accuracy_issues = list(set(feedback.accuracy_issues + validation_results.codelab_feedback.accuracy_issues))
            feedback.missing_information = list(set(feedback.missing_information + validation_results.codelab_feedback.missing_information))
            feedback.improvement_suggestions = list(set(feedback.improvement_suggestions + validation_results.codelab_feedback.improvement_suggestions))
        validation_results.codelab_feedback = feedback
    

    messages = state.messages.copy()
    messages.append(AIMessage(content=f"OpenAI validation complete for {file_type}"))
    
    return GraphState(
        **state.model_dump(),
        validation_results=validation_results,
        messages=messages
    )

def regenerate_content(state: GraphState) -> GraphState:
    
    # Check if validation results exist
    if not state.validation_results:
        return GraphState(
            **state.model_dump(),
            error="Cannot regenerate content without validation results"
        )
    
    
    if state.current_file == "readme":
        original_content = state.project_data.readme.content if state.project_data.readme else ""
        feedback = state.validation_results.readme_feedback
        file_type = "README"
    elif state.current_file == "codelab":
        original_content = state.project_data.codelab.content if state.project_data.codelab else ""
        feedback = state.validation_results.codelab_feedback
        file_type = "Codelab"
    else:
        return GraphState(
            **state.model_dump(),
            error=f"Invalid file type: {state.current_file}"
        )
    
    if not feedback:
        return GraphState(
            **state.model_dump(),
            error=f"No validation feedback available for {state.current_file}"
        )
    
    
    openai_messages = [
        {"role": "system", "content": """You are a documentation expert who creates high-quality technical documentation.
        Generate improved documentation based on feedback and original content."""},
        {"role": "user", "content": f"""
        Repository Information:
        {state.project_data.repo_summary}
        
        Original {file_type} Content:
        ```
        {original_content}
        ```
        
        Validation Feedback:
        - Accuracy Issues: {json.dumps(feedback.accuracy_issues)}
        - Missing Information: {json.dumps(feedback.missing_information)}
        - Improvement Suggestions: {json.dumps(feedback.improvement_suggestions)}
        
        Please generate an improved version of the {file_type} that addresses all the feedback points.
        Maintain the same format and structure when appropriate, but fix all issues and add missing information.
        """}
    ]
    
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=openai_messages,
        temperature=0.2,
        max_tokens=4000
    )
    
    
    regenerated_content = response.choices[0].message.content
    
    
    regenerated_content = re.sub(r'```[^\n]*\n', '', regenerated_content)
    regenerated_content = re.sub(r'```', '', regenerated_content)
    
    
    regenerated_files = state.regenerated_files or RegeneratedFiles()
    
    if state.current_file == "readme":
        regenerated_files.readme = regenerated_content
    elif state.current_file == "codelab":
        regenerated_files.codelab = regenerated_content
    
    
    messages = state.messages.copy()
    messages.append(AIMessage(content=f"Generated improved {file_type}"))
    
    return GraphState(
        **state.model_dump(),
        regenerated_files=regenerated_files,
        messages=messages
    )

def merge_validation_results(state: GraphState) -> GraphState:
    messages = state.messages.copy()
    
    if state.validation_results:
        readme_feedback = state.validation_results.readme_feedback
        codelab_feedback = state.validation_results.codelab_feedback
        
        
        summary = "# Validation Summary\n\n"
        
        if readme_feedback:
            summary += "## README Validation\n\n"
            summary += "### Accuracy Issues\n"
            for issue in readme_feedback.accuracy_issues:
                summary += f"- {issue}\n"
            
            summary += "\n### Missing Information\n"
            for missing in readme_feedback.missing_information:
                summary += f"- {missing}\n"
                
            summary += "\n### Improvement Suggestions\n"
            for suggestion in readme_feedback.improvement_suggestions:
                summary += f"- {suggestion}\n"
        
        if codelab_feedback:
            summary += "\n## Codelab Validation\n\n"
            summary += "### Accuracy Issues\n"
            for issue in codelab_feedback.accuracy_issues:
                summary += f"- {issue}\n"
            
            summary += "\n### Missing Information\n"
            for missing in codelab_feedback.missing_information:
                summary += f"- {missing}\n"
                
            summary += "\n### Improvement Suggestions\n"
            for suggestion in codelab_feedback.improvement_suggestions:
                summary += f"- {suggestion}\n"
        
        messages.append(AIMessage(content=summary))
    
    return GraphState(
        **state.model_dump(),
        messages=messages
    )

def report_results(state: GraphState) -> GraphState:
    """Generates a final report of validation and regeneration"""
    messages = state.messages.copy()
    report = "# Documentation Validation Report\n\n"
    

    if state.validation_results:
        readme_issues_count = 0
        codelab_issues_count = 0
        
        if state.validation_results.readme_feedback:
            readme_issues_count = (
                len(state.validation_results.readme_feedback.accuracy_issues) +
                len(state.validation_results.readme_feedback.missing_information)
            )
        
        if state.validation_results.codelab_feedback:
            codelab_issues_count = (
                len(state.validation_results.codelab_feedback.accuracy_issues) +
                len(state.validation_results.codelab_feedback.missing_information)
            )
        
        report += f"## Validation Summary\n\n"
        report += f"- README issues found: {readme_issues_count}\n"
        report += f"- Codelab issues found: {codelab_issues_count}\n\n"
    
    if state.regenerated_files:
        report += "## Regenerated Content\n\n"
        
        if state.regenerated_files.readme:
            report += "### Improved README\n\n"
            report += "The README has been regenerated addressing all validation feedback.\n\n"
        
        if state.regenerated_files.codelab:
            report += "### Improved Codelab\n\n"
            report += "The Codelab has been regenerated addressing all validation feedback.\n\n"
    

    if state.error:
        report += f"## Errors\n\n{state.error}\n\n"
    
    messages.append(AIMessage(content=report))
    
    return GraphState(
        **state.model_dump(),
        messages=messages
    )

def extract_json_from_text(text: str) -> Dict[str, Any]:
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    json_pattern = r'({[\s\S]*})'
    json_match = re.search(json_pattern, text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    return {
        "accuracy_issues": [],
        "missing_information": [],
        "improvement_suggestions": []
    }

def build_validation_graph():
    """Build the LangGraph for documentation validation"""
    # Define the graph
    builder = StateGraph(GraphState)
    
    # Add nodes
    builder.add_node("initialize", initialize_validation)
    builder.add_node("validate_with_claude", validate_with_claude)
    builder.add_node("validate_with_openai", validate_with_openai)
    builder.add_node("regenerate_content", regenerate_content)
    builder.add_node("merge_validation", merge_validation_results)
    builder.add_node("report_results", report_results)
    
    # Add edges
    builder.add_edge("initialize", "validate_with_claude")
    builder.add_edge("validate_with_claude", "validate_with_openai")
    builder.add_edge("validate_with_openai", "regenerate_content")
    builder.add_edge("regenerate_content", "merge_validation")
    builder.add_edge("merge_validation", "report_results")
    builder.add_edge("report_results", END)
    
    # Set conditional edges
    builder.add_conditional_edges(
        "validate_with_claude",
        lambda state: "validate_with_openai" if not state.error else "merge_validation"
    )
    
    builder.add_conditional_edges(
        "validate_with_openai",
        lambda state: "regenerate_content" if not state.error else "merge_validation"
    )
    
    builder.add_conditional_edges(
        "regenerate_content",
        lambda state: "merge_validation" if not state.error else "merge_validation"
    )
    
    # Compile the graph
    return builder.compile()

# Create the LangGraph agent
def create_validation_agent():
    """Create a validation agent for README and Codelab files"""
    graph = build_validation_graph()
    
    async def run_validation(
        repo_url: str, 
        readme_content: Optional[str] = None, 
        codelab_content: Optional[str] = None
    ):
        """Run the validation process on the provided content"""
        results = {
            "readme": None,
            "codelab": None,
            "validation_summary": None,
            "errors": []
        }
        
        try:
            # Fetch repository summary
            repo_summary = fetch_github_repo_summary(repo_url)
            
            # Prepare project data
            project_data = ProjectData(
                repo_url=repo_url,
                repo_summary=repo_summary
            )
            
            if readme_content:
                project_data.readme = FileContent(
                    filename="README.md",
                    content=readme_content
                )
            
            if codelab_content:
                project_data.codelab = FileContent(
                    filename="CODELAB.md",
                    content=codelab_content
                )
            
            # Run validation for README if provided
            if readme_content:
                initial_state = GraphState(
                    project_data=project_data,
                    current_file="readme"
                )
                
                readme_stream = graph.astream(initial_state)
                
                async for event in readme_stream:
                    if event["event"] == "agent:action":
                        pass  # Process agent actions if needed
                
                final_state = event["data"]
                
                if final_state.regenerated_files and final_state.regenerated_files.readme:
                    results["readme"] = final_state.regenerated_files.readme
                
                if final_state.error:
                    results["errors"].append(f"README validation error: {final_state.error}")
            
            # Run validation for Codelab if provided
            if codelab_content:
                initial_state = GraphState(
                    project_data=project_data,
                    current_file="codelab"
                )
                
                codelab_stream = graph.astream(initial_state)
                
                async for event in codelab_stream:
                    if event["event"] == "agent:action":
                        pass  # Process agent actions if needed
                
                final_state = event["data"]
                
                if final_state.regenerated_files and final_state.regenerated_files.codelab:
                    results["codelab"] = final_state.regenerated_files.codelab
                
                if final_state.error:
                    results["errors"].append(f"Codelab validation error: {final_state.error}")
            
            # Generate validation summary
            if readme_content or codelab_content:
                # Create a merged state with all validation results
                merged_state = GraphState(
                    project_data=project_data,
                    validation_results=ValidationResults(
                        readme_feedback=final_state.validation_results.readme_feedback if readme_content else None,
                        codelab_feedback=final_state.validation_results.codelab_feedback if codelab_content else None
                    ),
                    regenerated_files=RegeneratedFiles(
                        readme=results["readme"],
                        codelab=results["codelab"]
                    )
                )
                
                # Generate report
                final_report_state = report_results(merged_state)
                
                # Extract validation summary from the last message
                if final_report_state.messages:
                    results["validation_summary"] = final_report_state.messages[-1].content
        
        except Exception as e:
            results["errors"].append(f"Validation process error: {str(e)}")
        
        return results
    
    return run_validation

# CLI interface
async def main():
    """Command-line interface for the validation agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate and improve README and Codelab files")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("--readme", help="Path to README file")
    parser.add_argument("--codelab", help="Path to Codelab file")
    parser.add_argument("--output-dir", default="./improved", help="Directory to save improved files")
    
    args = parser.parse_args()
    
    # Read input files
    readme_content = None
    if args.readme and os.path.exists(args.readme):
        with open(args.readme, "r") as f:
            readme_content = f.read()
    
    codelab_content = None
    if args.codelab and os.path.exists(args.codelab):
        with open(args.codelab, "r") as f:
            codelab_content = f.read()
    
    if not readme_content and not codelab_content:
        print("Error: At least one of --readme or --codelab must be provided")
        sys.exit(1)
    
    print(f"Validating documentation for repository: {args.repo_url}")
    
    # Run validation
    validation_agent = create_validation_agent()
    results = await validation_agent(args.repo_url, readme_content, codelab_content)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Save results
    if results["readme"]:
        readme_path = os.path.join(args.output_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(results["readme"])
        print(f"Improved README saved to: {readme_path}")
    
    if results["codelab"]:
        codelab_path = os.path.join(args.output_dir, "CODELAB.md")
        with open(codelab_path, "w") as f:
            f.write(results["codelab"])
        print(f"Improved Codelab saved to: {codelab_path}")
    
    if results["validation_summary"]:
        summary_path = os.path.join(args.output_dir, "validation_summary.md")
        with open(summary_path, "w") as f:
            f.write(results["validation_summary"])
        print(f"Validation summary saved to: {summary_path}")
    
    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"- {error}")

if __name__ == "__main__":
    asyncio.run(main())