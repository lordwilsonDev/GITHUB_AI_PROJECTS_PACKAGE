import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

class RADE(FileSystemEventHandler):
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith(".py"):
            print(f"[RADE] File change detected | path={event.src_path}")
            with open(event.src_path, "rb") as f:
                code = f.read()

            tree = self.parser.parse(code)
            print(f"[RADE] AST parsed successfully | path={event.src_path}")

def start_rade():
    print("Starting RADE background watcher…")
    handler = RADE()
    observer = Observer()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    start_rade()
