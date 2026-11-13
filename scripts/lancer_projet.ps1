# Script de lancement de l'écosystème complet (API Python, Service Java, Interface Streamlit)
param(
    [switch]$SansStreamlit
)
$ErrorActionPreference = "Continue"

$env:PATH = "C:\Users\hessa\AppData\Local\Programs\Python\Python312;C:\Program Files\Java\jdk-27\bin;$env:PATH"
$env:JAVA_HOME = "C:\Program Files\Java\jdk-27"
$env:API_KEYS = "e2e-cle-client-tp-spring:client,e2e-cle-admin-tp-spring1:admin"
$env:SENTIMENT_API_KEY = "e2e-cle-client-tp-spring"
$env:SENTIMENT_API_URL = "http://127.0.0.1:8000"

$Racine = Split-Path -Parent $PSScriptRoot
Set-Location $Racine

# Arrêt préventif des processus sur les ports 8000, 8081, 8501
$ports = @(8000, 8081, 8501)
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids) {
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "== Démarrage de l'API Python FastAPI (Port 8000)..."
$apiProcess = Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000") -PassThru -NoNewWindow

Write-Host "== Démarrage du Service Java Spring Boot (Port 8081)..."
$jar = (Get-ChildItem (Join-Path $Racine "java\avis-service\target\avis-service-*.jar") | Select-Object -First 1).FullName
$javaProcess = Start-Process -FilePath "java" -ArgumentList @("-jar", "`"$jar`"", "--server.port=8081", "--sentiment.api.url=http://127.0.0.1:8000", "--sentiment.api.key=e2e-cle-client-tp-spring") -PassThru -NoNewWindow

if (-not $SansStreamlit) {
    Write-Host "== Démarrage de l'Interface Web Streamlit (Port 8501)..."
    $streamlitProcess = Start-Process -FilePath "python" -ArgumentList @("-m", "streamlit", "run", "ui/app.py", "--server.port", "8501", "--server.headless", "true") -PassThru -NoNewWindow
}

Write-Host "`nAttente de disponibilité des services..."
Start-Sleep -Seconds 6

$http = New-Object System.Net.Http.HttpClient
$http.Timeout = [TimeSpan]::FromSeconds(5)

try {
    $rApi = $http.GetAsync("http://127.0.0.1:8000/v1/health").GetAwaiter().GetResult()
    Write-Host "  [OK] API Python FastAPI : http://127.0.0.1:8000 (Documentation : http://127.0.0.1:8000/docs)"
} catch {
    Write-Host "  [!] L'API Python démarre encore... (http://127.0.0.1:8000)"
}

try {
    $rJava = $http.GetAsync("http://127.0.0.1:8081/avis/sante").GetAwaiter().GetResult()
    Write-Host "  [OK] Service Java Spring Boot : http://127.0.0.1:8081 (Santé : http://127.0.0.1:8081/avis/sante)"
} catch {
    Write-Host "  [!] Le service Java démarre encore... (http://127.0.0.1:8081)"
}

if (-not $SansStreamlit) {
    Write-Host "  [OK] Interface Utilisateur Streamlit : http://localhost:8501"
}

Write-Host "`nTous les services sont démarrés !"

