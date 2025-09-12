$ErrorActionPreference = "Stop"
Remove-Item -Recurse -Force dist, build -ErrorAction Ignore
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --name OrthoDictation `
  --add-data "config.json;." `
  windows_client.py
Write-Host "Built dist/OrthoDictation.exe"

