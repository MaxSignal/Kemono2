from rb import BaseRouter, UnroutableCommand

from .keyspaces import keyspaces


class KemonoRouter(BaseRouter):
    def get_host_for_key(self, key: str):
        top_level_prefix_of_key = key.split(':')[0]
        if (keyspaces.get(top_level_prefix_of_key) is not None):
            return keyspaces[top_level_prefix_of_key]
        else:
            raise UnroutableCommand()
