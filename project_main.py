from crews.file_crew import final_generator
from crews.summary_crew import get_file_summary
from data_pipeline.git_details import get_repo_latest_commit
from data_pipeline.git_ingest import repo_file_details
from data_pipeline.sf_details import fetch_sf_latest_commit, fetch_sf_repo



async def main_func(repo, file_type):

    sf_repo_value = fetch_sf_repo(repo)
        
    if sf_repo_value == repo:
        latest_commit_id = get_repo_latest_commit(repo)
        sf_latest_commit_id = fetch_sf_latest_commit(repo)
        
        if latest_commit_id == sf_latest_commit_id:

            return 'No change in readme file'

        else:
            pass

    else:

        file_summary_list = []

        try:
            file_dict, tree = await repo_file_details(repo)
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        for key, file in file_dict.items():
            #print(key)
            result = get_file_summary(repo, key, file, tree)
            file_summary_list.append(result)

        #file_summary_list.append(get_file_summary(repo, file, tree))

        final_file = final_generator(file_summary_list, file_type)

        if file_type == 'codelab':
                
                metadata_block = """
                summary: Learn how to build this project with detailed steps.
                id: auto-doc-ai-codelab
                categories: Python, SQL, C, Java
                status: Published
                authors: Auto Doc AI
                feedback link: https://your-feedback-link.com
                """

                final_file = metadata_block + final_file

    return final_file
    


#repo = 'https://github.com/hishitathakkar/LLM-Powered-Document-Intelligence-RAG-Pipeline-'
#repo = 'https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions'
#file_type = 'codelab'

#result = main_func(repo, file_type)
#print(result)