# Environment Variables Overhaul

## Table of contents
- [General Description](#general-description)
- [Technical Description](#technical-description)
- [Process](#process)
- [Issues](#issues)

## General Description

### The problem
As for now the configuration for the stack is spread among several files:

- `.env`
- `flask.cfg`
- `config.py`/`kitsune.py`
- `redis_map.py`/`redis_map.py`
- env vars declared in the `docker-compose` configs
- nginx implicitly depends on the names of the docker containers in its config

All of this (and especially duplicated configs between `archiver` and `server`) makes it extremely annoying to deal with updates and ultimately makes it impossible to separate dev and prod environment within one machine. And this separation is required in order to introduce automated tests.

### The Solution
- Shove every environment variable into a single `.env` file at most, one per environment.
- Write a module through which the rest of the code interacts with env variables.
- Split `.env` into `.env.dev` and `env.prod` files. The reason for this is programs generally refer to `.env` file for a reference, which makes the difference between environments more murky.

### Naming convention
The variables within `.env` files follow this pattern:
```
KEMONO_<PROJECT_ROLE>_VARIABLE_NAME
```

All kemono-specific variables are prepended with `KEMONO_`, while project-specific variables also add their role to it. All env vars follow the snake pascal casing. No two different variables referring to the same entity allowed.

Addition and removal of variables by any given PR should be mentioned in the `ENV VARS` section within its commit.

### Env Var Module
Such module consists of 3 submodules:
- `env-vars`

  Only this module is allowed to read env vars, the rest of the code imports values from it.
  The variables there are separated into 2 categories: optional and critical. If the value is not set, the optional variables will set a default value, while critical ones will crash the runtime.
  No value transformation is allowed, therefore all exported values are strings.

- `derived-vars`

  This module imports the values from `env-vars` and exports the results of the transformations applied to them.

- `constants`

  Not strictly env vars, but follows the same style and also allows exporting immutable collections. This module is for various variables which are known ahead of the application launch but also don't depend on the environment.

The variables exported from these modules follow the snake pascal casing, with `KEMONO_` omitted. The role prefix can be ommitted too in case the role is the same as project's role.

## Technical Description

### All variables
- FLASK_ENV
- PGHOST
- PGUSER
- PGPASSWORD
- PGDATABASE
- TELEGRAMTOKEN
- TELEGRAMCHANNEL
- KEMONO_SITE
- REQUESTS_IMAGES
- CACHE_TYPE
- CACHE_DEFAULT_TIMEOUT
- ENABLE_PASSWORD_VALIDATOR
- ENABLE_LOGIN_RATE_LIMITING
- SECRET_KEY
- download_path
- database_host
- database_dbname
- database_user
- database_password
- redis_host
- redis_port
- redis_password
- proxies
- ban_url
- pubkey
- salt
- pubsub
- pubsub_queue_limit
- nodes
- node_options
- keyspaces
- ARCHIVERHOST
- ARCHIVERPORT

### Server
- `.env`
- `flask.cfg`

  Look up how to refer to it from `.env` file.

- `config.py`/`kitsune.py`
- `redis_map.py`/`redis_map.py`

### Client
  No files for env vars currently, but should be introduced if only to be able to build outside of docker stack.

### Archiver
- `config.py`
- `redis_map.py`

### Docker
- `docker-compose.dev.yml`
- `docker-compose.yml`

  These can read from `env` file too.

### Nginx
- `nginx.conf`
