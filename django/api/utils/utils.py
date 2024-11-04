import requests
import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

from pinecone import Pinecone
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
