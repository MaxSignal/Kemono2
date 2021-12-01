from configs.env_vars import ENV_VARS

# Available Redis nodes.
# Passed directly to `Cluster.hosts`.
nodes = {
    0: {'db': 0}
}

# Options that apply to all nodes.
# Passed directly to `Cluster.host_defaults`.
node_options = dict(
    host=ENV_VARS.REDIS_HOST,
    port=ENV_VARS.REDIS_PORT,
    password=ENV_VARS.REDIS_PASSWORD
)
