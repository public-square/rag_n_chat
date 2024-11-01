# Setup Process
The repository does not contain the execution environment.

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

## 6. Unit Tests
```
./.venv/bin/python manage.py test
```

## 7. Server Launch
```
./.venv/bin/python manage.py runserver 8001 &
```

## 8. Test API Requests

### 8.1 Ping
The ping target responds with proof of life.
```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/ping/ -d '{"ping": "123 456 789"}'
```

### RAG Repositories
Repositories may be specified with or without a branch, and the leading `/` is optional.
If the branch is not specified, `main` is assumed.
```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/vectorize/ -d '{"repository": "public-square/rag_n_chat/django"}'
```

```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/vectorize/ -d '{"repository": "/public-square/rag_n_chat"}'
```


## 9. Admin Console
Django provides administrative capabilities. A default admin user and password are supplied with the repository.
```
Credentials: admin 123123

http://127.0.0.1:8001/admin/
```



# Addenda

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
