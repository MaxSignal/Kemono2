# Environment Variables

## Table of contents
- [General Description](#general-description)
<!-- - [Issues](#issues) -->

## General Description

### Naming convention
The environment variable names follow this pattern:
```
KEMONO_<PROJECT_ROLE>_VARIABLE_NAME
```

All kemono-specific variables are prepended with `KEMONO_`, while project-specific variables also add their role to it. All env vars follow the snake pascal casing. No two different variables referring to the same entity allowed.

Addition and removal of variables by any given PR should be mentioned in the `ENV VARS` section within its commit.

### Env Var Module
Such module consists of 3 submodules:
- `env-vars`

  Only this module is allowed to read env vars, the rest of the code imports values from it.
  Some of the variables can be of critical status, which will crash the runtime if they aren't set.
  No value transformation is allowed, therefore all exported values are strings.

- `derived-vars`

  This module imports the values from `env-vars` and exports the results of the transformations applied to them.

- `constants`

  Not strictly env vars, but follows the same style and also allows exporting immutable collections. This module is for various variables which are known ahead of the application launch but also don't depend on the environment.

The variables exported from these modules follow the snake pascal casing, with `KEMONO_` omitted. The role prefix can be ommitted too in case the role is the same as project's role.
