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

        self.webserver = config.get('archiver', {})
        self.webserver['enabled'] = self.archiver.get('enabled', True)
        self.webserver['secret_key']
        self.webserver['workers'] = self.archiver.get('workers', multiprocessing.cpu_count())
        self.webserver['port'] = self.archiver.get('port', 6942)

        self.database = config.get('database', {})
        self.database['host'] = self.database.get('host', '127.0.0.1')
        self.database['port'] = self.database.get('port', 5432)
        self.database['password'] = self.database.get('password')
        self.database['database'] = self.database.get('database', 'postgres')
        try:
            self.database['user'] = self.database.get('user', getpass.getuser())
        except:
            pass

        self.redis = config.get('redis', {})
        self.redis['host'] = self.redis.get('host', '127.0.0.1')
        self.redis['port'] = self.redis.get('port', 6379)
        self.redis['database'] = self.redis.get('database', 0)

        self.salt = config.get('salt') or ''.join(random.choice(string.ascii_letters) for _ in range(32))

        # self.webserver = config.get('webserver')
        # if self.webserver:
        #     self.webserver['enabled'] = config['webserver'].get('enabled', False)
        #     self.webserver['workers'] = config['webserver'].get('workers', multiprocessing.cpu_count())
        #     self.webserver['port'] = config['webserver'].get('port', 6942)

        # self.database = config.get('database')
        # if self.database:
        #     self.database['user'] = config['database'].get('user', os.getlogin())
        #     self.database['host'] = config['database'].get('host', '127.0.0.1')
        #     self.database['port'] = config['database'].get('port', 5432)
        #     self.database['password'] = config['database'].get('password')
        #     self.database['database'] = config['database'].get('database', 'postgres')

        # self.redis = config.get('redis')
        # if self.redis:
        #     self.redis['host'] = config['redis'].get('host', '127.0.0.1')
        #     self.redis['port'] = config['redis'].get('port', 6379)
        #     self.redis['database'] = config['redis'].get('database', 0)
        # self.salt = config.get('salt') or ''.join(random.choice(string.ascii_letters) for _ in range(32))

        # Create our data directory.
        os.makedirs(self.download_directory, exist_ok=True)
