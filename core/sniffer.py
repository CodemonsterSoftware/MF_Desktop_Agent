import time
import os
import re
import requests
from PyQt6.QtCore import QObject, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SlicerOutputHandler(FileSystemEventHandler):
    def __init__(self, thread):
        super().__init__()
        self.thread = thread

    def on_created(self, event):
        if event.is_directory:
            return
            
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Wait a bit to ensure the file is completely written
        time.sleep(2)
        
        if filepath.lower().endswith('.gcode'):
            data = self.thread.parse_gcode(filepath)
            self.thread.send_to_api(data)
        elif filepath.lower().endswith('.3mf'):
            self.thread.send_to_api({
                'filename': filename,
                'print_time_seconds': None,
                'filament_weight_g': None,
                'filament_type': None
            })

class SnifferThread(QObject):
    file_processed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.observer = None

    def parse_gcode(self, filepath):
        metadata = {
            'filename': os.path.basename(filepath),
            'print_time_seconds': None,
            'filament_weight_g': None,
            'filament_type': None
        }
        
        try:
            with open(filepath, 'rb') as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(max(size - 4096, 0))
                tail = f.read().decode('utf-8', errors='ignore')
                
                weight_match = re.search(r'; filament used \[g\] = ([\d.]+)', tail)
                if weight_match:
                    metadata['filament_weight_g'] = float(weight_match.group(1))
                
                time_match = re.search(r'; estimated printing time.*?= (.*)', tail)
                if time_match:
                    time_str = time_match.group(1).strip()
                    seconds = 0
                    h_match = re.search(r'(\d+)h', time_str)
                    m_match = re.search(r'(\d+)m', time_str)
                    s_match = re.search(r'(\d+)s', time_str)
                    if h_match: seconds += int(h_match.group(1)) * 3600
                    if m_match: seconds += int(m_match.group(1)) * 60
                    if s_match: seconds += int(s_match.group(1))
                    metadata['print_time_seconds'] = seconds
                    
                type_match = re.search(r'; filament_type = (.*)', tail)
                if type_match:
                    metadata['filament_type'] = type_match.group(1).strip()
        except Exception as e:
            self.error_occurred.emit(f"Error parsing GCODE: {e}")
            
        return metadata

    def send_to_api(self, data):
        if not data['filename']:
            return
            
        url = self.config.server_url.rstrip('/') + '/api/slicer/sync/'
        headers = {}
        if self.config.api_key:
            headers['X-API-Key'] = self.config.api_key
            
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            if response.status_code == 200:
                self.file_processed.emit(f"Successfully uploaded {data['filename']}")
            else:
                try:
                    err_msg = response.json().get('message', 'Unknown error')
                except:
                    err_msg = response.text
                self.error_occurred.emit(f"Server error: {err_msg}")
        except Exception as e:
            self.error_occurred.emit(f"Failed to connect to server: {e}")

    def start(self):
        if self.observer:
            self.stop()
            
        self.observer = Observer()
        handler = SlicerOutputHandler(self)
        
        has_paths = False
        for path in self.config.watch_directories:
            if os.path.exists(path):
                self.observer.schedule(handler, path, recursive=False)
                has_paths = True
                
        if has_paths:
            self.observer.start()
        else:
            self.error_occurred.emit("No valid watch directories found.")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
