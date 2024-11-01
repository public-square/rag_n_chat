# Setup Process
The repository does not contain the execution environment.

1. Install python 3.12 at the system level.
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.12 python3.12-venv
```

2. Install poetry for this version of python.
```
python3.12 -m pip install poetry
python3.12 -m poetry config virtualenvs.in-project true
python3.12 -m poetry config virtualenvs.create true
```

3. Install the project environment
Observe errors, if any, but don't worry about them yet.
This will create the local execution environment.
```
python3.12 -m poetry install
```

4. Set up poetry for this project
```
./.venv/bin/python -m pip install poetry
./.venv/bin/python -m poetry config virtualenvs.in-project true
./.venv/bin/python -m poetry config virtualenvs.create true
```

5. Install the dependencies using the local instance of poetry.
( This should succeed. )
```
./.venv/bin/python -m poetry install
```

6. Run unit tests
```
./.venv/bin/python manage.py test
```

7. Launch a local server
```
./.venv/bin/python manage.py runserver 8001 &
```

8. Make test requests against the api

The ping target responds with proof of life.
```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/ping/ -d '{"ping": "123 456 789"}'
```

Repositories may be specified with or without a branch, and the leading `/` is optional.
If the branch is not specified, `main` is assumed.
```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/vectorize/ -d '{"repository": "public-square/rag_n_chat/django"}'
```

```
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/vectorize/ -d '{"repository": "/public-square/rag_n_chat"}'
}'
```


9. Open the admin console
```
Credentials: admin 123123

http://127.0.0.1:8001/admin/
```



# Addenda

## Manual addition of dependencies to poetry
When adding requirements with poetry, be sure to keep them local.
```
./.venv/bin/python -m poetry add <dependency>

```

If you have a requirements.txt file, this will add them to poetry:
```
cat requirements.txt | xargs -I % sh -c './.venv/bin/python -m poetry add "%"'
```

## Common failures
If pip becomes corrupted, install latest version manually.

### Local pip
```
curl -sS https://bootstrap.pypa.io/get-pip.py | ./.venv/bin/python
```

### System pip
```
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
```


