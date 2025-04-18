
import os
import sys
import argparse
import logging
import json
import re
import glob
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import traceback
import tempfile
import subprocess
import shutil
import markdown

# API Client - Anthropic only version
from anthropic import Anthropic

# For repo handling
import git

# Progress bars
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("autodoc.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("autodoc")

# Constants
DEFAULT_MAX_TOKENS = 16000
DEFAULT_TEMPERATURE = 0.1
DEFAULT_CHUNK_SIZE = 8000  # Characters per chunk
MAX_THREADS = 10
IGNORE_DIRS = [".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"]
IGNORE_FILES = [".DS_Store", ".gitignore", "package-lock.json", "yarn.lock"]
FILE_EXTENSIONS = {
    # Programming languages
    "python": [".py"],
    "javascript": [".js", ".jsx", ".ts", ".tsx"],
    "java": [".java"],
    "csharp": [".cs"],
    "cpp": [".cpp", ".hpp", ".cc", ".h", ".c"],
    "go": [".go"],
    "rust": [".rs"],
    "ruby": [".rb"],
    "php": [".php"],
    "swift": [".swift"],
    "kotlin": [".kt", ".kts"],
    "scala": [".scala"],
    "dart": [".dart"],
    "r": [".r", ".R"],
    "perl": [".pl", ".pm"],
    "lua": [".lua"],
    "haskell": [".hs"],
    "julia": [".jl"],
    "shell": [".sh", ".bash"],
    "sql": [".sql"],
    "html": [".html", ".htm"],
    "css": [".css", ".scss", ".sass", ".less"],
    # Config/Data formats
    "json": [".json"],
    "yaml": [".yml", ".yaml"],
    "xml": [".xml"],
    "toml": [".toml"],
    "markdown": [".md", ".markdown"],
    "dockerfile": ["Dockerfile"],
    "makefile": ["Makefile"],
}

def get_extension_language(file_path: str) -> Optional[str]:
    """Determine programming language from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    
    for language, extensions in FILE_EXTENSIONS.items():
        if ext in extensions or filename in extensions:
            return language
    return None

class CodeNarrator:
    """
    Core class handling code analysis and documentation generation.
    """
    
    def __init__(
        self,
        repo_path: str,
        output_dir: str,
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        max_threads: int = MAX_THREADS,
        ignore_dirs: Optional[List[str]] = None,
        ignore_files: Optional[List[str]] = None,
    ):
        """Initialize the CodeNarrator."""
        self.repo_path = os.path.abspath(repo_path)
        self.output_dir = output_dir
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_threads = max_threads
        self.ignore_dirs = IGNORE_DIRS + (ignore_dirs or [])
        self.ignore_files = IGNORE_FILES + (ignore_files or [])
        
        # Initialize client
        self._init_client()
        
        # Create output directory if doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Track processed files and stats
        self.file_count = 0
        self.doc_stats = {
            "files_processed": 0,
            "functions_documented": 0,
            "classes_documented": 0,
            "total_tokens": 0,
            "languages": {}
        }
        
        # Repository metadata
        self.repo_info = self._get_repo_info()
        
        logger.info(f"Initialized CodeNarrator with Anthropic API, model: {self.model}")
        logger.info(f"Repository: {self.repo_info.get('name', 'Unknown')}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _init_client(self):
        """Initialize the Anthropic client."""
        if not self.api_key:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key not provided and not found in ANTHROPIC_API_KEY environment variable")
        self.client = Anthropic(api_key=self.api_key)
            
    def _get_repo_info(self) -> Dict[str, Any]:
        """Gather repository metadata."""
        repo_info = {
            "name": os.path.basename(self.repo_path),
            "path": self.repo_path,
            "files_count": 0,
            "is_git_repo": False,
            "git_url": None,
            "git_default_branch": None,
            "last_commit": None,
        }
        
        # Check if it's a git repository
        git_dir = os.path.join(self.repo_path, ".git")
        if os.path.exists(git_dir) and os.path.isdir(git_dir):
            try:
                repo = git.Repo(self.repo_path)
                repo_info["is_git_repo"] = True
                
                # Get remote URL if available
                if repo.remotes:
                    repo_info["git_url"] = repo.remotes.origin.url
                
                # Get default branch
                repo_info["git_default_branch"] = repo.active_branch.name
                
                # Get last commit info
                last_commit = repo.head.commit
                repo_info["last_commit"] = {
                    "hash": last_commit.hexsha,
                    "author": f"{last_commit.author.name} <{last_commit.author.email}>",
                    "date": last_commit.committed_datetime.isoformat(),
                    "message": last_commit.message.strip(),
                }
            except Exception as e:
                logger.warning(f"Error getting git info: {str(e)}")
        
        return repo_info
    
    def find_files(self) -> List[str]:
        """
        Find all relevant files in the repository for documentation.
        """
        files_list = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                # Skip ignored files
                if file in self.ignore_files:
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                # Skip files with no recognized extension
                language = get_extension_language(file_path)
                if not language:
                    continue
                
                files_list.append(rel_path)
                
                # Update language stats
                if language not in self.doc_stats["languages"]:
                    self.doc_stats["languages"][language] = 0
                self.doc_stats["languages"][language] += 1
        
        self.repo_info["files_count"] = len(files_list)
        logger.info(f"Found {len(files_list)} files to process")
        return files_list
    
    def count_tokens(self, text: str) -> int:
        """Count tokens for a string."""
        # Anthropic uses Claude tokenizer
        # This is an approximation
        return len(text) // 4  # Rough approximation
    
    def chunk_file_content(self, content: str, max_chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
        """Split file content into manageable chunks for the LLM."""
        # If content is small enough, return as single chunk
        if len(content) <= max_chunk_size:
            return [content]
        
        # Try to split at logical boundaries (functions, classes, blank lines)
        chunks = []
        current_chunk = ""
        
        # Split by lines to preserve line breaks
        lines = content.split("\n")
        
        for line in lines:
            # If adding this line would exceed chunk size, save current chunk and start new one
            if len(current_chunk) + len(line) + 1 > max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def generate_completion(self, prompt: str) -> str:
        """Generate completion using Anthropic API."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error calling Anthropic API: {str(e)}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                    raise
        
        return "Error generating documentation."
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file and generate its documentation.
        """
        full_path = os.path.join(self.repo_path, file_path)
        language = get_extension_language(full_path)
        
        if not language:
            return {
                "file_path": file_path,
                "language": "unknown",
                "error": "Unsupported file type"
            }
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return {
                    "file_path": file_path,
                    "language": language,
                    "error": "Empty file"
                }
            
            # For large files, chunk the content
            file_chunks = self.chunk_file_content(content)
            chunk_results = []
            
            for i, chunk in enumerate(file_chunks):
                chunk_prompt = self._create_file_analysis_prompt(
                    file_path=file_path,
                    language=language,
                    content=chunk,
                    chunk_info=(i+1, len(file_chunks)) if len(file_chunks) > 1 else None
                )
                
                chunk_result = self.generate_completion(chunk_prompt)
                chunk_results.append(chunk_result)
                
                # Update token stats
                self.doc_stats["total_tokens"] += self.count_tokens(chunk_prompt) + self.count_tokens(chunk_result)
            
            # Combine chunk results if needed
            if len(chunk_results) > 1:
                combined_result = self._combine_chunk_analyses(chunk_results, file_path, language)
                final_result = combined_result
            else:
                final_result = chunk_results[0]
            
            # Parse result to get stats
            doc_data = self._parse_documentation_result(final_result, language)
            
            # Update stats
            self.doc_stats["files_processed"] += 1
            self.doc_stats["functions_documented"] += doc_data.get("functions_count", 0)
            self.doc_stats["classes_documented"] += doc_data.get("classes_count", 0)
            
            return {
                "file_path": file_path,
                "language": language,
                "documentation": final_result,
                "metadata": doc_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "file_path": file_path,
                "language": language,
                "error": str(e)
            }
    
    def _create_file_analysis_prompt(self, file_path: str, language: str, content: str, chunk_info: Optional[Tuple[int, int]] = None) -> str:
        """Create a prompt for file analysis."""
        chunk_desc = f" (chunk {chunk_info[0]} of {chunk_info[1]})" if chunk_info else ""
        
        prompt = f"""
You are a Code Narrator, an expert in documenting and explaining code. Analyze this {language} file{chunk_desc}: {file_path}

CODE:
```{language}
{content}
```

Provide a detailed documentation analysis with the following structure:

1. FILE OVERVIEW
- Filename: {os.path.basename(file_path)}
- Purpose: [Brief description of the file's purpose]
- Key functionality: [Main capabilities provided]

2. DETAILED BREAKDOWN
[For each class, function, method, important variable or constant]:
- Name
- Purpose
- Parameters (if applicable)
- Return values (if applicable)
- Dependencies
- Key algorithms or logic
- Any notable design patterns or practices

3. CODE QUALITY ASSESSMENT
- Strengths
- Potential improvements
- Readability
- Maintainability
- Edge cases or error handling

4. INTEGRATION CONTEXT
- How this file integrates with other components
- Dependencies on other modules
- External APIs or services used

Format your response as structured markdown with appropriate headings and sections.
Be specific and technical in your analysis, focusing on the actual functionality present in the code.
"""

        return prompt
    
    def _combine_chunk_analyses(self, chunk_results: List[str], file_path: str, language: str) -> str:
        """Combine analyses from multiple chunks of a large file."""
        # First, try to see if we can simply concatenate the results
        if len("\n\n".join(chunk_results)) <= self.max_tokens * 4:  # Rough char approximation
            return "\n\n".join(chunk_results)
        
        # If too large, we need to create a meta-analysis
        combined_prompt = f"""
You are processing documentation chunks from a large {language} file: {file_path}

I have previously analyzed this file in {len(chunk_results)} separate chunks, and now need to create a consolidated documentation.
Here are the separate chunk analyses:

{"=" * 40}
{chunk_results[0][:2000]}  # Preview of first chunk
...
{chunk_results[-1][:2000]}  # Preview of last chunk
{"=" * 40}

Create a consolidated documentation that:
1. Provides a comprehensive file overview
2. Lists all important classes and functions
3. Avoids duplication
4. Preserves important details from each chunk
5. Maintains a cohesive structure similar to the individual chunks

Format your response as structured markdown with appropriate headings and sections.
"""
        
        return self.generate_completion(combined_prompt)
    
    def _parse_documentation_result(self, doc_text: str, language: str) -> Dict[str, Any]:
        """Parse documentation results to extract metadata like function count."""
        data = {
            "language": language,
            "functions_count": 0,
            "classes_count": 0,
        }
        
        # Rough estimation of functions and classes documented
        # This is an approximation and may need refinement
        function_patterns = {
            "python": r"def\s+(\w+)",
            "javascript": r"function\s+(\w+)|\(\s*\)\s*=>|\w+\s*:\s*function",
            "java": r"(public|private|protected)?\s+\w+\s+(\w+)\s*\(",
            "csharp": r"(public|private|protected)?\s+\w+\s+(\w+)\s*\(",
            "cpp": r"\w+\s+(\w+)\s*\(",
            "go": r"func\s+(\w+)",
            "rust": r"fn\s+(\w+)",
            "ruby": r"def\s+(\w+)",
            "php": r"function\s+(\w+)",
        }
        
        class_patterns = {
            "python": r"class\s+(\w+)",
            "javascript": r"class\s+(\w+)",
            "java": r"class\s+(\w+)",
            "csharp": r"class\s+(\w+)",
            "cpp": r"class\s+(\w+)",
            "go": r"type\s+(\w+)\s+struct",
            "rust": r"struct\s+(\w+)|enum\s+(\w+)",
            "ruby": r"class\s+(\w+)",
            "php": r"class\s+(\w+)",
        }
        
        # Count function mentions
        if language in function_patterns:
            matches = re.findall(r"- `?(\w+)`?\s*(\(\))?:", doc_text)
            data["functions_count"] = len(matches)
        
        # Count class mentions
        if language in class_patterns:
            matches = re.findall(r"## Class: `?(\w+)`?", doc_text)
            data["classes_count"] = len(matches)
        
        return data
    
    def generate_architecture_doc(self, file_analyses: List[Dict[str, Any]]) -> str:
        """
        Generate high-level architectural documentation for the entire repository.
        """
        # Prepare a summary of the repository for context
        file_summaries = []
        for file_data in file_analyses:
            if "error" in file_data:
                continue
                
            file_path = file_data["file_path"]
            language = file_data["language"]
            
            # Extract a brief summary from the file documentation
            doc = file_data.get("documentation", "")
            summary_lines = []
            in_overview = False
            
            for line in doc.split("\n"):
                if "FILE OVERVIEW" in line or "# Overview" in line:
                    in_overview = True
                elif in_overview and line.startswith("#"):
                    in_overview = False
                elif in_overview and line.strip():
                    summary_lines.append(line)
            
            summary = "\n".join(summary_lines)
            if len(summary) > 300:
                summary = summary[:300] + "..."
            
            file_summaries.append(f"- {file_path} ({language}): {summary}")
        
        # Group files by directory for better structure
        dir_structure = {}
        for file_data in file_analyses:
            if "error" in file_data:
                continue
                
            file_path = file_data["file_path"]
            dir_name = os.path.dirname(file_path)
            
            if not dir_name:
                dir_name = "root"
                
            if dir_name not in dir_structure:
                dir_structure[dir_name] = []
                
            dir_structure[dir_name].append(file_path)
        
        # Create directory structure summary
        dir_summary = []
        for dir_name, files in dir_structure.items():
            dir_summary.append(f"- {dir_name}/ ({len(files)} files)")
            for file in files[:5]:  # Limit to 5 files per directory
                dir_summary.append(f"  - {os.path.basename(file)}")
            if len(files) > 5:
                dir_summary.append(f"  - ... ({len(files) - 5} more files)")
        
        # Create architecture prompt
        repo_name = self.repo_info.get("name", "Unknown")
        prompt = f"""
You are a Code Narrator, an expert in documenting and explaining code architectures. Analyze this repository: {repo_name}

REPOSITORY STRUCTURE:
{os.linesep.join(dir_summary)}

REPOSITORY STATISTICS:
- Total files: {self.repo_info["files_count"]}
- Languages: {", ".join(f"{lang} ({count})" for lang, count in self.doc_stats["languages"].items())}
- Functions: {self.doc_stats["functions_documented"]}
- Classes: {self.doc_stats["classes_documented"]}

REPOSITORY METADATA:
{"- Git URL: " + self.repo_info["git_url"] if self.repo_info.get("git_url") else ""}
{"- Default branch: " + self.repo_info["git_default_branch"] if self.repo_info.get("git_default_branch") else ""}
{"- Last commit: " + self.repo_info["last_commit"]["message"] if self.repo_info.get("last_commit") else ""}

Generate a comprehensive architectural documentation with the following sections:

1. SYSTEM OVERVIEW
- Purpose of the repository
- Key functionality provided
- Target users/use cases

2. ARCHITECTURE DESIGN
- High-level architecture pattern (e.g., MVC, microservices, monolith)
- Key components and their responsibilities
- Component interactions and dependencies
- Data flow diagrams (described textually)

3. DIRECTORY STRUCTURE ANALYSIS
- Explanation of the repository organization
- Purpose of each major directory
- Important configuration files

4. KEY COMPONENTS
- Core modules/services
- Critical classes/functions
- External dependencies and integrations

5. TECHNICAL DECISIONS
- Programming paradigms used
- Design patterns employed
- Notable algorithms
- Performance considerations

6. DEVELOPMENT GUIDELINES
- Setup instructions
- Coding standards observed
- Testing approach
- Documentation conventions

Format your response as structured markdown with appropriate headings.
Be specific and focus on architectural patterns and design decisions rather than implementation details.
"""
        
        architecture_doc = self.generate_completion(prompt)
        
        # Update token stats
        self.doc_stats["total_tokens"] += self.count_tokens(prompt) + self.count_tokens(architecture_doc)
        
        return architecture_doc
    
    def generate_codelab(self, file_analyses: List[Dict[str, Any]]) -> str:
        """Generate a interactive codelab/tutorial for the repository."""
        # Select a few representative files for the codelab
        important_files = []
        
        # Try to find entry points like main files
        entry_patterns = [
            r"main\.py$", r"app\.py$", r"index\.js$", r"server\.js$", 
            r"app\.js$", r"Application\.java$", r"Main\.java$", r"Program\.cs$"
        ]
        
        # First look for main/entrypoint files
        for file_data in file_analyses:
            if "error" in file_data:
                continue
                
            file_path = file_data["file_path"]
            for pattern in entry_patterns:
                if re.search(pattern, file_path):
                    important_files.append(file_data)
                    break
                    
            # Stop once we have a few entry points
            if len(important_files) >= 3:
                break
        
        # If we don't have enough, add other non-error files
        if len(important_files) < 3:
            for file_data in file_analyses:
                if "error" in file_data or file_data in important_files:
                    continue
                    
                important_files.append(file_data)
                
                if len(important_files) >= 3:
                    break
        
        # Extract summaries for these files
        file_examples = []
        for file_data in important_files:
            file_path = file_data["file_path"]
            language = file_data["language"]
            
            # Extract a snippet from the file documentation
            doc = file_data.get("documentation", "")
            snippet_lines = []
            
            for line in doc.split("\n"):
                if line.startswith("```") and language in line:
                    in_code = True
                    continue
                elif line.startswith("```") and in_code:
                    in_code = False
                    break
                elif in_code:
                    snippet_lines.append(line)
            
            code_snippet = "\n".join(snippet_lines)
            if len(code_snippet) > 300:
                code_snippet = code_snippet[:300] + "..."
            
            file_examples.append(f"### {file_path}\n```{language}\n{code_snippet}\n```")
        
        # Create codelab prompt
        repo_name = self.repo_info.get("name", "Unknown")
        prompt = f"""
You are a Code Narrator, an expert in creating interactive codelabs and tutorials. Create a codelab for: {repo_name}

REPOSITORY INFO:
- Name: {repo_name}
- Languages: {", ".join(f"{lang} ({count})" for lang, count in self.doc_stats["languages"].items())}
- Total files: {self.repo_info["files_count"]}

FILE EXAMPLES:
{os.linesep.join(file_examples)}

Create an engaging, step-by-step codelab that helps developers understand and use this repository.
The codelab should follow this structure:

# {repo_name} Codelab

## Introduction
- What is this repository?
- What will you learn in this codelab?
- Prerequisites for following along

## Environment Setup
- Dependencies and requirements
- Installation instructions
- Configuration steps

## Core Concepts
- Key architectural concepts
- Important design patterns
- Data structures and models

## Hands-on Exercises
Create 3-5 progressive exercises that help users understand the codebase:

### Exercise 1: [Basic Task]
- Goal: [What the user will accomplish]
- Steps: [Detailed steps]
- Code example:
```[language]
[Code snippet]
```
- Expected output/outcome

### Exercise 2: [Intermediate Task]
...

## Advanced Usage
- Best practices
- Performance tips
- Common patterns and pitfalls

## Next Steps
- Suggestions for further exploration
- Additional resources
- Related projects

Make sure the codelab is practical, hands-on, and helps users get familiar with the codebase through realistic examples.
Provide concrete code examples for each exercise.
"""
        
        codelab_doc = self.generate_completion(prompt)
        
        # Update token stats
        self.doc_stats["total_tokens"] += self.count_tokens(prompt) + self.count_tokens(codelab_doc)
        
        return codelab_doc
        
    def generate_readme(self, architecture_doc: str) -> str:
        """Generate a comprehensive README for the repository."""
        repo_name = self.repo_info.get("name", "Unknown")
        
        # Extract sections from architecture doc
        overview = ""
        install = ""
        usage = ""
        
        for line in architecture_doc.split("\n"):
            if "SYSTEM OVERVIEW" in line or "# Overview" in line:
                section = "overview"
            elif "SETUP" in line or "INSTALLATION" in line or "# Installation" in line:
                section = "install"
            elif "USAGE" in line or "# Usage" in line:
                section = "usage"
            else:
                if section == "overview" and line.strip() and not line.startswith("#"):
                    overview += line + "\n"
                elif section == "install" and line.strip() and not line.startswith("#"):
                    install += line + "\n"
                elif section == "usage" and line.strip() and not line.startswith("#"):
                    usage += line + "\n"
        
        # Limit section sizes
        overview = overview[:500] + "..." if len(overview) > 500 else overview
        install = install[:300] + "..." if len(install) > 300 else install
        usage = usage[:300] + "..." if len(usage) > 300 else usage
        
        prompt = f"""
You are a Code Narrator, an expert in creating comprehensive documentation. Create a README.md file for: {repo_name}

REPOSITORY INFO:
- Name: {repo_name}
- Languages: {", ".join(f"{lang} ({count})" for lang, count in self.doc_stats["languages"].items())}
- Total files: {self.repo_info["files_count"]}
- Functions: {self.doc_stats["functions_documented"]}
- Classes: {self.doc_stats["classes_documented"]}

OVERVIEW NOTES:
{overview}

INSTALLATION NOTES:
{install}

USAGE NOTES:
{usage}

Create a comprehensive, well-structured README.md file following best practices:

# {repo_name}

[Add a brief, compelling description of the project]

[Include badges where applicable: build status, test coverage, license, etc.]

## Overview

[Expand on the project description, including its purpose, key features, and target users]

## Table of Contents

[Generate a table of contents for the README]

## Installation

[Provide detailed installation instructions]

## Usage

[Explain how to use the project with examples]

## Architecture

[Provide a high-level overview of the architecture]

## API Documentation

[If applicable, include basic API documentation or link to full docs]

## Contributing

[Guidelines for contributing to the project]

## License

[License information]

## Acknowledgments

[Credits and acknowledgments]

Make the README clear, comprehensive, and following standard markdown conventions.
"""
        
        readme_doc = self.generate_completion(prompt)
        
        # Update token stats
        self.doc_stats["total_tokens"] += self.count_tokens(prompt) + self.count_tokens(readme_doc)
        
        return readme_doc
    
    def process_all_files(self) -> List[Dict[str, Any]]:
        """
        Process all files in the repository and generate documentation.
        """
        # Find all files to process
        files = self.find_files()
        
        # Process files with multithreading
        results = []
        with ThreadPoolExecutor(max_workers=min(self.max_threads, len(files))) as executor:
            tasks = {executor.submit(self.analyze_file, file): file for file in files}
            
            # Show progress bar
            with tqdm(total=len(files), desc="Analyzing files") as pbar:
                for future in concurrent.futures.as_completed(tasks):
                    file = tasks[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing {file}: {str(e)}")
                        results.append({
                            "file_path": file,
                            "error": str(e)
                        })
                    finally:
                        pbar.update(1)
        
        return results
    
    def generate_docs(self) -> Dict[str, str]:
        """
        Main method to generate all documentation.
        """
        start_time = time.time()
        logger.info(f"Starting documentation generation for {self.repo_info['name']}")
        
        # Process all files
        file_analyses = self.process_all_files()
        
        # Save individual file documentations
        docs_dir = os.path.join(self.output_dir, "file_docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        for file_data in file_analyses:
            if "error" in file_data:
                continue
                
            file_path = file_data["file_path"]
            doc_content = file_data.get("documentation", "")
            
            # Create directory structure matching repo
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(os.path.join(docs_dir, file_dir), exist_ok=True)
            
            # Save documentation
            doc_file_path = os.path.join(docs_dir, file_path + ".md")
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        logger.info(f"Generated documentation for {self.doc_stats['files_processed']} files")
        
        # Generate high-level documentation
        logger.info("Generating architecture documentation")
        architecture_doc = self.generate_architecture_doc(file_analyses)
        
        logger.info("Generating README")
        readme_doc = self.generate_readme(architecture_doc)
        
        logger.info("Generating Codelab")
        codelab_doc = self.generate_codelab(file_analyses)
        
        # Save high-level docs
        with open(os.path.join(self.output_dir, "ARCHITECTURE.md"), 'w', encoding='utf-8') as f:
            f.write(architecture_doc)
            
        with open(os.path.join(self.output_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_doc)
            
        with open(os.path.join(self.output_dir, "CODELAB.md"), 'w', encoding='utf-8') as f:
            f.write(codelab_doc)
        
        # Generate HTML versions for better readability
        try:
            self._generate_html_docs(architecture_doc, readme_doc, codelab_doc)
        except Exception as e:
            logger.warning(f"Error generating HTML docs: {str(e)}")
        
        # Save documentation stats
        with open(os.path.join(self.output_dir, "doc_stats.json"), 'w', encoding='utf-8') as f:
            json.dump(self.doc_stats, f, indent=2)
        
        # Calculate timing
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Documentation generation completed in {total_time:.2f} seconds")
        
        return {
            "architecture": architecture_doc,
            "readme": readme_doc,
            "codelab": codelab_doc
        }
    
    def _generate_html_docs(self, architecture_doc: str, readme_doc: str, codelab_doc: str):
        """Generate HTML versions of the markdown documentation."""
        html_dir = os.path.join(self.output_dir, "html")
        os.makedirs(html_dir, exist_ok=True)
        
        # Simple HTML template
        html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        h1 {
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        h2 {
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        code {
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
            font-size: 85%;
            padding: 0.2em 0.4em;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            font-size: 85%;
            line-height: 1.45;
            overflow: auto;
            padding: 16px;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #dfe2e5;
            color: #6a737d;
            margin: 0;
            padding: 0 1em;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        table th, table td {
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }
        table tr {
            background-color: #fff;
            border-top: 1px solid #c6cbd1;
        }
        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }
        img {
            max-width: 100%;
        }
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }
        .nav {
            margin-bottom: 20px;
            padding: 10px 0;
            border-bottom: 1px solid #eaecef;
        }
        .nav a {
            margin-right: 15px;
        }
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html">README</a>
        <a href="architecture.html">Architecture</a>
        <a href="codelab.html">Codelab</a>
    </div>
    <div class="content">
        {content}
    </div>
</body>
</html>
"""
        
        # Convert markdown to HTML
        def md_to_html(md_content, title):
            html_content = markdown.markdown(
                md_content,
                extensions=['extra', 'codehilite', 'tables']
            )
            return html_template.format(title=title, content=html_content)
        
        # Write HTML files
        with open(os.path.join(html_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(md_to_html(readme_doc, "README"))
            
        with open(os.path.join(html_dir, "architecture.html"), 'w', encoding='utf-8') as f:
            f.write(md_to_html(architecture_doc, "Architecture"))
            
        with open(os.path.join(html_dir, "codelab.html"), 'w', encoding='utf-8') as f:
            f.write(md_to_html(codelab_doc, "Codelab"))


def main():
    """Main entry point for the AutoDoc AI CLI."""
    parser = argparse.ArgumentParser(description="AutoDoc AI with Code-Narrator - Generate comprehensive code documentation")
    parser.add_argument("repo_path", help="Path to the repository to document")
    parser.add_argument("--output-dir", "-o", default="autodoc_output", help="Output directory for documentation")
    parser.add_argument("--api-key", help="Anthropic API key (or set via ANTHROPIC_API_KEY environment variable)")
    parser.add_argument("--model", default="claude-3-opus-20240229", help="Anthropic model to use")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Maximum tokens for LLM responses")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help="Temperature for LLM responses")
    parser.add_argument("--max-threads", type=int, default=MAX_THREADS, help="Maximum number of concurrent threads")
    parser.add_argument("--ignore-dirs", nargs="+", help="Additional directories to ignore")
    parser.add_argument("--ignore-files", nargs="+", help="Additional files to ignore")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger("autodoc").setLevel(logging.DEBUG)
    
    # Validate repo path
    if not os.path.exists(args.repo_path):
        print(f"Error: Repository path does not exist: {args.repo_path}")
        return 1
    
    try:
        # Initialize Code Narrator
        narrator = CodeNarrator(
            repo_path=args.repo_path,
            output_dir=args.output_dir,
            api_key=args.api_key,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            max_threads=args.max_threads,
            ignore_dirs=args.ignore_dirs,
            ignore_files=args.ignore_files,
        )
        
        # Generate documentation
        docs = narrator.generate_docs()
        
        print(f"\nDocumentation generated successfully in: {os.path.abspath(args.output_dir)}")
        print(f"Files processed: {narrator.doc_stats['files_processed']}")
        print(f"Functions documented: {narrator.doc_stats['functions_documented']}")
        print(f"Classes documented: {narrator.doc_stats['classes_documented']}")
        print(f"Total tokens used: {narrator.doc_stats['total_tokens']}")
        
        # Open output directory
        if sys.platform == 'win32':
            os.startfile(args.output_dir)
        elif sys.platform == 'darwin':
            subprocess.call(['open', args.output_dir])
        else:
            subprocess.call(['xdg-open', args.output_dir])
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())