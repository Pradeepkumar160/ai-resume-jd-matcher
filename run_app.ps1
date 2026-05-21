#Requires -Version 5.1
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "" ; Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "  [OK] $msg"   -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

Write-Step "Checking Docker..."
try {
    $null = docker info 2>&1
    Write-OK "Docker is running."
} catch {
    Write-Fail "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

Write-Step "Checking Docker Compose..."
try {
    $null = docker compose version 2>&1
    Write-OK "Docker Compose is available."
} catch {
    Write-Fail "Docker Compose not found. It ships with Docker Desktop."
    exit 1
}

Write-Step "Verifying project files..."
$required = @("docker-compose.yml", "backend\Dockerfile", "frontend\Dockerfile")
foreach ($f in $required) {
    if (Test-Path $f) {
        Write-OK "Found: $f"
    } else {
        Write-Fail "Missing: $f"
        exit 1
    }
}

Write-Step "Building and starting containers (first run takes 5-10 minutes)..."
Write-Host "  NOTE: Downloading NLP model ~90MB inside Docker - please be patient." -ForegroundColor Yellow

docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Fail "docker compose up failed."
    exit 1
}
Write-OK "Containers started."

Write-Step "Waiting for backend to be ready..."
$maxWait  = 120
$elapsed  = 0
$interval = 5

while ($elapsed -lt $maxWait) {
    Start-Sleep -Seconds $interval
    $elapsed += $interval
    try {
        $resp = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
        Write-OK "Backend is healthy! (database: $($resp.database))"
        break
    } catch {
        Write-Host "  Waiting... ($elapsed/$maxWait sec)" -ForegroundColor Yellow
    }
}

if ($elapsed -ge $maxWait) {
    Write-Host "Backend did not respond in time - check: docker compose logs backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  APP IS RUNNING!" -ForegroundColor Green
Write-Host ""
Write-Host "  Streamlit UI  -->  http://localhost:8501" -ForegroundColor Cyan
Write-Host "  API Docs      -->  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Health Check  -->  http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To stop:  docker compose down" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Green

Start-Process "http://localhost:8501"
