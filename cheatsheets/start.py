import sys
import subprocess
from pathlib import Path

# --- check python ---
print("Python version:", sys.version)
print("Python executable:", sys.executable)

PROJECT_ROOT = Path(__file__).parent
VENV_DIR = PROJECT_ROOT / "venv"

# --- create venv ---
if not VENV_DIR.exists():
    print("Creating venv...")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
else:
    print("venv already exists")

# --- check venv python ---
venv_python = VENV_DIR / "Scripts" / "python.exe"
print("venv python:", venv_python)

# --- create .gitignore ---
gitignore_content = """\
# Python
__pycache__/
*.py[cod]

# Virtual environments
venv/
.venv/
env/

# IDE
.idea/
.vscode/

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""

# --- create main.py ---
main_py = PROJECT_ROOT / "main.py"
if not main_py.exists():
    main_py.write_text(
        'if __name__ == "__main__":\n'
        '    print("Project initialized")\n',
        encoding="utf-8"
    )
    print("main.py created")
else:
    print("main.py already exists")


gitignore_path = PROJECT_ROOT / ".gitignore"
gitignore_path.write_text(gitignore_content, encoding="utf-8")
print(".gitignore created")
print("terminal: venv\Scripts\activate
")
