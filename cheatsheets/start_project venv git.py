venv\Scripts\python.exe - -version # check python version
python -m venv venv # add venv
venv\Scripts\activate # activate venv
python -c "import sys; print(sys.executable)" # check venv path

makr .gitignore
@"
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
"@ | Out-File -Encoding utf8 .gitignore
