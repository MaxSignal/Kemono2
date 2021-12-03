# Kemono project

## Table of contents
- [Setup](#setup)
- [Develop](#develop)
- [Frequently Asked Questions](#frequently-asked-questions)

## Setup
1. Clone repo and switch to the repo folder:
    ```sh
    git clone --recurse-submodules https://github.com/OpenYiff/Kemono2.git kemono-2
    cd kemono-2
    ```

2. Set up configs:
    ```sh
    cp .env.example .env # open .env and configure missing values
    ```

## Develop
For now Docker is a primary way of working on the repo.

### Installation
1. Create a virtual environment:
    ```sh
    pip install virtualenv # install the package if it's not installed
    virtualenv --upgrade-embed-wheels # makes it easier to manage python versions
    virtualenv --python 3.8 venv
    ```

2. Activate the virtual environment:
    ```sh
    source venv/bin/activate # venv\Scripts\activate on Windows
    ```

3. Install python packages:
    ```sh
    pip install --requirement requirements.txt
    ```

4. Install `pre-commit` hooks:
    ```sh
    pre-commit install --install-hooks
    ````

### IDE-specific

#### VSCode
Copy `.code-workspace` file:
```sh
cp configs/workspace.code-workspace.example kemono-2.code-workspace
```
And install recommended extensions.

### Docker
```sh
docker-compose --env-file .env.dev build
docker-compose --env-file .env.dev up
```
Open `http://localhost:5000/` in the browser.

#### Database
1. Register an account.
2. Visit `http://localhost:5000/development`.
3. Click either seeded or random generation.
4. This will start a mock import process, which will also populate the database.

#### Files
TBD

#### Build
```sh
docker-compose --env-file .env.prod build
docker-compose --env-file .env.prod up --detach
```

Open `http://localhost:8000/` in the browser.

### Manual
TODO: write installation and setup instructions

This assumes you have Python 3.8+ Node 12+ installed and a running PostgreSQL server.
```sh
# make sure your database is initialized
# cd to kemono directory
pip install virtualenv
virtualenv venv
source venv/bin/activate # venv\Scripts\activate on Windows
pip install --requirement requirements.txt
cd client && npm install && npm run build && cd ..
cp .env.example .env # open .env and configure
cp flask.cfg.example flask.cfg # open flask.cfg and configure
set FLASK_APP=server.py
set FLASK_ENV=development
flask run
```

## Frequently Asked Questions

### __My dump doesn't migrate.__
Assuming the running setup:

1. Enter into database container:
    ```sh
    docker exec --interactive --tty kemono-db psql --username=nano kemonodb
    ```
2. Check the contents of the `posts` table:
    ```sql
    SELECT * FROM posts;
    ```
    Most likely it has 0 rows.
3. Move contents of `booru_posts` to `posts`:
    ```sql
    INSERT INTO posts SELECT * FROM booru_posts ON CONFLICT DO NOTHING;
    ```
4. Restart the archiver:
    ```sh
    docker restart kemono-archiver
    ```
    If you see a bunch of log entries from `kemono-db`, then it means archiver is doing the job.
5. In case the frontend still doesn't show the artists/posts, clear redis cache:
    ```sh
    docker exec kemono-redis redis-cli FLUSHALL
    ```
### __How do I git modules?__
Assuming you haven't cloned the repo recursively for whatever reason:
1. Initiate the submodules
    ```sh
    git submodule init
    git submodule update --init --recursive
    ```
2. Switch to archiver folder and add your fork to the remotes list:
    ```sh
    cd archiver
    git remote add <remote_name> <your_fork_link>
    ```
3. Now you can interact with Kitsune repo the same way you do as if it was outside of project folder.

### __How do I import from db dump?__
1. Retrieve a database dump.
2. Run this command in the folder of said dump:
    ```sh
    cat db-filename.dump | gunzip | docker exec --interactive kemono-db psql --username=nano kemonodb
    ```
3. Restart the archiver to trigger migrations:
    ```sh
    docker restart kemono-archiver
    ```
    If that didn't start the migrations, refer to [FAQ section](#my-dump-doesnt-migrate) for manual instructions.

### __How do I put files into nginx container?__
1. Retrieve the files in required folder structure.
2. Copy them into nginx image:
    ```sh
    docker cp ./ kemono-nginx:/storage
    ```
3. Add required permissions to that folder:
    ```sh
    docker exec kemono-nginx chown --recursive nginx /storage
    ```
