# Install the python environment of an ewoks workflow with nothing but a package
# manager. For example
#
#   & ([scriptblock]::Create((irm https://ewoks.readthedocs.io/en/stable/ewoks-install.ps1))) demo.json --package-manager-name uv
#
# Errors are thrown instead of calling `exit`, which would close the PowerShell
# session that runs the script block.

$ErrorActionPreference = "Stop"

$usage = @'
Usage: ewoks-install.ps1 [OPTIONS] WORKFLOW [ARGS ...]

Install the python environment of an ewoks workflow with nothing but a package
manager. The ewoks version that generated the workflow requirements is
installed in a bootstrap environment, which then runs

    ewoks install WORKFLOW ARGS

See 'ewoks install --help' for ARGS. The package manager that creates the
bootstrap environment is selected with '--package-manager-name' and
'--package-manager-command', which are passed to 'ewoks install' as well.
Without them it is the first available of uv, pixi, conda, poetry and pip-venv.

Options:
  --print-command          Print the 'ewoks install' command instead of
                           running it.
  --ewoks-requirement REQ  Install REQ instead of the ewoks version of the
                           workflow, for example 'ewoks>=7' or a wheel file.
  -h, --help               Show this help.

Environment variables:
  EWOKS_BOOTSTRAP_DIR      Directory of the bootstrap environments.
                           Default: ~/.ewoks/bootstrap
'@

$onWindows = ($PSVersionTable.PSEdition -eq "Desktop") -or $IsWindows

function Write-Info([string]$message) {
    [Console]::Error.WriteLine("ewoks-install: $message")
}

# Run a native command with its output on the console instead of in the pipeline
function Invoke-Native([string[]]$command) {
    $arguments = @()
    if ($command.Count -gt 1) {
        $arguments = $command[1..($command.Count - 1)]
    }
    & $command[0] @arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "command failed: $($command -join ' ')"
    }
}

function Test-Command([string]$name) {
    return [bool](Get-Command $name -CommandType Application -ErrorAction SilentlyContinue)
}

# Python interpreter with this major.minor version, or the default one
function Find-Python([string]$minor) {
    if ($onWindows) {
        if (Test-Command "py") {
            if ($minor) {
                & py "-$minor" -c "pass" 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    return @("py", "-$minor")
                }
            }
            return @("py", "-3")
        }
    } elseif ($minor -and (Test-Command "python$minor")) {
        return @("python$minor")
    } elseif (Test-Command "python3") {
        return @("python3")
    }
    if (Test-Command "python") {
        return @("python")
    }
    throw "no python interpreter found"
}

function Get-PythonMinor([string[]]$python) {
    $arguments = @()
    if ($python.Count -gt 1) {
        $arguments = $python[1..($python.Count - 1)]
    }
    $minor = & $python[0] @arguments -c 'import sys; print(''%d.%d'' % sys.version_info[:2])'
    if ($LASTEXITCODE -ne 0) {
        throw "cannot run $($python -join ' ')"
    }
    return "$minor".Trim()
}

# Argument quoted for PowerShell when needed
function Format-Argument([string]$argument) {
    if ($argument -match '^[A-Za-z0-9_./=:@%+,\\-]+$') {
        return $argument
    }
    return "'" + $argument.Replace("'", "''") + "'"
}

