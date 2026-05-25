param(
    [string]$ServerUrl = "http://localhost:5000"
)

# Legacy helper: this script resets the optional FastAPI backend demo.
# It is not required for the official React/Phaser demo in frontend/.

$ErrorActionPreference = "Stop"
$baseUrl = $ServerUrl.TrimEnd("/")

function Invoke-SilaGet {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    Invoke-RestMethod -Method Get -Uri "$baseUrl$Path"
}

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    Write-Host ""
    Write-Host "== $Title =="
}

try {
    Write-Section "Reset demo"
    $reset = Invoke-SilaGet "/nfc?letra=RESET_TODO"
    $reset | ConvertTo-Json -Depth 8

    Write-Section "Healthcheck"
    $health = Invoke-SilaGet "/health"
    $health | ConvertTo-Json -Depth 8

    Write-Section "Buffer"
    $buffer = Invoke-SilaGet "/buffer"
    $buffer | ConvertTo-Json -Depth 8

    Write-Section "Progress"
    $progress = Invoke-SilaGet "/progress"
    $progress | ConvertTo-Json -Depth 8
}
catch {
    Write-Error "No se pudo contactar el servidor en $baseUrl. Inicia primero: .\.venv\Scripts\python.exe arduino\sila_server.py"
    exit 1
}

Write-Section "Telefono en la misma WiFi"
$serverUri = [Uri]$baseUrl
$port = $serverUri.Port
$scheme = $serverUri.Scheme
$localIps = @()
try {
    $localIps = [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
        Where-Object {
            $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork -and
            $_.IPAddressToString -notlike "127.*" -and
            $_.IPAddressToString -notlike "169.254.*"
        } |
        ForEach-Object { $_.IPAddressToString } |
        Sort-Object -Unique
}
catch {
    $localIps = @()
}

if (-not $localIps) {
    Write-Host "No encontre una IP local activa. Revisa con: ipconfig"
}
else {
    Write-Host "Configura el telefono/NFC Tools con una de estas URLs:"
    foreach ($ip in $localIps) {
        Write-Host "$scheme`://$ip`:$port/nfc?letra=MA"
    }
}

Write-Host ""
Write-Host "Pantallas:"
Write-Host "$baseUrl/"
Write-Host "$baseUrl/aldea"
