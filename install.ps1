$ErrorActionPreference = "Stop"

Write-Host "Installing PokeFact..." -ForegroundColor Cyan

# Paths
$InstallDir = "$Env:USERPROFILE\.pokefact"
$BinDir = "$InstallDir\bin"
$RepoUrl = "https://gitlab.com/phoneybadger/pokemon-colorscripts.git"

# 1. Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is missing. Install Git for Windows."
    Exit 1
}

# 2. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is missing. Install Python."
    Exit 1
}

# 3. Clean Install Directory
if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
New-Item -ItemType Directory -Force -Path "$InstallDir\src" | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# 4. Copy Files
Write-Host "Copying files..."
Copy-Item "src\pokefact.py" "$InstallDir\src\pokefact.py"
Copy-Item "requirements.txt" "$InstallDir\requirements.txt"

# 5. Clone Art
Write-Host "Downloading art..."
git clone --depth 1 $RepoUrl "$InstallDir\pokemon-colorscripts" | Out-Null

# 6. Python Venv
Write-Host "Setting up Python..."
python -m venv "$InstallDir\venv"
& "$InstallDir\venv\Scripts\pip" install -q -r "$InstallDir\requirements.txt"

# 7. Create Launcher
Write-Host "Creating launcher..."
$Exe = "$InstallDir\venv\Scripts\python.exe"
$Script = "$InstallDir\src\pokefact.py"
$Content = "@echo off`r`n`"$Exe`" `"$Script`" %*"
Set-Content -Path "$BinDir\pokefact.bat" -Value $Content

# 8. Update Path
$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentPath -notlike "*$BinDir*") {
    Write-Host "Adding to PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$CurrentPath;$BinDir", "User")
}

Write-Host "Done! Please restart your terminal." -ForegroundColor Green