function Invoke-EwoksInstall([object[]]$arguments) {
    # --- Arguments: the bootstrap options are removed, the others are kept ---

    $printCommand = $false
    $requirement = ""
    $manager = ""
    $managerCommand = ""
    $workflow = ""
    $forwarded = @()
    $i = 0
    while ($i -lt $arguments.Count) {
        $arg = [string]$arguments[$i]
        $i++
        if ($arg -in @("-h", "--help")) {
            Write-Output $usage
            return
        }
        if ($arg -eq "--print-command") {
            $printCommand = $true
            continue
        }
        if ($arg -eq "--ewoks-requirement") {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $requirement = [string]$arguments[$i]
            $i++
            continue
        }
        if ($arg.StartsWith("--ewoks-requirement=")) {
            $requirement = $arg.Substring($arg.IndexOf("=") + 1)
            continue
        }
        $forwarded += $arg
        if ($arg -in @("--package-manager-name", "--package-manager-command")) {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $value = [string]$arguments[$i]
            $i++
            $forwarded += $value
            if ($arg -eq "--package-manager-name") {
                $manager = $value
            } else {
                $managerCommand = $value
            }
        } elseif ($arg.StartsWith("--package-manager-name=")) {
            $manager = $arg.Substring($arg.IndexOf("=") + 1)
        } elseif ($arg.StartsWith("--package-manager-command=")) {
            $managerCommand = $arg.Substring($arg.IndexOf("=") + 1)
        } elseif (-not $arg.StartsWith("-") -and -not $workflow -and (Test-Path -LiteralPath $arg -PathType Leaf)) {
            $workflow = $arg
        }
    }

    if (-not $workflow) {
        Write-Info $usage
        throw "provide the file of the workflow"
    }

    # --- Package manager ---

    $manager = $manager.ToLower()
    if (-not $manager) {
        if ($managerCommand) {
            throw "--package-manager-command requires --package-manager-name"
        }
        foreach ($name in @("uv", "pixi", "conda", "poetry")) {
            if (Test-Command $name) {
                $manager = $name
                break
            }
        }
        if (-not $manager) {
            $manager = "pip-venv"
        }
    }

    $command = @()
    if ($managerCommand) {
        $command = @($managerCommand -split '\s+' | Where-Object { $_ })
    }
    if ($manager -in @("uv", "pixi", "conda", "poetry")) {
        if (-not $command) { $command = @($manager) }
    } elseif ($manager -ne "pip-venv") {
        throw "package manager '$manager' is not supported"
    }

    # --- Ewoks and python versions of the workflow requirements ---

    $version = ""
    $pythonVersion = ""
    try {
        $requirements = (Get-Content -LiteralPath $workflow -Raw | ConvertFrom-Json).graph.requirements
        if ($requirements.ewoks.version) { $version = [string]$requirements.ewoks.version }
        if ($requirements.python.version) { $pythonVersion = [string]$requirements.python.version }
    } catch {
        Write-Info "cannot read the requirements of '$workflow'"
    }
    $pythonMinor = ""
    if ($pythonVersion -match '^(\d+\.\d+)') {
        $pythonMinor = $Matches[1]
    }

    if ($requirement) {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($requirement))
        $tag = "custom-" + (($hash[0..4] | ForEach-Object { $_.ToString("x2") }) -join "")
    } elseif ($version) {
        $tag = $version
        $requirement = "ewoks==$version"
    } else {
        Write-Info "the workflow does not provide the ewoks version: using the latest one"
        $tag = "latest"
        $requirement = "ewoks>=7"
    }

    # pip-venv and poetry cannot provide a python version: the interpreter decides
    $basePython = @()
    if ($manager -eq "pip-venv") {
        if (-not $command) { $command = @(Find-Python $pythonMinor) }
        $pythonMinor = Get-PythonMinor $command
    } elseif ($manager -eq "poetry") {
        $basePython = @(Find-Python $pythonMinor)
        $pythonMinor = Get-PythonMinor $basePython
    }

    $root = $env:EWOKS_BOOTSTRAP_DIR
    if (-not $root) {
        $root = Join-Path (Join-Path $HOME ".ewoks") "bootstrap"
    }
    $name = "ewoks-$tag"
    if ($pythonMinor) {
        $name = "$name-python$pythonMinor"
    }
    $location = Join-Path (Join-Path $root $manager) $name

    # --- Bootstrap environment ---

    if ($onWindows) {
        $venvPython = Join-Path "Scripts" "python.exe"
        $prefixPython = "python.exe"
    } else {
        $venvPython = Join-Path "bin" "python"
        $prefixPython = $venvPython
    }
    switch ($manager) {
        "pixi" { $python = Join-Path $location (Join-Path ".pixi/envs/default" $prefixPython) }
        "conda" { $python = Join-Path $location $prefixPython }
        "poetry" { $python = Join-Path $location (Join-Path ".venv" $venvPython) }
        default { $python = Join-Path $location $venvPython }
    }

    $pythonSpec = "python"
    if ($pythonMinor) {
        $pythonSpec = "python=$pythonMinor"
    }
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        Write-Info "create the bootstrap environment $location"
        # A previous attempt failed
        if (Test-Path -LiteralPath $location) {
            Remove-Item -LiteralPath $location -Recurse -Force
        }
        New-Item -ItemType Directory -Path $location -Force | Out-Null
        switch ($manager) {
            "uv" {
                $create = $command + @("venv", "--quiet")
                if ($pythonMinor) { $create += @("--python", $pythonMinor) }
                Invoke-Native ($create + @($location))
            }
            "pixi" {
                Invoke-Native ($command + @("init", $location))
                Invoke-Native ($command + @("add", "--manifest-path", (Join-Path $location "pixi.toml"), $pythonSpec, "pip"))
            }
            "conda" {
                Invoke-Native ($command + @("create", "--yes", "--quiet", "--prefix", $location, $pythonSpec, "pip"))
            }
            "poetry" {
                $pyproject = "[tool.poetry]`npackage-mode = false`n`n[tool.poetry.dependencies]`npython = `"*`"`n"
                [System.IO.File]::WriteAllText((Join-Path $location "pyproject.toml"), $pyproject)
                # Poetry uses an active virtual or conda environment instead of the one of the project
                $virtualEnv = $env:VIRTUAL_ENV
                $condaPrefix = $env:CONDA_PREFIX
                $inProject = $env:POETRY_VIRTUALENVS_IN_PROJECT
                try {
                    Remove-Item Env:VIRTUAL_ENV, Env:CONDA_PREFIX -ErrorAction SilentlyContinue
                    $env:POETRY_VIRTUALENVS_IN_PROJECT = "true"
                    $interpreter = & $basePython[0] @($basePython | Select-Object -Skip 1) -c "import sys; print(sys.executable)"
                    Invoke-Native ($command + @("-C", $location, "env", "use", "$interpreter".Trim()))
                } finally {
                    $env:VIRTUAL_ENV = $virtualEnv
                    $env:CONDA_PREFIX = $condaPrefix
                    $env:POETRY_VIRTUALENVS_IN_PROJECT = $inProject
                }
            }
            "pip-venv" {
                Invoke-Native ($command + @("-m", "venv", $location))
            }
        }
    }

    $installed = ""
    try {
        $installed = "$(& $python -c 'import importlib.metadata as m; print(m.version(''ewoks''))' 2>$null)".Trim()
    } catch {
        $installed = ""
    }

    if (($tag -ne $version) -or ($installed -ne $version)) {
        Write-Info "install $requirement in $location"
        try {
            if ($manager -eq "uv") {
                Invoke-Native ($command + @("pip", "install", "--quiet", "--upgrade", "--python", $python, $requirement))
            } else {
                Invoke-Native @($python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--upgrade", $requirement)
            }
        } catch {
            throw "cannot install $requirement (see --ewoks-requirement)"
        }
    }

    # --- ewoks install ---

    $install = @("-m", "ewoks", "install") + $forwarded
    if ($printCommand) {
        $formatted = @($install | ForEach-Object { Format-Argument $_ })
        Write-Output ("& " + "'" + $python.Replace("'", "''") + "' " + ($formatted -join " "))
    } else {
        & $python @install
    }
}

Invoke-EwoksInstall $args
