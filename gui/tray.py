from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject
import os
import webbrowser

class AgentTray(QObject):
    def __init__(self, app, config, sniffer, settings_dialog_class, icon_path):
        super().__init__()
        self.app = app
        self.config = config
        self.sniffer = sniffer
        self.settings_dialog_class = settings_dialog_class
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("Model Foundry Slicer Agent")
        
        # Menu
        self.menu = QMenu()
        
        self.status_action = QAction("Status: Monitoring")
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        
        self.settings_action = QAction("Settings...")
        self.settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.settings_action)
        
        self.web_action = QAction("Open Model Foundry")
        self.web_action.triggered.connect(self.open_web)
        self.menu.addAction(self.web_action)
        
        self.log_action = QAction("Open Logs")
        self.log_action.triggered.connect(self.open_logs)
        self.menu.addAction(self.log_action)
        
        self.menu.addSeparator()
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        
        # Connect Sniffer Signals
        self.sniffer.file_processed.connect(self.on_file_processed)
        self.sniffer.error_occurred.connect(self.on_error)

    def show_settings(self):
        dialog = self.settings_dialog_class(self.config)
        if dialog.exec():
            # Restart sniffer if settings saved
            self.sniffer.stop()
            # We can't restart a QThread easily, so the main loop should handle recreation or we just restart app.
            # For simplicity, we ask the app to restart the thread.
            self.app.restart_sniffer()

    def open_web(self):
        webbrowser.open(self.config.server_url)
        
    def open_logs(self):
        if hasattr(self.app, 'log_file') and os.path.exists(self.app.log_file):
            os.startfile(self.app.log_file)

    def on_file_detected(self, msg):
        self.tray_icon.showMessage("Detecting Slice", msg, QSystemTrayIcon.MessageIcon.Information, 3000)

    def on_file_processed(self, msg):
        self.tray_icon.showMessage("Slice Sent", msg, QSystemTrayIcon.MessageIcon.Information, 3000)

    def on_error(self, msg):
        self.tray_icon.showMessage("Agent Error", msg, QSystemTrayIcon.MessageIcon.Warning, 5000)

    def quit_app(self):
        self.sniffer.stop()
        self.app.quit()
