import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QListWidget, QFileDialog, 
                             QMessageBox)
import requests

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Model Foundry Agent Settings")
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Server URL
        layout.addWidget(QLabel("Server URL:"))
        self.url_input = QLineEdit(self.config.server_url)
        layout.addWidget(self.url_input)
        
        # API Key
        layout.addWidget(QLabel("API Key (Optional):"))
        self.api_key_input = QLineEdit(self.config.api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        layout.addWidget(self.api_key_input)
        
        # Test Connection Button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_btn)
        
        # Watch Directories
        layout.addWidget(QLabel("Watch Directories (Slicer Output Folders):"))
        self.dir_list = QListWidget()
        for d in self.config.watch_directories:
            self.dir_list.addItem(d)
        layout.addWidget(self.dir_list)
        
        dir_btn_layout = QHBoxLayout()
        self.add_dir_btn = QPushButton("Add Folder")
        self.add_dir_btn.clicked.connect(self.add_directory)
        self.remove_dir_btn = QPushButton("Remove Selected")
        self.remove_dir_btn.clicked.connect(self.remove_directory)
        dir_btn_layout.addWidget(self.add_dir_btn)
        dir_btn_layout.addWidget(self.remove_dir_btn)
        layout.addLayout(dir_btn_layout)
        
        # Save / Cancel
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save && Restart")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def test_connection(self):
        url = self.url_input.text().strip().rstrip('/') + '/api/slicer/sync/'
        api_key = self.api_key_input.text().strip()
        
        headers = {}
        if api_key:
            headers['X-API-Key'] = api_key
            
        try:
            # We send a dummy payload just to see if we get a 400 (Bad Request / Missing Filename)
            # or a 401 (Unauthorized). If we get a 400, auth succeeded.
            resp = requests.post(url, json={'test': True}, headers=headers, timeout=5)
            if resp.status_code in [200, 400]:
                QMessageBox.information(self, "Success", "Successfully connected to Model Foundry!")
            elif resp.status_code == 401:
                QMessageBox.warning(self, "Error", "Connection failed: Unauthorized. Check API Key.")
            else:
                QMessageBox.warning(self, "Error", f"Connection failed: Status {resp.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {e}")

    def add_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Slicer Output Folder")
        if dir_path:
            # Check if already added
            items = [self.dir_list.item(i).text() for i in range(self.dir_list.count())]
            if dir_path not in items:
                self.dir_list.addItem(dir_path)

    def remove_directory(self):
        for item in self.dir_list.selectedItems():
            self.dir_list.takeItem(self.dir_list.row(item))

    def save_settings(self):
        self.config.server_url = self.url_input.text().strip()
        self.config.api_key = self.api_key_input.text().strip()
        
        self.config.watch_directories = [self.dir_list.item(i).text() for i in range(self.dir_list.count())]
        
        self.config.save()
        self.accept()
