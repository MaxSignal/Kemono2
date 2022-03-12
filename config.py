import multiprocessing
import getpass
import random
import string
import json
import os


class Configuration:
    def __init__(self):
        config_file = os.environ.get('KEMONO_CONFIG') or 'config.json'
        config_location = os.path.join('./', config_file)
        config = {}

        if os.path.exists(config_location):
            with open(config_location) as f:
                config = json.loads(f.read())

        # Load in configuration...
        self.site = config.get('site', 'http://localhost:6942')
        self.development_mode = config.get('development_mode', True)
        self.download_directory = config.get('download_directory', './development/data')

        self.webserver = config.get('webserver', {})
        self.webserver['enabled'] = self.webserver.get('enabled', True)
        self.webserver['secret_key'] = self.webserver.get('secret_key', ''.join(random.choice(string.ascii_letters) for _ in range(32)))
        self.webserver['workers'] = self.archiver.get('workers', multiprocessing.cpu_count())
        self.webserver['port'] = self.archiver.get('port', 6942)

        self.archiver = config.get('archiver', {})
        self.archiver['enabled'] = self.archiver.get('enabled', True)
        self.archiver['proxies'] = self.archiver.get('proxies', [])
        self.archiver['ban_prefix'] = self.archiver.get('ban_prefix', None)
        self.archiver['public_key'] = self.archiver.get('public_key', None)
        self.archiver['salt'] = self.archiver.get('salt', None)
        self.archiver['queue_limit'] = self.archiver.get('queue_limit', 200)

        self.database = config.get('database', {})
        self.database['host'] = self.database.get('host', '127.0.0.1')
        self.database['port'] = self.database.get('port', 5432)
        self.database['password'] = self.database.get('password', '')
        self.database['database'] = self.database.get('database', 'postgres')
        try:
            self.database['user'] = self.database.get('user', getpass.getuser())
        except:
            self.database['user'] = self.database.get('user', 'shinonome')

        self.redis = config.get('redis', {})
        self.redis['node_options'] = self.redis.get('defaults', {
            "host": "127.0.0.1",
            "port": 6379,
            "database": 0
        })
        self.redis['nodes'] = self.redis.get('nodes', [
            {"db": 0}
        ])
        self.redis['keyspaces'] = self.redis.get('keyspaces', {
            "account": 0,
            "saved_key_import_ids": 0,
            "saved_keys": 0,
            "top_artists": 0,
            "artists_faved": 0,
            "artists_faved_count": 0,
            "top_artists_recently": 0,
            "artists_recently_faved_count": 0,
            "random_artist_keys": 0,
            "non_discord_artist_keys": 0,
            "non_discord_artists": 0,
            "artists_by_service": 0,
            "artist": 0,
            "artist_post_count": 0,
            "artist_last_updated": 0,
            "artists_by_update_time": 0,
            "unapproved_dms": 0,
            "dms": 0,
            "all_dms": 0,
            "all_dms_count": 0,
            "all_dms_by_query": 0,
            "all_dms_by_query_count": 0,
            "dms_count": 0,
            "favorite_artists": 0,
            "favorite_posts": 0,
            "artist_favorited": 0,
            "post_favorited": 0,
            "posts_by_favorited_artists": 0,
            "notifications_for_account": 0,
            "random_post_keys": 0,
            "all_post_keys": 0,
            "post": 0,
            "comments": 0,
            "posts_by_artist": 0,
            "artist_posts_offset": 0,
            "is_post_flagged": 0,
            "next_post": 0,
            "previous_post": 0,
            "importer_logs": 0,
            "ratelimit": 0,
            "all_posts": 0,
            "all_posts_for_query": 0,
            "global_post_count": 0,
            "global_post_count_for_query": 0,
            "lock": 0,
            "lock-signal": 0,
            "imports": 0,
            "running_imports": 0
        })

        # Create our data directory.
        os.makedirs(self.download_directory, exist_ok=True)
