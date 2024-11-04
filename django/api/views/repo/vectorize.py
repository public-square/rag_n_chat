from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import os
from pinecone import Pinecone
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX'))

def get_github_contents(owner, repo, branch='main', path=''):
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}'
    headers = {}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = f"Token {os.getenv('GITHUB_TOKEN')}"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f'Github API error: {response.status_code}')

    contents = response.json()
    if not isinstance(contents, list):
        return [contents]

    all_contents = []
    for item in contents:
        if item['type'] == 'dir':
            subdir_contents = get_github_contents(owner, repo, branch, item['path'])
            all_contents.extend(subdir_contents)
        else:
            all_contents.append(item)
    return all_contents

def process_file_contents(file_info):
    if file_info['type'] != 'file':
        return None

    valid_extensions = ['.md', '.py']

    if not any(file_info['name'].endswith(ext) for ext in valid_extensions):
        return None

    response = requests.get(file_info['download_url'])
    if response.status_code != 200:
        raise Exception(f'Error fetching file content: {response.status_code}')

    content = response.text
    truncated_content = content[:8000].strip()
    if not truncated_content:
        return None

    embedding_response = client.embeddings.create(input=truncated_content,
    model='text-embedding-ada-002')
    embedding = embedding_response.data[0].embedding

    if len(embedding) != 1536:
        raise ValueError(f'Unexpected embedding dimension: {len(embedding)}')

    return {
        'file_name': file_info['name'],
        'content': truncated_content,
        'download_url': file_info['download_url'],
        'embedding': embedding
    }

def parse_repository_string(repo_string):
    """
    Parse a repository string in the format '/owner/repo/branch' or 'owner/repo/branch'.
    Returns tuple of (owner, repo, branch).
    If branch is not specified, returns 'main' as default.
    Raises ValueError if the format is invalid.
    """
    # Remove leading slash if present
    repo_string = repo_string.lstrip('/')

    # Split the string into parts
    parts = repo_string.split('/')

    if len(parts) < 2 or len(parts) > 3:
        raise ValueError('Repository string must be in format "owner/repo" or "owner/repo/branch"')

    owner = parts[0]
    repo = parts[1]
    branch = parts[2] if len(parts) == 3 else 'main'

    if not owner or not repo:
        raise ValueError('Both owner and repo must be non-empty')

    return owner, repo, branch

@api_view(['POST'])
def vectorize_repository(request):
    """
    Vectorize a GitHub repository's contents and store in Pinecone.

    Accepts POST requests with a JSON body containing:
    {
        'repository': 'owner/repo/branch'  # branch is optional, defaults to 'main'
    }
    The repository string can optionally start with a forward slash.

    Examples:
        {
            'repository': 'microsoft/vscode'  # Uses 'main' branch
        }
        {
            'repository': 'microsoft/vscode/develop'  # Uses 'develop' branch
        }
        {
            'repository': '/microsoft/vscode/main'  # Leading slash is optional
        }

    Returns:
    200 OK: Successfully vectorized repository
    {
        'status': 'success',
        'processed_files': 5,
        'owner': 'owner',
        'repo': 'repo',
        'branch': 'branch'
    }

    400 Bad Request: Invalid input
    {
        'error': '<error message>'
    }

    500 Internal Server Error: Processing error
    {
        'error': '<error message>'
    }
    """
    if not request.data:
        return Response(
            {'error': 'Please provide repository string in the request body'},
            status=status.HTTP_400_BAD_REQUEST
        )

    repository = request.data.get('repository')
    if not repository:
        return Response(
            {'error': 'Repository parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        owner, repo, branch = parse_repository_string(repository)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

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
            return Response(
                {
                    'error': 'No valid files to process in repository: '
                    + f'{owner}/{repo}/{branch}',
                    'github_contents': contents
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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
                'content': file['content']
            }
        } for file in vectorized_files]

        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)

        return Response({
            'status': 'success',
            'processed_files': len(vectorized_files),
            'owner': owner,
            'repo': repo,
            'branch': branch
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
