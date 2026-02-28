import sys
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.run_script()

    def run_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, self.script])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}, reloading...")
            self.run_script()

if __name__ == "__main__":
    script = "main.py"  # Change to your main script if needed
    event_handler = ReloadHandler(script)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
