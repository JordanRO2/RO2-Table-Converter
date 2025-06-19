# RO2 Table Converter - PowerShell Setup Script
# Community tool for converting RO2 CT files to Excel format

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Banner {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " RO2 Table Converter - Community Tool" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Show-Banner
    Write-Host "USAGE:" -ForegroundColor Green
    Write-Host "  .\setup.ps1 install    Install dependencies" -ForegroundColor White
    Write-Host "  .\setup.ps1 run        Start the web interface" -ForegroundColor White
    Write-Host "  .\setup.ps1 help       Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "REPOSITORY:" -ForegroundColor Green
    Write-Host "  https://github.com/JordanRO2/RO2-Table-Converter" -ForegroundColor Blue
    Write-Host ""
    Write-Host "This is a community-driven tool for Ragnarok Online 2" -ForegroundColor Gray
}

function Install-Dependencies {
    Show-Banner
    Write-Host "🔧 Installing dependencies..." -ForegroundColor Yellow
    
    try {
        python -m pip install -r requirements.txt
        Write-Host ""
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
        Write-Host "💡 Run '.\setup.ps1 run' to start the web interface" -ForegroundColor Cyan
    }
    catch {
        Write-Host ""
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Write-Host "💡 Make sure Python 3.8+ is installed and in PATH" -ForegroundColor Yellow
    }
}

function Start-Application {
    Show-Banner
    Write-Host "🚀 Starting RO2 Table Converter..." -ForegroundColor Green
    Write-Host "📍 Web interface: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "⏹️  Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        python app.py
    }
    catch {
        Write-Host "❌ Failed to start application" -ForegroundColor Red
        Write-Host "💡 Make sure dependencies are installed: .\setup.ps1 install" -ForegroundColor Yellow
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "install" { Install-Dependencies }
    "run" { Start-Application }
    "help" { Show-Help }
    default { Show-Help }
}
