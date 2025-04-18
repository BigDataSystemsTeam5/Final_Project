import re
from gitingest import ingest_async
from data_pipeline.logger_code import get_logger
#import nest_asyncio



git_logger = get_logger("git_logger", "git_logger.log")

async def repo_file_details(repo):

    #nest_asyncio.apply()

    git_logger.info('Started repo_file_details step')

    file_dict = {}

    try:
        # Attempt to ingest the repository
        summary, tree, content = await ingest_async(repo)

        #repo_name = repo.split("/")[-1]
        #owner_name = repo.split("/")[-2]

        # Define the delimiter pattern (escape special characters)
        #file_pattern = r"\n=+\nFile: .+\n=+\n"
        file_pattern = r"(?=\n=+\nFile: .+\n=+\n)"

        # Split the content based on the delimiter
        files = re.split(file_pattern, content)

        # Define the regex pattern to match the filename
        filename_pattern = r"File: ([^\n]+)"

        # Find all filenames that match the pattern
        filenames = re.findall(filename_pattern, content)
        #print(filenames)

        for i in range(len(filenames)):
            file_dict[filenames[i]] = files[i]

        for key in list(file_dict.keys()):
            if not key.endswith(('.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.sh', '.bat', '.sql', '.db', '.sqlite', '.ipynb')):
                del file_dict[key]

        newdict = {
        (key.rsplit('/', 1)[-1] if '/' in key else key): value
            for key, value in file_dict.items()
        }

        #for key in newdict.keys():
        #    print(key)   
        git_logger.info('Finished repo_file_details step')

        return newdict, tree
        #return summary

    except Exception as e:
        git_logger.error(f"Error during git ingestion: {e}")

#repo = 'https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions'

#file_dict, tree = repo_file_details(repo)
#print(tree)
#result = repo_file_details(repo)