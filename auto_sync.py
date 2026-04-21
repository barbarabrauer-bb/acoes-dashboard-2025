"""
Monitora mudancas nos arquivos do projeto e faz commit+push automatico no GitHub.
Uso: python3 auto_sync.py
"""
import subprocess
import time
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_DIR = Path(__file__).parent
IGNORAR = {".git", "__pycache__", ".DS_Store", "auto_sync.py"}

def git(cmd):
    result = subprocess.run(
        ["git"] + cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def sync():
    code, status, _ = git(["status", "--porcelain"])
    if not status:
        return

    git(["add", "."])
    code, _, err = git(["commit", "-m", "auto-sync: atualização automática"])
    if code != 0:
        print(f"Erro no commit: {err}")
        return

    code, out, err = git(["push"])
    if code == 0:
        print(f"[sync] Push realizado com sucesso.")
    else:
        print(f"[sync] Erro no push: {err}")

class Handler(FileSystemEventHandler):
    def __init__(self):
        self._pendente = False
        self._ultimo = 0

    def on_any_event(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if any(part in IGNORAR for part in path.parts):
            return
        self._pendente = True
        self._ultimo = time.time()

    def verificar(self):
        if self._pendente and time.time() - self._ultimo > 3:
            self._pendente = False
            print(f"[sync] Mudança detectada, enviando para o GitHub...")
            sync()

if __name__ == "__main__":
    print(f"[sync] Monitorando {PROJECT_DIR}")
    print("[sync] Pressione Ctrl+C para parar.\n")

    handler = Handler()
    observer = Observer()
    observer.schedule(handler, str(PROJECT_DIR), recursive=True)
    observer.start()

    try:
        while True:
            handler.verificar()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[sync] Encerrado.")
    observer.join()
