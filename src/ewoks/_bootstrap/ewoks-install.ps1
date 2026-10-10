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
manager. The ewoks version that generated the workflow requirements, and the
engine that saved the workflow, are installed in a bootstrap environment, which
then runs

    ewoks install WORKFLOW ARGS

See 'ewoks install --help' for ARGS. The package manager that creates the
bootstrap environment is selected with '--package-manager-name' and
'--package-manager-command', which are passed to 'ewoks install' as well.
Without them it is the first available of uv, pixi, conda, poetry and pip-venv.
A package manager that is not installed can be installed in the bootstrap
directory with '--install-package-manager'.

Options:
  --print-command          Print the 'ewoks install' command instead of
                           running it.
  --ewoks-requirement REQ  Install REQ instead of the ewoks version and engine
                           of the workflow, for example 'ewoks>=7' or a wheel
                           file. Repeat it to install more, for example
                           '--ewoks-requirement ewoks --ewoks-requirement
                           ewoksmyengine'.
  --bootstrap-dir DIR      Directory of the bootstrap environments.
                           Default: ~/.ewoks/bootstrap
  --install-package-manager
                           Install the package manager of
                           '--package-manager-name' when it is not installed.
  -h, --help               Show this help.
'@

$onWindows = ($PSVersionTable.PSEdition -eq "Desktop") -or $IsWindows

function Write-Info([string]$message) {
    [Console]::Error.WriteLine("ewoks-install: $message")
}

# Run a native command with its output on stderr instead of in the pipeline
function Invoke-Native([string[]]$command) {
    $arguments = @()
    if ($command.Count -gt 1) {
        $arguments = $command[1..($command.Count - 1)]
    }
    & $command[0] @arguments 2>&1 | ForEach-Object { [Console]::Error.WriteLine($_) }
    if ($LASTEXITCODE -ne 0) {
        throw "command failed: $($command -join ' ')"
    }
}

function Test-Command([string]$name) {
    return [bool](Get-Command $name -CommandType Application -ErrorAction SilentlyContinue)
}

# Python interpreter with this major.minor version, or the default one
function Find-Python([string]$majorMinor) {
    if ($onWindows) {
        if (Test-Command "py") {
            if ($majorMinor) {
                & py "-$majorMinor" -c "pass" 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    return @("py", "-$majorMinor")
                }
            }
            return @("py", "-3")
        }
    } elseif ($majorMinor -and (Test-Command "python$majorMinor")) {
        return @("python$majorMinor")
    } elseif (Test-Command "python3") {
        return @("python3")
    }
    if (Test-Command "python") {
        return @("python")
    }
    throw "no python interpreter found"
}

function Get-PythonMajorMinor([string[]]$python) {
    $arguments = @()
    if ($python.Count -gt 1) {
        $arguments = $python[1..($python.Count - 1)]
    }
    $majorMinor = & $python[0] @arguments -c 'import sys; print(''%d.%d'' % sys.version_info[:2])'
    if ($LASTEXITCODE -ne 0) {
        throw "cannot run $($python -join ' ')"
    }
    return "$majorMinor".Trim()
}

# Value in the requirements of a workflow file, for example `ewoks.version`. The
# requirements are JSON, which can be embedded in another format, or YAML.
function Get-RequirementValue([string]$content, [string]$key) {
    $value = Get-JsonRequirementValue $content $key
    if (-not $value) {
        $value = Get-YamlRequirementValue $content $key
    }
    return $value
}

function Get-JsonRequirementValue([string]$content, [string]$key) {
    $q = "[""']"
    $value = "$q\s*:\s*$q([^""']*)$q"
    # The members of an object, which can contain objects themselves
    $members = "[^{}]*(?:\{[^{}]*\}[^{}]*)*"
    switch ($key) {
        "ewoks.version" { $pattern = "${q}ewoks$q\s*:\s*\{$members${q}version$value" }
        "ewoks.engine.name" { $pattern = "${q}ewoks$q\s*:\s*\{[^{}]*${q}engine$q\s*:\s*\{[^{}]*${q}name$value" }
        "ewoks.engine.version" { $pattern = "${q}ewoks$q\s*:\s*\{[^{}]*${q}engine$q\s*:\s*\{[^{}]*${q}version$value" }
        "python.version" { $pattern = "${q}python$q\s*:\s*\{[^{}]*${q}version$value" }
    }
    $found = [regex]::Matches($content.Replace("&quot;", '"'), $pattern)
    if ($found.Count -eq 0) {
        return ""
    }
    return $found[$found.Count - 1].Groups[1].Value
}

