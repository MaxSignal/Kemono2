
# Develop

For now Docker is a primary way of working on the repo. Python3.8 and Docker is required.

<br>

## Installation

<br>

1.  Create a virtual environment.
    
    ```sh
    #   Install the package if it's not installed
    python3.8 -m pip install virtualenv
    
    #   Make it easier to manage python versions
    python3.8 -m virtualenv --upgrade-embed-wheels
    python3.8 -m virtualenv --python 3.8 venv
    ```
    
    <br>

2.  Activate the virtual environment.
    
    ```sh
    #   Windows ➞ venv\Scripts\activate
    source venv/bin/activate
    ```
    
    <br>

3.  Install python packages.

    ```sh
    pip install -r requirements.txt
    ```
    
    <br>

4.  Install  `pre-commit`  hooks.

    ```sh
    pre-commit install --install-hooks
    ````

    <br>

5. Initialize git submodules

    ```
    git submodule update --init --recursive
    ```
<br>
<br>

## IDE

*IDE specific instructions.*

<br>

### VSCode

<br>

1.  Copy  `.code-workspace`  file.

    ```sh
    cp                                              \
        configs/workspace.code-workspace.example    \
        kemono-2.code-workspace
    ```
    
    <br>
    
2.  Install the recommended extensions.

<br>
<br>

## Docker
This assumes you have the git submodules already initialized.
<br>

```sh
# Copy configuration files
cp config.example.json config.json
cp redis_map.py.example redis_map.py

# Change directory
cd docker

# Build and run
docker-compose build && docker-compose up -d
```

<br>

In a browser, visit  [`http://localhost:5000/`]

<br>
<br>

### Database

<br>

> **TODO** : Fix implementation of randomly generated db for development

<br>
<br>

## Manual

<br>

This assumes you have  `Python 3.8+`  &  `Node 16+`  installed <br>
as well as a running **PostgreSQL** server with **Pgroonga**.

<br>

```sh
#   Make sure your database is initialized
#   cd to kemono directory

pip install virtualenv
virtualenv venv

#   Windows ➞ venv\Scripts\activate 
source venv/bin/activate

pip install -r requirements.txt

cp config.json.example config.json

python daemon.py
```

<br>


<!----------------------------------------------------------------------------->

[`http://localhost:5000/development`]: http://localhost:5000/development
[`http://localhost:5000/`]: http://localhost:5000/
[`http://localhost:8000/`]: http://localhost:8000/