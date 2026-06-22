python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Host "Environment is ready. Activate with .\\.venv\\Scripts\\Activate.ps1"