function Get-YamlRequirementValue([string]$content, [string]$key) {
    $wanted = "requirements.$key"
    $indents = New-Object System.Collections.Generic.List[int]
    $keys = New-Object System.Collections.Generic.List[string]
    $found = ""
    foreach ($line in ($content -split "\r?\n")) {
        if ($line -match '^\s*(#|$)') {
            continue
        }
        # The dash of a list item belongs to the indentation of its first key
        $match = [regex]::Match($line, '^([ -]*)([A-Za-z0-9_]+):\s*(.*)$')
        if (-not $match.Success) {
            continue
        }
        $indent = $match.Groups[1].Length
        while ($indents.Count -gt 0 -and $indents[$indents.Count - 1] -ge $indent) {
            $indents.RemoveAt($indents.Count - 1)
            $keys.RemoveAt($keys.Count - 1)
        }
        $indents.Add($indent)
        $keys.Add($match.Groups[2].Value)
        $path = $keys -join "."
        $value = $match.Groups[3].Value
        if ($value -and (($path -eq $wanted) -or $path.EndsWith(".$wanted"))) {
            $found = $value -replace "^[""']|[""']$", ""
        }
    }
    return $found
}

# Version of an installed distribution, or nothing when it is not installed
function Get-DistributionVersion([string]$python, [string]$name) {
    try {
        return "$(& $python -c 'import importlib.metadata as m, sys; print(m.version(sys.argv[1]))' $name 2>$null)".Trim()
    } catch {
        return ""
    }
}

# Argument quoted for PowerShell when needed
function Format-Argument([string]$argument) {
    if ($argument -match '^[A-Za-z0-9_./=:@%+,\\-]+$') {
        return $argument
    }
    return "'" + $argument.Replace("'", "''") + "'"
}

# Executable of a package manager installed in a directory by this script
function Get-ManagerExecutable([string]$manager, [string]$directory) {
    $suffix = ""
    if ($onWindows) { $suffix = ".exe" }
    if ($manager -eq "conda") {
        if ($onWindows) { return Join-Path (Join-Path $directory "Scripts") "conda.exe" }
        return Join-Path (Join-Path $directory "bin") "conda"
    }
    return Join-Path (Join-Path $directory "bin") "$manager$suffix"
}

# Run a native command with additional environment variables
function Invoke-NativeWithEnv([hashtable]$variables, [string[]]$command) {
    $previous = @{}
    foreach ($name in $variables.Keys) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name)
        [Environment]::SetEnvironmentVariable($name, $variables[$name])
    }
    try {
        Invoke-Native $command
    } finally {
        foreach ($name in $variables.Keys) {
            [Environment]::SetEnvironmentVariable($name, $previous[$name])
        }
    }
}

