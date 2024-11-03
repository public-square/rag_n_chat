# Setup Process
The repository does not contain the execution environment - the steps below will set one up.

## 1. System Python
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.12 python3.12-venv
```

## 2. System Poetry
```
python3.12 -m pip install poetry
python3.12 -m poetry config virtualenvs.in-project true
python3.12 -m poetry config virtualenvs.create true
```

## 3. Local Virtual Execution Environment
Observe errors, if any, but don't worry about them yet.
This will create the local execution environment.
```
python3.12 -m poetry install
```

## 4. Local Poetry
```
./.venv/bin/python -m pip install poetry
./.venv/bin/python -m poetry config virtualenvs.in-project true
./.venv/bin/python -m poetry config virtualenvs.create true
```

## 5. Local Dependencies via Poetry
( This should succeed. )
```
./.venv/bin/python -m poetry install
```

## 6. Environment Variables
Create `django/global/.env` with the necessary access keys:
```
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=rag-n-chat
EMBEDDING_DIMENSIONS=1536
GITHUB_TOKEN=
TAVILY_API_KEY=
API_SERVER_PORT=8001
DJANGO_SECRET_KEY=change-this-value
```

## 7. Unit Tests
```
./.venv/bin/python manage.py test
```

## 8. Server Launch
```
./.venv/bin/python manage.py runserver 8001 &
```

## 9. Test API Requests

### 9.1 Ping
The ping target responds with proof of life.
```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/ping/ \
-d '{"ping": "123 456 789"}'
```

### 9.2 RAG Repositories
Repositories may be specified with or without a branch, and the leading `/` is optional.
If the branch is not specified, `main` is assumed.
```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/repo/vectorize/ \
-d '{"repository": "public-square/rag_n_chat/django"}'
```

```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/repo/vectorize/ \
-d '{"repository": "/public-square/rag_n_chat"}'
```

```
curl -X GET -H "Content-Type: application/json" \
http://localhost:8001/api/repo/list/
```

```
curl -X DELETE -H "Content-Type: application/json" \
http://localhost:8001/api/repo/delete/ \
-d '{"repository": "public-square/rag_n_chat/main"}'
```

### 9.3 Chat
The chat target hits OpenAI.
```
curl --silent -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/chat/prompt/ \
-d '{"prompt": "Make me laugh in 50 words or less."}'
```

## 10. Admin Console
Django provides administrative capabilities. A default admin user and password are supplied with the repository.
```
Credentials: admin 123123

http://127.0.0.1:8001/admin/
```


# Addenda

## Control Script
A rudimentary control script is supplied, suitable for development use on Linux systems. The script supports the standard start, stop, and status functions, and if `lsof` is available, will also find processes listening on the port used by the system.
```
./rag-n-chat start|stop|status|listeners
```

```
USAGE:
./rag-n-chat
    start      launch the server
    stop       stop a running server
    status     print the current process tree
    listeners  find processes listening on 8001
```

## Manual Dependency Addition
When adding requirements with poetry, be sure to keep them local.
```
./.venv/bin/python -m poetry add <dependency>

```

If you have a requirements.txt file, this will add them to poetry:
```
cat requirements.txt | xargs -I % sh -c './.venv/bin/python -m poetry add "%"'
```

## Common Failures
If pip becomes corrupted, install latest version manually. The local instance should be used to manage dependencies and the system instance associated with the correct version of python is used for initial setup.

### Local Pip
```
curl -sS https://bootstrap.pypa.io/get-pip.py | ./.venv/bin/python
```

### System Pip
```
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
```

## Local Execution Environment Rebuild
If the local instance of python or dependencies becomes corrupted, or to validate that poetry provides a complete execution environment, simply delete the virtual environment and run steps `3`, `4`, and `5` above.
```
rm -rf .venv
```
