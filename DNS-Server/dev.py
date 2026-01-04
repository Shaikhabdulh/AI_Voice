# dev.py
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.restart()
    
    def restart(self):
        if self.process:
            print("\n🔄 Restarting due to changes...")
            self.process.terminate()
            self.process.wait()
        
        print(f"▶️  Starting {self.script_path}...")
        self.process = subprocess.Popen([sys.executable, self.script_path])
    
    def on_modified(self, event):
        # Only restart on .py or .env file changes
        if event.src_path.endswith(('.py', '.env')):
            # Ignore our own file
            if 'dev.py' not in event.src_path:
                print(f"\n📝 Detected change in {event.src_path}")
                self.restart()

if __name__ == "__main__":
    script = "main.py"  # Your main script
    
    handler = RestartHandler(script)
    observer = Observer()
    observer.schedule(handler, path='.', recursive=False)
    observer.start()
    
    print(f"👀 Watching for changes in current directory...")
    print(f"📝 Will auto-restart on .py and .env file changes")
    print(f"⚠️  Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()
        print("\n👋 Stopped watching")
    
    observer.join()
