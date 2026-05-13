import sys
import os
import requests
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from core.config import ConfigManager
from core.sniffer import SnifferThread
from gui.settings_dialog import SettingsDialog
from gui.tray import AgentTray

class AgentApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        self.setQuitOnLastWindowClosed(False)
        
        self.config = ConfigManager()
        self.sniffer = None
        
        # Determine icon path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_dir, 'assets', 'logo', 'logo_small.png')
                
        # Check initial connectivity
        if not self.check_connection():
            # Force settings if connection fails on startup
            dialog = SettingsDialog(self.config)
            dialog.exec()
            
        self.start_sniffer()
        
        self.tray = AgentTray(self, self.config, self.sniffer, SettingsDialog, self.icon_path)

    def check_connection(self):
        url = self.config.server_url.rstrip('/') + '/api/slicer/sync/'
        headers = {}
        if self.config.api_key:
            headers['X-API-Key'] = self.config.api_key
        try:
            resp = requests.post(url, json={'test': True}, headers=headers, timeout=2)
            # 400 or 200 or 405 means we hit the server but payload was bad/unsupported method. 
            # 401 means auth failed.
            if resp.status_code == 401:
                return False
            return True
        except:
            return False

    def start_sniffer(self):
        if self.sniffer:
            self.sniffer.stop()
            self.sniffer.wait()
            
        self.sniffer = SnifferThread(self.config)
        self.sniffer.start()
        
        if hasattr(self, 'tray'):
            # Update tray signals
            self.sniffer.file_processed.connect(self.tray.on_file_processed)
            self.sniffer.error_occurred.connect(self.tray.on_error)

    def restart_sniffer(self):
        self.start_sniffer()

if __name__ == '__main__':
    app = AgentApplication(sys.argv)
    sys.exit(app.exec())
