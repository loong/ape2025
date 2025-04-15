import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_modified = {}
        
    def on_created(self, event):
        if not event.is_directory and self._is_image_file(event.src_path):
            self.callback(event.src_path)
            
    def on_modified(self, event):
        if not event.is_directory and self._is_image_file(event.src_path):
            current_time = time.time()
            if event.src_path in self.last_modified:
                # Ensure we don't process the same file multiple times
                if current_time - self.last_modified[event.src_path] > 0.5:
                    self.callback(event.src_path)
            else:
                self.callback(event.src_path)
            self.last_modified[event.src_path] = current_time
            
    def _is_image_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

def monitor_directory(directory_path, callback):
    event_handler = ImageHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, directory_path, recursive=True)
    observer.start()
    return observer 