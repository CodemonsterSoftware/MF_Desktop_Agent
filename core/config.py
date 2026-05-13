import os
import json
import sys
import winreg

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
        self.run_on_startup = False
        
        default_dirs = []
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            bambu_cache = os.path.join(appdata, 'BambuStudio', 'cache')
            orca_cache = os.path.join(appdata, 'OrcaSlicer', 'cache')
            if os.path.exists(bambu_cache):
                default_dirs.append(bambu_cache)
            if os.path.exists(orca_cache):
                default_dirs.append(orca_cache)
                
        self.watch_directories = default_dirs
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.server_url = data.get('server_url', self.server_url)
                    self.api_key = data.get('api_key', self.api_key)
                    self.run_on_startup = data.get('run_on_startup', self.run_on_startup)
                    self.watch_directories = data.get('watch_directories', self.watch_directories)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        data = {
            'server_url': self.server_url,
            'api_key': self.api_key,
            'run_on_startup': self.run_on_startup,
            'watch_directories': self.watch_directories
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def toggle_startup_registry(self, enable):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "ModelFoundryAgent"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                if getattr(sys, 'frozen', False):
                    # Running as compiled pyinstaller executable
                    app_path = f'"{sys.executable}"'
                else:
                    # Running as python script
                    main_script = os.path.abspath(sys.argv[0])
                    app_path = f'"{sys.executable}" "{main_script}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to toggle startup registry: {e}")

