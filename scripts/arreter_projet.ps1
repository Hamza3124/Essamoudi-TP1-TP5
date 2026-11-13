# Arrêt de tous les services du projet (ports 8000, 8081, 8501)
$ports = @(8000, 8081, 8501)
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids) {
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            Write-Host "Processus arrêté sur le port $port (PID: $p)"
        }
    }
}
Write-Host "Tous les services sont arrêtés."

