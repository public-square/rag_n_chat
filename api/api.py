import requests
import openai
import os
EMBEDDING_DIMENSION = 1536

def process_content(file_info):
    valid_extentions = [".md"]
    # print(item['name'])
    if not any(file_info['name'].endswith(ext) for ext in valid_extentions):
        return None
    res = requests.get(file_info['download_url'])
    response = openai.Embedding.create(input=res.text, model="text-embedding-ada-002")
    embedding = response['data'][0]['embedding']
    if len(embedding) != EMBEDDING_DIMENSION:
        print("invalid embedding")
    else:
        return {
            'file_name': file_info['name'],
            'content': res.text,
            'embedding': embedding
        }

headers = {}
headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
res = requests.get("https://api.github.com/repos/decagondev/8.1-crewai/contents", headers=headers)
print(res.status_code)

file_content = []
for item in res.json():
    if item['type'] == "file":
        data = process_content(item)
        if data == None:
            continue
        print(data)


# print(file_content)
# response = openai.Embedding.create(input=file_content[0], model="text-embedding-ada-002")
# embedding = response['data'][0]['embedding']
# if len(embedding) != EMBEDDING_DIMENSION:
#     print("invalid embedding")
# else:
#     print(embedding)
    
