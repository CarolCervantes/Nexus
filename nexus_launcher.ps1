# NEXUS: Personal Life Agent - Desktop Launcher Script
$ErrorActionPreference = "SilentlyContinue"

# 1. Verificar y levantar Ollama si no está corriendo
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/" -Method Get -TimeoutSec 2
} catch {
    $ollamaCheck = $null
}

if (-not $ollamaCheck) {
    $ollamaExe = "C:\Users\HP\AppData\Local\Programs\Ollama\ollama.exe"
    if (Test-Path $ollamaExe) {
        Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    }
}

# 2. Verificar y levantar el Servidor FastAPI NEXUS (Frontend PWA + Backend API)
try {
    $nexusCheck = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 2
} catch {
    $nexusCheck = $null
}

if (-not $nexusCheck) {
    $pythonExe = "C:\Users\HP\Downloads\nexus\backend\venv\Scripts\python.exe"
    $backendDir = "C:\Users\HP\Downloads\nexus\backend"
    $env:PYTHONPATH = $backendDir
    Start-Process -FilePath $pythonExe -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $backendDir -WindowStyle Hidden
    
    # Esperar hasta que el backend esté listo
    $attempts = 0
    while ($attempts -lt 15) {
        Start-Sleep -Milliseconds 600
        try {
            $check = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 1
            if ($check.status -eq "healthy") {
                break
            }
        } catch {}
        $attempts++
    }
}

# 3. Abrir la interfaz PWA como Aplicación de Escritorio Nativa (Edge o Chrome)
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$edgePath64 = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$chromePathUser = "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"

$url = "http://localhost:8000"

if (Test-Path $edgePath) {
    Start-Process -FilePath $edgePath -ArgumentList "--app=$url", "--profile-directory=Default"
} elseif (Test-Path $edgePath64) {
    Start-Process -FilePath $edgePath64 -ArgumentList "--app=$url", "--profile-directory=Default"
} elseif (Test-Path $chromePath) {
    Start-Process -FilePath $chromePath -ArgumentList "--app=$url"
} elseif (Test-Path $chromePathUser) {
    Start-Process -FilePath $chromePathUser -ArgumentList "--app=$url"
} else {
    Start-Process $url
}