# Install a package manager in a directory with its official installer
function Install-Manager([string]$manager, [string]$directory) {
    Write-Info "install $manager in $directory"
    if (Test-Path -LiteralPath $directory) {
        Remove-Item -LiteralPath $directory -Recurse -Force
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $directory) -Force | Out-Null
    # The PowerShell installers of uv and pixi only install Windows binaries
    # and exit their PowerShell session
    if ($onWindows) {
        $suffix = ".ps1"
        $runInstaller = @((Get-Process -Id $PID).Path, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File")
    } else {
        $suffix = ".sh"
        $runInstaller = @("sh")
    }
    $temp = [System.IO.Path]::GetTempPath()
    $installer = Join-Path $temp ("ewoks-install-" + [guid]::NewGuid())
    try {
        switch ($manager) {
            "uv" {
                $installer += $suffix
                Invoke-WebRequest -UseBasicParsing -Uri "https://astral.sh/uv/install$suffix" -OutFile $installer
                Invoke-NativeWithEnv @{ UV_INSTALL_DIR = (Join-Path $directory "bin"); UV_NO_MODIFY_PATH = "1" } ($runInstaller + @($installer))
            }
            "pixi" {
                $installer += $suffix
                Invoke-WebRequest -UseBasicParsing -Uri "https://pixi.sh/install$suffix" -OutFile $installer
                Invoke-NativeWithEnv @{ PIXI_HOME = $directory; PIXI_NO_PATH_UPDATE = "1" } ($runInstaller + @($installer))
            }
            "poetry" {
                $installer += ".py"
                Invoke-WebRequest -UseBasicParsing -Uri "https://install.python-poetry.org" -OutFile $installer
                Invoke-NativeWithEnv @{ POETRY_HOME = $directory } (@(Find-Python "") + @($installer))
            }
            "conda" {
                $url = "https://github.com/conda-forge/miniforge/releases/latest/download"
                if ($onWindows) {
                    $installer += ".exe"
                    Invoke-WebRequest -UseBasicParsing -Uri "$url/Miniforge3-Windows-x86_64.exe" -OutFile $installer
                    # '/D' must be the last argument and must not be quoted
                    Start-Process -Wait -FilePath $installer -ArgumentList "/S", "/D=$directory"
                } else {
                    $installer += ".sh"
                    $system = "$(uname -s)".Trim()
                    if ($system -eq "Darwin") { $system = "MacOSX" }
                    $machine = "$(uname -m)".Trim()
                    Invoke-WebRequest -UseBasicParsing -Uri "$url/Miniforge3-$system-$machine.sh" -OutFile $installer
                    Invoke-Native @("bash", $installer, "-b", "-p", $directory)
                }
            }
        }
    } finally {
        Remove-Item -LiteralPath $installer -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-EwoksInstall([object[]]$arguments) {
    # --- Arguments: the bootstrap options are removed, the others are kept ---

    $printCommand = $false
    $installPackageManager = $false
    $requirements = @()
    $root = Join-Path (Join-Path $HOME ".ewoks") "bootstrap"
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
        if ($arg -eq "--install-package-manager") {
            $installPackageManager = $true
            continue
        }
        if ($arg -eq "--ewoks-requirement") {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $requirements += [string]$arguments[$i]
            $i++
            continue
        }
        if ($arg.StartsWith("--ewoks-requirement=")) {
            $requirements += $arg.Substring($arg.IndexOf("=") + 1)
            continue
        }
        if ($arg -eq "--bootstrap-dir") {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $root = [string]$arguments[$i]
            $i++
            continue
        }
        if ($arg.StartsWith("--bootstrap-dir=")) {
            $root = $arg.Substring($arg.IndexOf("=") + 1)
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
    if ($installPackageManager -and -not $manager) {
        throw "--install-package-manager requires --package-manager-name"
    }
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

    $cmd = @()
    if ($managerCommand) {
        $cmd = @($managerCommand -split '\s+' | Where-Object { $_ })
    }
    if ($manager -in @("uv", "pixi", "conda", "poetry")) {
        if (-not $cmd) { $cmd = @($manager) }
    } elseif ($manager -ne "pip-venv") {
        throw "package manager '$manager' is not supported"
    }

    # `ewoks install` needs the package manager this script installed
    if ($cmd -and -not $managerCommand -and -not (Test-Command $cmd[0])) {
        $managerDir = Join-Path (Join-Path $root "package-managers") $manager
        $executable = Get-ManagerExecutable $manager $managerDir
        if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
            if (-not $installPackageManager) {
                throw "$manager is not installed (see --install-package-manager)"
            }
            Install-Manager $manager $managerDir
            if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
                throw "cannot install $manager in $managerDir"
            }
        }
        $cmd = @($executable)
        $forwarded += @("--package-manager-command", $executable)
    }

    # --- Ewoks, engine and python versions of the workflow requirements ---

    $content = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $workflow))
    $version = Get-RequirementValue $content "ewoks.version"
    $engine = Get-RequirementValue $content "ewoks.engine.name"
    $engineVersion = Get-RequirementValue $content "ewoks.engine.version"
    $pythonVersion = Get-RequirementValue $content "python.version"
    if (-not $engineVersion) {
        $engine = ""
    }
    $pythonMajorMinor = ""
    if ($pythonVersion -match '^(\d+\.\d+)') {
        $pythonMajorMinor = $Matches[1]
    }

    # The bootstrap environment of pinned requirements is up to date when it has their versions
    $pinned = $false
    if ($requirements) {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($requirements -join " "))
        $tag = "custom-" + (($hash[0..4] | ForEach-Object { $_.ToString("x2") }) -join "")
    } elseif ($version) {
        $pinned = $true
        $tag = $version
        $requirements = @("ewoks==$version")
        if ($engine) {
            $tag = "$tag-$engine-$engineVersion"
            $requirements += "$engine==$engineVersion"
        }
    } else {
        Write-Info "the workflow does not provide the ewoks version: using the latest one"
        $tag = "latest"
        $requirements = @("ewoks>=7")
    }

    # pip-venv and poetry cannot provide a python version: the interpreter decides
    $basePython = @()
    if ($manager -eq "pip-venv") {
        if (-not $cmd) { $cmd = @(Find-Python $pythonMajorMinor) }
        $pythonMajorMinor = Get-PythonMajorMinor $cmd
    } elseif ($manager -eq "poetry") {
        $basePython = @(Find-Python $pythonMajorMinor)
        $pythonMajorMinor = Get-PythonMajorMinor $basePython
    }

    $name = "ewoks-$tag"
    if ($pythonMajorMinor) {
        $name = "$name-python$pythonMajorMinor"
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
    if ($pythonMajorMinor) {
        $pythonSpec = "python=$pythonMajorMinor"
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
                $create = $cmd + @("venv", "--quiet")
                if ($pythonMajorMinor) { $create += @("--python", $pythonMajorMinor) }
                Invoke-Native ($create + @($location))
            }
            "pixi" {
                Invoke-Native ($cmd + @("init", $location))
                Invoke-Native ($cmd + @("add", "--manifest-path", (Join-Path $location "pixi.toml"), $pythonSpec, "pip"))
            }
            "conda" {
                Invoke-Native ($cmd + @("create", "--yes", "--quiet", "--prefix", $location, $pythonSpec, "pip"))
            }
            "poetry" {
                $pyproject = "[tool.poetry]`npackage-mode = false`n`n[tool.poetry.dependencies]`npython = `"*`"`n"
                [System.IO.File]::WriteAllText((Join-Path $location "pyproject.toml"), $pyproject)
                $interpreter = & $basePython[0] @($basePython | Select-Object -Skip 1) -c "import sys; print(sys.executable)"
                # Poetry uses an active virtual or conda environment instead of the one of the project.
                # Without its own python it runs the `python` command, which can be python 2.
                $variables = @{
                    VIRTUAL_ENV = $null
                    CONDA_PREFIX = $null
                    POETRY_VIRTUALENVS_IN_PROJECT = "true"
                    POETRY_VIRTUALENVS_USE_POETRY_PYTHON = "true"
                }
                Invoke-NativeWithEnv $variables ($cmd + @("-C", $location, "env", "use", "$interpreter".Trim()))
            }
            "pip-venv" {
                Invoke-Native ($cmd + @("-m", "venv", $location))
            }
        }
    }

    $upToDate = $pinned -and ((Get-DistributionVersion $python "ewoks") -eq $version)
    if ($upToDate -and $engine) {
        $upToDate = (Get-DistributionVersion $python $engine) -eq $engineVersion
    }

    if (-not $upToDate) {
        Write-Info "install $($requirements -join ' ') in $location"
        try {
            if ($manager -eq "uv") {
                Invoke-Native ($cmd + @("pip", "install", "--quiet", "--upgrade", "--python", $python) + $requirements)
            } else {
                Invoke-Native (@($python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--upgrade") + $requirements)
            }
        } catch {
            throw "cannot install $($requirements -join ' ') (see --ewoks-requirement)"
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
