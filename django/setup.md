# Setup Process
This process requires python 3.12 with poetry. Installation on Ubuntu systems
is detailed in the addenda below.

Note that these steps should be executed in the `django` directory. Once the
project is finalized, that will change.

## 1. Local Virtual Execution Environment
Configure poetry to install a local virtual environment and launch a poetry
shell to instantiate it.
```bash
python3.12 -m poetry config virtualenvs.in-project true
python3.12 -m poetry config virtualenvs.create true
echo exit | python3.12 -m poetry shell
./.venv/bin/python -m pip install poetry
./.venv/bin/python -m poetry install
```

## 2. Environment Variables
Create `django/global/.env` with the necessary access keys:
```bash
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=rag-n-chat
EMBEDDING_DIMENSIONS=1536
GITHUB_TOKEN=
TAVILY_API_KEY=
API_SERVER_PORT=8001
DJANGO_SECRET_KEY=change-this-value
```

## 3. Unit Tests
```bash
./.venv/bin/python manage.py test
```

## 4. Server Launch
```bash
./rag-n-chat-ctrl start
./rag-n-chat-ctrl status
cat rag-n-chat-ctrl.log
```

## 5. Test API Requests

### 5.1 Ping
The ping target responds with proof of life.
```bash
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/ping/ \
-d '{"ping": "123 456 789"}'
```

### 5.2 RAG Repositories
Repositories may be specified with or without a branch, and the leading `/`
is optional. If the branch is not specified, `main` is assumed.
```bash
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/repo/vectorize/ \
-d '{"repository": "public-square/rag_n_chat/django"}'
```

```bash
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/repo/vectorize/ \
-d '{"repository": "/public-square/rag_n_chat"}'
```

```bash
curl -X GET -H "Content-Type: application/json" \
http://localhost:8001/api/repo/list/
```

```bash
curl -X DELETE -H "Content-Type: application/json" \
http://localhost:8001/api/repo/delete/ \
-d '{"repository": "public-square/rag_n_chat/main"}'
```

### 5.3 Chat
The chat target hits OpenAI. It operates with or without RAG.

#### 5.3.1 No Context
```bash
curl --silent -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/chat/prompt/ \
-d '{"prompt": "Make me laugh in 50 words or less."}'
```

#### 5.3.2 With Context from a Github Repository
```bash
curl --silent -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/chat/prompt/ \
-d @- << EOF
{ "prompt": "What curl command I should use to hit the ping API target?",
  "repository": "public-square/rag_n_chat/django"   }
EOF
```

## 5. Admin Console
Django provides administrative capabilities. A default admin user and password
are supplied with the repository.
```
Credentials: admin 123123

http://127.0.0.1:8001/admin/
```


# Addenda

## Control Script
A rudimentary control script is supplied, suitable for development use on Linux
systems. The script supports the standard start, stop, and status functions,
and if `lsof` is available, will also find processes listening on the port used
by the system.
```bash
./rag-n-chat-ctrl start|stop|status|listeners
```

```
USAGE:
./rag-n-chat-ctrl
    start      launch the server
    stop       stop a running server
    status     print the current process tree
    listeners  find processes listening on 8001
```

## Manual Dependency Addition
When adding requirements with poetry, be sure to keep them local.
```bash
./.venv/bin/python -m poetry add <dependency>

```

If you have a requirements.txt file, this will add them to poetry:
```bash
cat requirements.txt | xargs -I % sh -c './.venv/bin/python -m poetry add "%"'
```

## Common Failures
If pip becomes corrupted, install latest version manually. The local instance
should be used to manage dependencies and the system instance associated with
the correct version of python is used for initial setup.

### Local Pip
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | ./.venv/bin/python
```

### System Pip
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
```

## Local Execution Environment Rebuild
If the local instance of python or dependencies becomes corrupted, or to
validate that poetry provides a complete execution environment, simply delete
the virtual environment and recreate it.
```bash
rm -rf .venv
python3.12 -m poetry config virtualenvs.in-project true
python3.12 -m poetry config virtualenvs.create true
echo exit | python3.12 -m poetry shell
./.venv/bin/python -m pip install poetry
./.venv/bin/python -m poetry install

```

## Ubuntu System Execution Environment
### System Python
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.12 python3.12-venv
```

## System Poetry
```bash
python3.12 -m pip install poetry
python3.12 -m poetry config virtualenvs.in-project true
python3.12 -m poetry config virtualenvs.create true
```
