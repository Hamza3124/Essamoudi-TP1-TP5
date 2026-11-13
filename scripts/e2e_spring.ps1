# Essai de bout en bout du TP Spring Boot (contrôles J6 et J7), version Windows (PowerShell 5.1 ou 7).
# Depuis la racine du dépôt, environnement Python activé :
#   .venv\Scripts\Activate.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1
# Options : -ApiPort 8765 -JavaPort 8091 -Transport httpurlconnection (ou jdk-defaut) pour reproduire un piège (J8).
param(
    [int]$ApiPort = 8000,
    [int]$JavaPort = 8081,
    [ValidateSet("jdk-http11", "httpurlconnection", "jdk-defaut")] [string]$Transport = "jdk-http11"
)
$ErrorActionPreference = "Continue"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

# Auto-détection de Java et Python dans les répertoires standards Windows si absents du PATH
if (-not (Get-Command "java" -ErrorAction SilentlyContinue)) {
    $candidatsJava = @(
        "C:\Program Files\Java\jdk-27\bin",
        "C:\Program Files\Java\latest\bin",
        "C:\Program Files\Java\jdk-21\bin",
        "C:\Program Files\Eclipse Adoptium\jdk-21*\bin"
    )
    foreach ($cand in $candidatsJava) {
        $trouves = Get-ChildItem -Path $cand -ErrorAction SilentlyContinue
        if ($trouves) {
            $javaDir = (Get-Item $cand).FullName
            $env:PATH = "$javaDir;$env:PATH"
            $env:JAVA_HOME = (Split-Path -Parent $javaDir)
            break
        }
    }
}

$pyCmd = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pyCmd -or $pyCmd.Source -match "WindowsApps") {
    $candidatsPy = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312",
        "$env:LOCALAPPDATA\Programs\Python\Python311",
        "C:\Python312",
        "C:\Python311"
    )
    foreach ($cand in $candidatsPy) {
        if (Test-Path "$cand\python.exe") {
            $env:PATH = "$cand;$cand\Scripts;$env:PATH"
            break
        }
    }
}

Add-Type -AssemblyName System.Net.Http

$CleClient = "e2e-cle-client-tp-spring"
$CleAdmin = "e2e-cle-admin-tp-spring1"
$Racine = Split-Path -Parent $PSScriptRoot
$Service = Join-Path $Racine "java\avis-service"
$Journaux = Join-Path $Service "target\e2e"
$SurWindows = ($env:OS -eq "Windows_NT")
if ($SurWindows) { $Mvnw = Join-Path $Service "mvnw.cmd" } else { $Mvnw = Join-Path $Service "mvnw" }
$script:Echecs = 0
$script:Processus = @()
$Http = New-Object System.Net.Http.HttpClient
$Http.Timeout = [TimeSpan]::FromSeconds(15)

function Attendre([string]$Url) {
    for ($i = 0; $i -lt 120; $i++) {
        try { $null = $Http.GetAsync($Url).GetAwaiter().GetResult(); return $true } catch { Start-Sleep -Milliseconds 500 }
    }
    return $false
}

function Lancer([string]$Fichier, [string[]]$Arguments, [string]$Journal) {
    $p = Start-Process -FilePath $Fichier -ArgumentList $Arguments -PassThru -NoNewWindow `
        -RedirectStandardOutput "$Journal.out" -RedirectStandardError "$Journal.err"
    $script:Processus += $p
    return $p
}

function Arreter($p) {
    if ($p -and -not $p.HasExited) {
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        $p.WaitForExit()
        Start-Sleep -Milliseconds 500
    }
}

function Lancer-Java([string]$UrlApi, [string]$Cle, [string]$Journal) {
    $env:SENTIMENT_API_URL = $UrlApi
    $env:SENTIMENT_API_KEY = $Cle
    $jar = (Get-ChildItem (Join-Path $Service "target\avis-service-*.jar") | Select-Object -First 1).FullName
    $p = Lancer "java" @("-jar", "`"$jar`"", "--server.port=$JavaPort", "--sentiment.api.transport=$Transport") $Journal
    if (-not (Attendre "http://localhost:$JavaPort/avis/sante")) {
        Write-Host "  le service Java ne démarre pas : voir $Journal.out"; exit 1
    }
    return $p
}

function Verifier([string]$Libelle, [int]$Statut, [string]$Attendu, [string]$Corps) {
    $contenu = New-Object System.Net.Http.StringContent($Corps, [System.Text.Encoding]::UTF8, "application/json")
    $r = $Http.PostAsync("http://localhost:$JavaPort/avis/analyse", $contenu).GetAwaiter().GetResult()
    $texte = $r.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    $obtenu = [int]$r.StatusCode
    if ($obtenu -eq $Statut -and $texte.Contains($Attendu)) {
        Write-Host ("  OK     {0,-38} {1} {2}" -f $Libelle, $obtenu, $texte)
    }
    else {
        Write-Host ("  ECHEC  {0,-38} {1} {2} (attendu {3}, {4})" -f $Libelle, $obtenu, $texte, $Statut, $Attendu)
        $script:Echecs++
    }
}

