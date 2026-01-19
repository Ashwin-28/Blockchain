$ErrorActionPreference = "Stop"

Write-Host "=== Decentralized Biometric Identity (Dev Runner) ==="
Write-Host "This will start: Ganache -> Truffle migrate -> Backend -> Frontend"
Write-Host ""

function Require-Command($name, $hint) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Host "Missing command: $name" -ForegroundColor Red
    if ($hint) { Write-Host $hint }
    exit 1
  }
}

Require-Command "node" "Install Node.js 18+ and restart your terminal."
Require-Command "npm"  "Install Node.js (includes npm) and restart your terminal."

if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
  Write-Host "Missing command: python" -ForegroundColor Red
  Write-Host "Install Python 3.10+ from https://www.python.org/downloads/windows/ and CHECK 'Add python.exe to PATH'."
  exit 1
}

Write-Host "Installing root deps (if needed)..."
npm install

Write-Host "Starting Ganache (background)..."
Start-Process -WindowStyle Normal -FilePath "npm" -ArgumentList "run","ganache"
Start-Sleep -Seconds 3

Write-Host "Compiling + migrating contracts..."
npm run compile
npm run migrate

Write-Host "Installing frontend deps (if needed)..."
Push-Location "frontend"
npm install
Pop-Location

Write-Host "Installing backend deps (venv)..."
Push-Location "backend"
if (-not (Test-Path ".\venv")) {
  python -m venv venv
}
& .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Pop-Location

Write-Host ""
Write-Host "Starting backend + frontend in separate windows..."
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList "-NoExit","-Command","cd backend; .\venv\Scripts\Activate.ps1; python app.py"
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList "-NoExit","-Command","cd frontend; npm start"

Write-Host ""
Write-Host "Done. Frontend: http://localhost:3000  Backend: http://localhost:5000"

