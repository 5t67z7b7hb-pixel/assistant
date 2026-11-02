$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$root = $PSScriptRoot
Set-Location -LiteralPath $root

try {
    Write-Host 'Voice Assistant setup: this may take several minutes and needs internet.' -ForegroundColor Cyan

    # Find Python 3.11, or install it for the current Windows user with winget.
    $pythonExe = $null
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $candidate = & $pyLauncher.Source -3.11 -c 'import sys; print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0 -and $candidate) {
            $candidatePath = ([string]$candidate).Trim()
            if (Test-Path -LiteralPath $candidatePath) { $pythonExe = $candidatePath }
        }
    }
    if (-not $pythonExe) {
        $candidatePath = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'
        if (Test-Path -LiteralPath $candidatePath) { $pythonExe = $candidatePath }
    }
    if (-not $pythonExe) {
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) { throw 'Python 3.11 is missing and winget was not found. Install Python 3.11, then run this installer again.' }
        Write-Host 'Installing Python 3.11...' -ForegroundColor Yellow
        & $winget.Source install --id Python.Python.3.11 --exact --scope user --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { throw 'Python installation did not complete.' }
        $candidatePath = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'
        for ($i = 0; $i -lt 30 -and -not (Test-Path -LiteralPath $candidatePath); $i++) { Start-Sleep -Seconds 1 }
        if (Test-Path -LiteralPath $candidatePath) { $pythonExe = $candidatePath }
        else { throw 'Python was installed but could not be located. Reopen this folder and run Install Assistant.bat again.' }
    }

    # Install Ollama using its official Windows installer if needed.
    $ollamaCommand = Get-Command ollama.exe -ErrorAction SilentlyContinue
    $ollamaExe = if ($ollamaCommand) { $ollamaCommand.Source } else { $null }
    if (-not $ollamaExe) {
        Write-Host 'Installing Ollama from its official Windows installer...' -ForegroundColor Yellow
        $officialInstall = 'irm https://ollama.com/install.ps1 | iex'
        & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command $officialInstall
        if ($LASTEXITCODE -ne 0) { throw 'Ollama installation did not complete.' }
        $ollamaCommand = Get-Command ollama.exe -ErrorAction SilentlyContinue
        if ($ollamaCommand) { $ollamaExe = $ollamaCommand.Source }
        if (-not $ollamaExe) {
            $candidatePath = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
            if (Test-Path -LiteralPath $candidatePath) { $ollamaExe = $candidatePath }
        }
        if (-not $ollamaExe) { throw 'Ollama was installed but could not be located. Reopen this folder and run Install Assistant.bat again.' }
    }

    # Install Python packages into this app folder, so no global pip setup is needed.
    $venvPython = Join-Path $root '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Write-Host 'Creating the app environment...' -ForegroundColor Yellow
        & $pythonExe -m venv (Join-Path $root '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
    }
    Write-Host 'Installing assistant packages...' -ForegroundColor Yellow
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw 'Could not update pip.' }
    & $venvPython -m pip install -r (Join-Path $root 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the assistant packages.' }

    # Start Ollama in the background if the Windows app has not already started it.
    $apiReady = $false
    try { $null = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2; $apiReady = $true } catch { }
    if (-not $apiReady) {
        Write-Host 'Starting the local model service...' -ForegroundColor Yellow
        Start-Process -FilePath $ollamaExe -ArgumentList 'serve' -WindowStyle Hidden
        for ($i = 0; $i -lt 60; $i++) {
            Start-Sleep -Seconds 2
            try { $null = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2; $apiReady = $true; break } catch { }
        }
    }
    if (-not $apiReady) { throw 'Ollama did not start. Open Ollama and run Install Assistant.bat again.' }

    Write-Host 'Importing the included Qwen3 model...' -ForegroundColor Yellow
    & $ollamaExe create qwen3:4b-instruct-2507-q4_K_M -f (Join-Path $root 'Modelfile')
    if ($LASTEXITCODE -ne 0) { throw 'Ollama could not import the included model.' }

    Write-Host 'Setup is complete. Opening the assistant...' -ForegroundColor Green
    & $venvPython (Join-Path $root 'app.py')
    if ($LASTEXITCODE -ne 0) { throw 'The assistant closed with an error. See logs\voice_assistant.log if present.' }
}
catch {
    Write-Host "`nSetup error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
