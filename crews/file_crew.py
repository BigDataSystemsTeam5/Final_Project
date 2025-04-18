import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import  FileWriterTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
#from langchain_groq import ChatGroq
#from nltk.tokenize import word_tokenize
#from langchain_deepseek.chat_models import ChatDeepSeek


load_dotenv(r'environment\access.env')

#llm = ChatOpenAI(
#    model="gpt-4.1-mini",
#    openai_api_key=os.environ["OPENAI_API_KEY"],
#    temperature=0
#)

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    temperature=0
)

def final_generator(file_summary_list: list, file_type: str):

    file_write_tool = FileWriterTool()

    #print(file_summary_list)

    full_file = ''

    for file in file_summary_list:
        full_file += file.raw

    #print(full_file)
    #tokens = word_tokenize(file_summary_list)
    #num_tokens = len(tokens)

    #if num_tokens >= 4000: 
    #    source1 = StringKnowledgeSource(
    #        content=file_summary_list,
    #        chunk_size=4000,      
    #        chunk_overlap=200    
    #    )
    #else:
    #source1 = StringKnowledgeSource(content=full_file)

    

    # Content Merger Agent: Merges the content from the two files
    content_merger_agent = Agent(
        role='Content Creator',
        goal="""Write a Readme file with the {content} that has been provided. So when the File Reader agent gives you the message, 
        do not ask for more info from it. use analyse the info given and create a good readme. Pass the created 
        README to the README editor (readme_generator_agent) and try to interact with it whenever it wants info 
        from you.""",
        backstory="You are a skilled synthesizer, capable of combining information from multiple sources into a unified format and create a good readme based on the code report info and style wanted given.",
        verbose=True,
        llm=llm,
        #knowledge_sources=[source1],
        tools=[], 
        max_iterations=100,
        time_limit=300
    )

    # Content Merging Task: Merge the content from the two files into a structured README draft
    content_merging_task = Task(
        description="Using the {content} provided, combine the analyzed sections into a coherent and well-organized README draft. Structure the README in a way that fits well with the identified style, while including the detailed information from the code analysis. Once the draft is created, pass it to the README editor (readme_generator_agent) Agent for final review and improvements. Be sure to interact with the README Editor Agent if it requires further details or clarification.",
        agent=content_merger_agent,
        expected_output="A structured README text draft with the merged content, applying the preferred style to the code analysis.to be passed to the README editor agent."
    )   


    readme_generator_agent = Agent(
        role='README editor',
        goal='Have a review based on the readme file given by the Content Creator and rewrite a final README and edit it well to produce a really cool and detiled Readme file. Add lots of fun things too, for exmaple adding emojies to create a great readme. Try to rewrite it and add emojies or anything other needed for make it perfect. Ensure it is formatted professionally and coherently and write the final README file.',
        backstory="You are an expert technical writer and reviewr for README files, proficient at organizing information into professional documentation formats. You have a great knowledge in the features of the cool README files and try to rewrite readme files to make them great.",
        verbose=True,
        llm=llm,
        tools=[file_write_tool], 
        max_iterations=100,
        time_limit=300
    )


    readme_writing_task = Task(
        description="""Review the draft README provided by the Content Creator (content_merger_agent) Agent. 
        Refine the content for clarity and coherence, making sure that it adheres to professional standards. 
        Add enhancements such as emojis, icons, and other creative elements to make the README engaging and 
        visually appealing. Ensure the README follows best practices for formatting and layout. Once 
        finalized, give the final README content.""",
        agent=readme_generator_agent,
        expected_output="A polished and professionally formatted README content (maybe as string or txt) with added creative touches such as emojis."
    )


    codelab_generator_agent = Agent(
        role='Codelab Author',
        goal="""Create a multi-page interactive Codelab guide that emphasizes *step-by-step explanations* of how to build and deploy the project,
                with minimal code. Focus on guiding the user through concepts, tools used, setup steps, configuration instructions, and architectural decisions.
                Include code only where essential. Also generate a matching `index.html` and `codelab.json` file for seamless deployment via GitHub Pages.""",
        backstory="""You are a world-class technical instructor and documentation expert who creates beginner-friendly, multi-step tutorials.
                     Your guides are instructional and narrative-driven, breaking down complex projects into digestible conceptual steps.
                     You explain *how* to do something, not just *what* to type. You only include code where necessary, and highlight configuration steps, tools setup, and reasoning behind decisions.""",
        verbose=True,
        llm=llm,
        tools=[file_write_tool],
        max_iterations=100,
        time_limit=300
    )


    codelab_writing_task = Task(
        description="""Convert the provided project documentation into a multi-page `codelab.md` tutorial with **minimal code** and **maximum explanation**.
        Focus on:
        - Step-by-step breakdowns of what the user should do at each stage (like setting up environments, choosing tools, creating services, etc.)
        - Explanations of *why* a step is being done, not just how
        - Clear section headers using '##' for each page (e.g., ## Introduction, ## Setup, ## Backend Configuration, ## Deployment, ## Summary)
        - Visual or contextual formatting such as tips, warnings, links to tools or references
        Include code only where absolutely necessary (e.g., installation commands or small critical config). Avoid full blocks of application logic.
        Finally, also generate:
        1. A `codelab.md` with well-organized step-by-step structure
        2. An `index.html` with embedded <google-codelab> pointing to the JSON
        3. A `codelab.json` metadata file linking the markdown tutorial
        All outputs should be ready for direct GitHub Pages deployment without claat.""",
        agent=codelab_generator_agent,
        expected_output="""Three deployable files:
        - `codelab.md` (multi-page tutorial with fewer code blocks, more conceptual steps)
        - `index.html` (Google Codelab web embed)
        - `codelab.json` (metadata config for deployment)"""
    )

 


    if file_type == 'readme':
        agent = [content_merger_agent, readme_generator_agent]
        task = [content_merging_task, readme_writing_task]
        prcocesses=Process.sequential
    elif file_type == 'codelab':
        agent = [content_merger_agent, codelab_generator_agent]
        task = [content_merging_task, codelab_writing_task]
        prcocesses=Process.sequential
    #else:
    #    agent = [content_merger_agent, readme_generator_agent, codelab_generator_agent]
    #    task = [content_merging_task, readme_writing_task, codelab_writing_task]
    #    prcocesses=Process.hierarchical
    

    crew_readme = Crew(
        agents=agent,
        tasks=task,
        process=prcocesses, 
        memory=False,
        verbose=True
    )

    #crew_readme.reset_memories(command_type = 'all')

    # Kickoff the crew - start the process
    final_file = crew_readme.kickoff(inputs={"content":full_file})

    return final_file

