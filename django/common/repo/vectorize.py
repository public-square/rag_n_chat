from django.conf import settings
from common.utils import parse_repository_string, process_file_contents, get_github_contents
from pinecone import Pinecone

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

def vectorize_repository(repository):
    """
    Vectorize a GitHub repository's contents and store in Pinecone.

    Args:
        repository (str): Repository string in format 'owner/repo/branch'
                        (branch is optional, defaults to 'main')

    Returns:
        dict: A dictionary containing:
            - On success:
                {
                    'status': 'success',
                    'processed_files': <number_of_files>,
                    'owner': <owner>,
                    'repo': <repo>,
                    'branch': <branch>
                }
            - On error:
                {
                    'error': <error_message>,
                    'github_contents': <contents> (optional)
                }

    Raises:
        ValueError: If repository string is invalid
        Exception: If there's an error processing the repository
    """
    owner, repo, branch = parse_repository_string(repository)

    try:
        contents = get_github_contents(owner, repo, branch)
        vectorized_files = []

        for file_info in contents:
            try:
                result = process_file_contents(file_info)
                if result:
                    vectorized_files.append(result)
            except Exception as e:
                # Log the error but continue processing other files
                print(f'Error processing {file_info["name"]}: {str(e)}')

        if not vectorized_files:
            return {
                'error': f'No valid files to process in repository: {owner}/{repo}/{branch}',
                'github_contents': contents
            }

        namespace = f'{owner}/{repo}/{branch}'
        vectors_to_upsert = [{
            'id': f'{namespace}/{file["file_name"]}',
            'values': file['embedding'],
            'metadata': {
                'file_name': file['file_name'],
                'owner': owner,
                'repo': repo,
                'branch': branch,
                'download_url': file['download_url'],
                'text': file['content']
            }
        } for file in vectorized_files]

        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)

        return {
            'status': 'success',
            'processed_files': len(vectorized_files),
            'owner': owner,
            'repo': repo,
            'branch': branch
        }

    except Exception as e:
        return {'error': str(e)}