try {
    Write-Host "== Préparation"
    foreach ($p in @($ApiPort, $JavaPort)) {
        $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
        if ($conns) {
            $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($pidToKill in $pids) {
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            }
            Start-Sleep -Milliseconds 500
        }
    }
    New-Item -ItemType Directory -Force -Path $Journaux | Out-Null
    Set-Location $Racine
    if (-not (Test-Path "models\sentiment.joblib")) { python src\make_demo.py | Out-Null; python src\train.py | Out-Null }
    if (-not (Test-Path "models\sentiment.joblib")) { Write-Host "  modèle absent : lancez python src\train.py"; exit 1 }
    Push-Location $Service
    & $Mvnw -q -B -DskipTests package
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -ne 0) { Write-Host "  la construction Maven échoue"; exit 1 }

    $env:API_KEYS = "${CleClient}:client,${CleAdmin}:admin"
    $api = Lancer "python" @("-m", "uvicorn", "api.main:app", "--port", "$ApiPort") (Join-Path $Journaux "uvicorn")
    if (-not (Attendre "http://localhost:$ApiPort/v1/health")) {
        Write-Host "  l'API Python ne démarre pas : voir $Journaux\uvicorn.err"; exit 1
    }
    Write-Host "  API Python sur $ApiPort, journaux dans java\avis-service\target\e2e\"

    Write-Host "== J6 : le service Java contre l'API réelle (transport $Transport)"
    $j = Lancer-Java "http://127.0.0.1:$ApiPort" $CleClient (Join-Path $Journaux "java")
    Verifier "avis positif" 200 '"verdict":"POSITIVE"' '{"texte":"Livraison rapide, produit conforme, très satisfait"}'
    Verifier "avis négatif" 200 '"verdict":"NEGATIVE"' '{"texte":"Produit cassé et service injoignable, à fuir"}'
    Verifier "texte blanc" 400 'ENTREE_INVALIDE' '{"texte":"   "}'
    Arreter $j
    $j = Lancer-Java "http://127.0.0.1:$ApiPort" "mauvaise-cle-du-service-java" (Join-Path $Journaux "java-cle")
    Verifier "clé du service erronée" 502 'NON_AUTHENTIFIE' '{"texte":"Très bien"}'
    Arreter $j
    $j = Lancer-Java "http://127.0.0.1:1" $CleClient (Join-Path $Journaux "java-panne")
    Verifier "API Python injoignable" 503 'API_INJOIGNABLE' '{"texte":"Très bien"}'
    Arreter $j
    $journalApi = Get-Content (Join-Path $Journaux "uvicorn.err"), (Join-Path $Journaux "uvicorn.out") -Raw -ErrorAction SilentlyContinue
    if ($journalApi -match "Unsupported upgrade|Invalid HTTP request") {
        Write-Host "  ECHEC  uvicorn signale des requêtes corrompues (piège HTTP/2)"; $script:Echecs++
    }
    else {
        Write-Host "  OK     aucun avertissement de requête corrompue dans uvicorn"
    }

    Write-Host "== J7 : tests JUnit contre l'API réelle"
    if ($Transport -ne "jdk-http11") {
        Write-Host "  (J7 sauté : il teste le transport du cours, pas $Transport)"
    }
    else {
        $env:SENTIMENT_API_IT = "1"
        $env:SENTIMENT_API_URL = "http://127.0.0.1:$ApiPort"
        $env:SENTIMENT_API_KEY = $CleClient
        Push-Location $Service
        & $Mvnw -q -B test "-Dtest=ApiReelleTest" "-Dsurefire.failIfNoSpecifiedTests=false" *> (Join-Path $Journaux "it.log")
        $code = $LASTEXITCODE
        Pop-Location
        Remove-Item Env:SENTIMENT_API_IT
        if ($code -eq 0) {
            $ligne = Get-Content (Join-Path $Service "target\surefire-reports\ma.cours.avis.ApiReelleTest.txt") | Select-String "Tests run"
            Write-Host "  OK     $ligne"
        }
        else {
            Write-Host "  ECHEC  voir $Journaux\it.log"; $script:Echecs++
        }
    }
    Write-Host "== Bilan : $script:Echecs échec(s)"
}
finally {
    foreach ($p in $script:Processus) { Arreter $p }
    $Http.Dispose()
}
exit $script:Echecs
h