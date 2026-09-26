# Citizen Rights and Government Scheme Navigator - Quick Start Script
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " Citizen Rights and Government Scheme Navigator" -ForegroundColor Green
Write-Host " MAIT CST Department - Minor Project Batch (2023-2027)" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerInstalled) {
    Write-Host "[1] Docker detected! Building and launching containers (images prefixed with 'minor_')..." -ForegroundColor Yellow
    docker compose up --build
} else {
    Write-Host "[2] Starting local Python server at http://localhost:8000 ..." -ForegroundColor Yellow
    python run_backend.py
}
