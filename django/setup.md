# install python 3.12 at the system level
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.12 python3.12-venv

# if pip gets corrupted, install latest
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# install poetry for this version of python
python3.12 -m pip install poetry
python3.12 -m poetry config virtualenvs.in-project true 
python3.12 -m poetry config virtualenvs.create true

# install the project environment
# observer errors, if any, but don't worry about them yet
python3.12 -m poetry install

# if pip for this project gets corrupted, install latest
curl -sS https://bootstrap.pypa.io/get-pip.py | ./.venv/bin/python

# set up poetry for this project
./.venv/bin/python -m pip install poetry
./.venv/bin/python -m poetry config virtualenvs.in-project true 
./.venv/bin/python -m poetry config virtualenvs.create true

# install the dependencies using the local instance of poetry
# this should succeed
./.venv/bin/python -m poetry install

# if you have only a requirements.txt file, this will add them to poetry
# cat requirements.txt | xargs -I % sh -c './.venv/bin/python -m poetry add "%"'

# to manually add dependencies to the project locally
# ./.venv/bin/python -m poetry add <dependency>


# run unit tests
./.venv/bin/python manage.py test

# launch the server
./.venv/bin/python manage.py runserver 8001 &

# make a test request against the api
curl -X POST -H "Content-Type: application/json" \
http://localhost:8001/api/ping/ -d '{"ping": "123 456 789"}'

# open the admin console
# admin 123123
http://127.0.0.1:8001/admin/


