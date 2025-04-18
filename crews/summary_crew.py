import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import  TXTSearchTool
from dotenv import load_dotenv
#from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai_tools import GithubSearchTool
#from nltk.tokenize import word_tokenize
from langchain_openai import ChatOpenAI
#from langchain_deepseek.chat_models import ChatDeepSeek
#from langchain_groq import ChatGroq



load_dotenv(r'environment\access.env')


llm = ChatOpenAI(
    model="gpt-4.1-mini",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    temperature=0
)

#llm = LLM(
#    model="claude-3-7-sonnet-latest",
#    temperature=0.2,
#    api_key=os.environ["CLAUDE_API_KEY"]  
#)


def get_file_summary(repo, key, file, tree):


    #file_write_tool = FileWriterTool()
    text_read_tool = TXTSearchTool()
    
    #print(key)

    # Initialize the tool for semantic searches within a specific GitHub repository
    git_search_tool = GithubSearchTool(
        gh_token = os.getenv("GITHUB_TOKEN2"),
	    content_types=['code','repo'] 
    )
 
    #tokens = word_tokenize(file)
    #num_tokens = len(tokens)

    #if num_tokens >= 2000: 
    #    source1 = StringKnowledgeSource(
    #        content=file,
    #        chunk_size=2000,      
    #        chunk_overlap=200    
    #    )
    #else:
    #source1 = StringKnowledgeSource(content=file)
    #print(source1)
    #source2 = StringKnowledgeSource(content=repo)
    #source3 = StringKnowledgeSource(content=tree)

    text_reader_agent = Agent(
        role="Code File Expert Reader and Analyzer",
        goal="Read the content of each {file} having filename: {filename}. Analyze the file, the problem it addresses, the results obtained, and other important elements. Provide a comprehensive analysis and review for the GitHub agent.",
        backstory="You are an avid reader capable of handling large files and an expert in generating analysis and summary of files. Your task is to go through the file content, handle large files if necessary, and analyze the code file, identifying its key methods, problem scope, and results. Provide an overview with details of everything.",
        verbose=True,
        llm=llm, 
        tools=[text_read_tool], 
        #knowledge_sources=[source1, source3], 
        max_iterations=100,
        time_limit=600
    )

    # File Reading Task
    text_reading_task = Task(
        description="Read the content of file and analyze the code. Identify key methods, the problem addressed, and the results. A {structure} of the repository is provided. Provide a comprehensive analysis. Summarize each provided file separately. For each file, produce a concise summary. If a combined summary is needed, first summarize each file individually, then create a final summary based only on the individual summaries, not by merging the full original file. Do not attempt to process full file together.",
        agent=text_reader_agent,
        expected_output="A comprehensive analysis of the file, problem, and results to be passed to GitHub agent."
    )

    github_agent = Agent(
        role='GitHub Repository Analyst',
        goal="Analyze {repository} structure, validate the file from Code File Expert Reader and Analyzer, and prepare refined documentation",
        backstory="You're a meticulous GitHub specialist who cross-references code summaries against actual repository structures. Your attention to detail ensures documentation accuracy through direct repository inspection and collaborative verification.",
        verbose=True,
        llm=llm, 
        tools=[git_search_tool], 
        #knowledge_sources=[source2], 
        max_iterations=1000,
        time_limit=900
    )

    # File Reading Task
    github_task = Task(
        description="You are a detail-oriented GitHub repository analyst agent. Your primary responsibility is to thoroughly inspect the structure, files, and configuration of a given GitHub repository, ensuring that the information provided by the code expert agent resonate with the actual repository contents. You identify any discrepancies, and comments to the original document, and prepare a comprehensive, validated report. Your work guarantees that all downstream documentation is accurate, up-to-date, and reflects the true state of the repository. You cannot go to any other repository.",
        agent=github_agent,
        expected_output=
        """
        A comprehensive summary file
        """
    )


    #report_writer_agent = Agent(
    #    role="Summary Writer",
    #    goal="Generate a structured and detailed summary based on the analysis provided by the Github agent. Organize the analysis into a clear format with sections that are best suitable for the current file.",
    #    backstory="You are a skilled technical writer capable of synthesizing complex technical information into a well-organized summary. Use the analysis provided by the GitHub agent to generate a file summary.",
    #    verbose=True,
    #    llm=llm, 
    #    tools=[], 
    #    max_iterations=100,
    #    time_limit=600
    #)
#
    ## Report Writing Task
    #report_writing_task = Task(
    #    description="Take the analysis from the Text Expert Reader and Analyzer agent and generate a detailed, structured report. Organize the content into a professional format with an introduction, methods, results, and conclusion.",
    #    agent=report_writer_agent,
    #    expected_output="A detailed written summary based on the analysis of the practice code."
    #)


    summary_crew = Crew(
        agents=[text_reader_agent, github_agent],
        tasks=[text_reading_task, github_task],
        process=Process.sequential, 
        memory=False,
        verbose=True
    )

    #summary_crew.reset_memories(command_type = 'all')

    # Kickoff the crew - start the process
    file_summary = summary_crew.kickoff(inputs= {"repository":repo, "structure":tree, "filename":key, "file":file})


    return file_summary


