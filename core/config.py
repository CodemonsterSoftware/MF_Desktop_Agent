import os
import json

def get_appdata_dir():
    appdata = os.environ.get('APPDATA')
    if not appdata:
        appdata = os.path.expanduser('~')
    
    config_dir = os.path.join(appdata, 'ModelFoundry')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir

CONFIG_FILE = os.path.join(get_appdata_dir(), 'agent_config.json')

class ConfigManager:
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.api_key = ""
        self.watch_directories = [
            os.path.join(os.path.expanduser('~'), 'Downloads')
        ]
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.server_url = data.get('server_url', self.server_url)
                    self.api_key = data.get('api_key', self.api_key)
                    self.watch_directories = data.get('watch_directories', self.watch_directories)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        data = {
            'server_url': self.server_url,
            'api_key': self.api_key,
            'watch_directories': self.watch_directories
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
