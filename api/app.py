import requests
import openai
import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))
EMBEDDING_DIM = os.getenv("EMBEDDING_DIMENSIONS")

def get_github_contents(repo_url, path=''):
    parts = repo_url.strip('/').split('/')
    owner, repo = parts[-2], parts[-1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = f"Token {os.getenv('GITHUB_TOKEN')}"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Github API error: {response.status_code}")
    
    contents = response.json()

    if not isinstance(contents, list):
        return [contents]

    all_contents = []
    for item in contents:
        if item['type'] == 'dir':
            subdir_contents = get_github_contents(repo_url, item['path'])
            all_contents.extend(subdir_contents)
        else:
            all_contents.append(item)
    return all_contents

def process_file_contents(file_info):
    if file_info['type'] != 'file':
        return None
    
    valid_extentions = ['.md']
    
    if not any(file_info['name'].endswith(ext) for ext in valid_extentions):
        return None
    
    response = requests.get(file_info['download_url'])

    if response.status_code != 200:
        raise Exception(f"Error fetching file content: {response.status_code}")
    
    content = response.text
    truncated_content = content[:8000].strip()
    if not truncated_content:
        return None
    
    embedding_response = openai.Embedding.create(
        input=truncated_content,
        model="text-embedding-ada-002"
    )

    embedding = embedding_response['data'][0]['embedding']

    if len(embedding) != 1536:
        raise ValueError(f"Unexpected embedding dimension: {len(embedding)}")
    
    return {
        'file_name': file_info['name'],
        'content': truncated_content,
        'download_url': file_info['download_url'],
        'embedding': embedding
    }

def vectorize_repo(index):
    print("\nEnter repository in format 'owner/repo':")
    repo_url = input("> ")

    if not repo_url or '/' not in repo_url:
        print("Invalid repo format.")
        return
    try:
        print("Fetching repo contents...")
        contents = get_github_contents(repo_url)

        print("Processing files...")
        vectorized_files = []

        for file_info in contents:
            try:
                result = process_file_contents(file_info)
                if result:
                    vectorized_files.append(result)
                    print(f"Processed: {file_info['name']}")
            except Exception as e:
                print(f"Error processing file {file_info['name']} : {str(e)}")
        if not vectorized_files:
            print("No valid files to process")
        

        print("Upserting vectors to Pinecone...")
        vectors_to_upsert = []
        for file in vectorized_files:
            vector_id = f"{repo_url}/{file['file_name']}"
            vectors_to_upsert.append({
                'id': vector_id,
                'values': file['embedding'],
                'metadata': {
                    'file_name': file['file_name'],
                    'repo_url': repo_url,
                    'download_url': file['download_url'],
                    'content': file['content']
                }
            })
        
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i: i + batch_size]
            index.upsert(vectors=batch, namespace=repo_url)
            print(f"Upserting batch {int(i / batch_size + 1)}/{(len(vectors_to_upsert) + batch_size - 1) // batch_size}")
        print(f"\nSuccessfully processed {len(vectorized_files)} files.")
    except Exception as e:
        print(f"Error: {str(e)}")

def chat_with_repo(index):
    print("Chatting...")


print("Initializing...")
while True:
    print("\n=== Github Repository Chat ===")
    print("1. Vectorize a Repository")
    print("2. Chat with a Repository")
    print("3. Quit")

    choice = input("\nEnter your choice (1-3): ")

    if choice == '1':
        vectorize_repo(index)
    elif choice == '2':
        chat_with_repo(index)
    elif choice == '3':
        print("Goodbye!")
        break
    else:
        print("Invalid choice, please choose again.")