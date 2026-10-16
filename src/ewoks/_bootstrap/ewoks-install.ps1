# Install the python environment of an ewoks workflow with nothing but a package
# manager. For example
#
#   & ([scriptblock]::Create((irm https://ewoks.readthedocs.io/en/stable/ewoks-install.ps1))) demo.json --package-manager-name uv
#
# or download the script first
#
#   irm https://ewoks.readthedocs.io/en/stable/ewoks-install.ps1 -OutFile ewoks-install.ps1
#   powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json --package-manager-name uv
#
# Steps (see `Invoke-EwoksInstall` at the end), like ewoks-install.sh:
#
#   1. Split the arguments in options of this script and arguments of `ewoks install`.
#   2. Select the package manager.
#   3. Read the ewoks, engine and python versions from the workflow requirements.
#   4. Create a bootstrap environment with that ewoks and engine, unless it exists.
#   5. Run `ewoks install` in the bootstrap environment.
#
# The bootstrap environments are cached in ~/.ewoks/bootstrap/<manager>/<name>
# where the name is, for example, `ewoks=7.0.0@ewokscore=5.1.0@python=3.12`.
#
# Errors are thrown instead of calling `exit`, which would close the PowerShell
# session that runs the script block. Native commands run with the "Continue"
# error action: Windows PowerShell 5.1 turns their stderr into errors.

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
  --bootstrap-requirement REQ
                           Install REQ in the bootstrap environment instead of
                           the ewoks version and engine of the workflow, for
                           example 'ewoks>=7' or a wheel file. Repeat it to
                           install an engine as well, for example
                           '--bootstrap-requirement ewoks
                           --bootstrap-requirement ewoksorange'.
  --bootstrap-dir DIR      Directory of the bootstrap environments.
                           Default: ~/.ewoks/bootstrap
  --install-package-manager
                           Install the package manager of
                           '--package-manager-name' when it is not installed.
  -h, --help               Show this help.
'@

$onWindows = ($PSVersionTable.PSEdition -eq "Desktop") -or $IsWindows

# =============================================================================
# Helpers
# =============================================================================

function Write-Info([string]$message) {
    [Console]::Error.WriteLine("ewoks-install: $message")
}

# Argument quoted for PowerShell when needed
function Format-Argument([string]$argument) {
    if ($argument -match '^[A-Za-z0-9_./=:+\\-]+$') {
        return $argument
    }
    return "'" + $argument.Replace("'", "''") + "'"
}

# Arguments quoted for PowerShell and joined with spaces
function Format-Arguments([string[]]$arguments) {
    return @($arguments | ForEach-Object { Format-Argument $_ }) -join " "
}

function Test-Command([string]$name) {
    return [bool](Get-Command $name -CommandType Application -ErrorAction SilentlyContinue)
}

# Run a native command with its output on stderr instead of in the pipeline
function Invoke-Native([string[]]$command) {
    $ErrorActionPreference = "Continue"
    $arguments = @()
    if ($command.Count -gt 1) {
        $arguments = $command[1..($command.Count - 1)]
    }
    & $command[0] @arguments 2>&1 | ForEach-Object { [Console]::Error.WriteLine($_) }
    if ($LASTEXITCODE -ne 0) {
        throw "command failed: $($command -join ' ')"
    }
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

# Output of a native command
function Get-NativeOutput([string[]]$command) {
    $ErrorActionPreference = "Continue"
    $arguments = @()
    if ($command.Count -gt 1) {
        $arguments = $command[1..($command.Count - 1)]
    }
    $output = & $command[0] @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "command failed: $($command -join ' ')"
    }
    return "$output".Trim()
}

# Python interpreter with this major.minor version, or the default one
function Find-Python([string]$majorMinor) {
    $ErrorActionPreference = "Continue"
    if ($onWindows) {
        # The python of the PATH, like the one of an active environment, when it has this version
        if ($majorMinor -and (Test-Command "python")) {
            try {
                $pathMajorMinor = Get-PythonMajorMinor @("python")
            } catch {
                $pathMajorMinor = ""
            }
            if ($pathMajorMinor -eq $majorMinor) {
                return @("python")
            }
        }
        if (Test-Command "py") {
            if ($majorMinor) {
                & py "-$majorMinor" -c "pass" 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    return @("py", "-$majorMinor")
                }
                Write-Info "warning: python $majorMinor of the workflow is not found: using py -3"
            }
            return @("py", "-3")
        }
    } elseif ($majorMinor -and (Test-Command "python$majorMinor")) {
        return @("python$majorMinor")
    } elseif (Test-Command "python3") {
        if ($majorMinor) { Write-Info "warning: python$majorMinor of the workflow is not found: using python3" }
        return @("python3")
    }
    if (Test-Command "python") {
        if ($majorMinor) { Write-Info "warning: python $majorMinor of the workflow is not found: using python" }
        return @("python")
    }
    throw "no python interpreter found (see --package-manager-name uv --install-package-manager)"
}

# major.minor version of a python interpreter
function Get-PythonMajorMinor([string[]]$python) {
    return Get-NativeOutput ($python + @("-c", 'import sys; print(''%d.%d'' % sys.version_info[:2])'))
}

# Version of an installed distribution, or nothing when it is not installed
function Get-DistributionVersion([string]$python, [string]$name) {
    $ErrorActionPreference = "Continue"
    try {
        return "$(& $python -c 'import importlib.metadata as m, sys; print(m.version(sys.argv[1]))' $name 2>$null)".Trim()
    } catch {
        return ""
    }
}

# =============================================================================
# Workflow requirements
# =============================================================================

# Value in the requirements of a workflow file: ewoks.version, ewoks.engine.name,
# ewoks.engine.version or python.version. The requirements are JSON, which can be
# embedded in another format like the XML of .ows files, or YAML.
function Get-RequirementValue([string]$content, [string]$key) {
    $value = Get-JsonRequirementValue $content $key
    if (-not $value) {
        $value = Get-YamlRequirementValue $content $key
    }
    return $value
}

# Value in JSON without a JSON parser. For example `ewoks.version` in
#
#   "ewoks": {"engine": {"name": "ewokscore", "version": "5.1.0"}, "version": "7.0.0"}
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
    # With the quotes that XML escapes
    $found = [regex]::Matches($content.Replace("&quot;", '"'), $pattern)
    if ($found.Count -eq 0) {
        return ""
    }
    return $found[$found.Count - 1].Groups[1].Value
}

# Value in YAML without a YAML parser: the last `key: value` line whose key path
# ends with requirements.<key>
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
        # Key path of this line, from the keys of the lines with less indentation
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

# =============================================================================
# Package managers
# =============================================================================

# Arguments of a '--package-manager-command' argument, split like `ewoks install` does
function Split-Command([string]$command) {
    if ($onWindows) {
        # Spaces escaped with a backslash are part of an argument
        return @([regex]::Split($command, '(?<!\\) ') | ForEach-Object { $_.Replace('\ ', ' ') } | Where-Object { $_ })
    }
    return @($command -split '\s+' | Where-Object { $_ })
}

# Executable as a '--package-manager-command' argument, quoted like `ewoks install`
# expects it
function Format-Command([string]$executable) {
    if ($onWindows) {
        return $executable.Replace(" ", "\ ")
    }
    if ($executable -match '^[A-Za-z0-9_./=:@%+,-]+$') {
        return $executable
    }
    return "'" + $executable.Replace("'", "'\''") + "'"
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

# Install a package manager in a directory with its official installer
function Install-Manager([string]$manager, [string]$directory) {
    if ($manager -eq "conda" -and $directory.Contains(" ")) {
        throw "Miniforge cannot be installed in a directory with spaces: $directory (see --bootstrap-dir)"
    }
    Write-Info "install $manager in $directory"
    if (Test-Path -LiteralPath $directory) {
        Remove-Item -LiteralPath $directory -Recurse -Force
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $directory) -Force | Out-Null
    # The PowerShell installers of uv and pixi only install Windows binaries
    # and exit their PowerShell session. Without `PSModulePath` the session of an
    # installer finds its own modules: Windows PowerShell 5.1 cannot load the
    # modules of PowerShell 7 when it is started from it.
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
                Invoke-NativeWithEnv @{ UV_INSTALL_DIR = (Join-Path $directory "bin"); UV_NO_MODIFY_PATH = "1"; PSModulePath = $null } ($runInstaller + @($installer))
            }
            "pixi" {
                $installer += $suffix
                Invoke-WebRequest -UseBasicParsing -Uri "https://pixi.sh/install$suffix" -OutFile $installer
                Invoke-NativeWithEnv @{ PIXI_HOME = $directory; PIXI_NO_PATH_UPDATE = "1"; PSModulePath = $null } ($runInstaller + @($installer))
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
                    # Only for this script: not on the PATH, no registry entries and no shortcuts.
                    # '/D' must be the last argument and must not be quoted.
                    $options = @("/S", "/InstallationType=JustMe", "/AddToPath=0", "/RegisterPython=0", "/NoRegistry=1", "/NoShortcuts=1", "/D=$directory")
                    $process = Start-Process -Wait -PassThru -FilePath $installer -ArgumentList $options
                    if ($process.ExitCode -ne 0) {
                        throw "the Miniforge installer failed with exit code $($process.ExitCode)"
                    }
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

# =============================================================================
# Steps of `Invoke-EwoksInstall`, which share the `$state` hashtable
# =============================================================================

# State with the options of this script and `Forwarded`: the other arguments,
# which are for `ewoks install`
function Read-Arguments([object[]]$arguments) {
    $state = @{
        Help = $false
        PrintCommand = $false
        InstallPackageManager = $false
        CustomRequirements = @()
        Root = Join-Path (Join-Path $HOME ".ewoks") "bootstrap"
        Manager = ""
        ManagerCommand = ""
        Workflow = ""
        Forwarded = @()
    }
    $i = 0
    while ($i -lt $arguments.Count) {
        $arg = [string]$arguments[$i]
        $i++
        if ($arg -in @("-h", "--help")) {
            $state.Help = $true
            return $state
        } elseif ($arg -eq "--print-command") {
            $state.PrintCommand = $true
        } elseif ($arg -eq "--install-package-manager") {
            $state.InstallPackageManager = $true
        } elseif ($arg -eq "--bootstrap-requirement") {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $state.CustomRequirements += [string]$arguments[$i]
            $i++
        } elseif ($arg.StartsWith("--bootstrap-requirement=")) {
            $state.CustomRequirements += $arg.Substring($arg.IndexOf("=") + 1)
        } elseif ($arg -eq "--bootstrap-dir") {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $state.Root = [string]$arguments[$i]
            $i++
        } elseif ($arg.StartsWith("--bootstrap-dir=")) {
            $state.Root = $arg.Substring($arg.IndexOf("=") + 1)
        } elseif ($arg -in @("--package-manager-name", "--package-manager-command")) {
            if ($i -ge $arguments.Count) { throw "$arg requires a value" }
            $value = [string]$arguments[$i]
            $i++
            if ($arg -eq "--package-manager-name") {
                $state.Manager = $value
            } else {
                $state.ManagerCommand = $value
            }
            $state.Forwarded += @($arg, $value)
        } elseif ($arg.StartsWith("--package-manager-name=")) {
            $state.Manager = $arg.Substring($arg.IndexOf("=") + 1)
            $state.Forwarded += $arg
        } elseif ($arg.StartsWith("--package-manager-command=")) {
            $state.ManagerCommand = $arg.Substring($arg.IndexOf("=") + 1)
            $state.Forwarded += $arg
        } else {
            # The workflow is the first argument that is an existing file.
            # Its absolute path makes the printed commands work from any directory.
            if (-not $state.Workflow -and -not $arg.StartsWith("-") -and (Test-Path -LiteralPath $arg -PathType Leaf)) {
                $arg = (Resolve-Path -LiteralPath $arg).ProviderPath
                $state.Workflow = $arg
            }
            $state.Forwarded += $arg
        }
    }
    return $state
}

# Set `Manager` and `Command`: the command of the package manager as an array.
# `Command` is empty for pip-venv without '--package-manager-command'.
function Select-Manager([hashtable]$state) {
    $manager = $state.Manager.ToLower()
    if ($state.InstallPackageManager -and -not $manager) {
        throw "--install-package-manager requires --package-manager-name"
    }
    if (-not $manager) {
        if ($state.ManagerCommand) {
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
    if ($state.ManagerCommand) {
        $command = @(Split-Command $state.ManagerCommand)
    }
    if ($manager -in @("uv", "pixi", "conda", "poetry")) {
        if (-not $command) { $command = @($manager) }
    } elseif ($manager -ne "pip-venv") {
        throw "package manager '$manager' is not supported"
    }
    $state.Manager = $manager
    $state.Command = $command
}

# Set `PythonVersion` (major.minor), `Requirements` of the bootstrap environment,
# `Tag` (the name of the bootstrap environment without the python version) and, to
# check whether an existing bootstrap environment is up to date, `Version`, `Engine`
# and `EngineVersion`
function Read-WorkflowRequirements([hashtable]$state) {
    $content = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $state.Workflow))
    $state.PythonVersion = ""
    if ((Get-RequirementValue $content "python.version") -match '^(\d+\.\d+)') {
        $state.PythonVersion = $Matches[1]
    }

    # The `@` and `=` separators of the tag cannot be part of a distribution name or version
    $state.Version = ""
    $state.Engine = ""
    $state.EngineVersion = ""
    if ($state.CustomRequirements) {
        $state.Requirements = $state.CustomRequirements
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($state.Requirements -join " "))
        $state.Tag = "custom=" + (($hash[0..4] | ForEach-Object { $_.ToString("x2") }) -join "")
        return
    }

    $version = Get-RequirementValue $content "ewoks.version"
    $engine = Get-RequirementValue $content "ewoks.engine.name"
    $engineVersion = Get-RequirementValue $content "ewoks.engine.version"
    if (-not $engineVersion) {
        $engine = ""
    }
    if (-not $engine -and $state.Workflow.EndsWith(".ows")) {
        # Workflows saved before ewoks recorded the engine
        Write-Info "the workflow does not provide its engine: using the latest ewoksorange"
        $engine = "ewoksorange"
    }

    if ($version) {
        $requirements = @("ewoks==$version")
        $tag = "ewoks=$version"
    } else {
        Write-Info "the workflow does not provide the ewoks version: using the latest one"
        $requirements = @("ewoks>=7")
        $tag = "ewoks=latest"
    }
    if ($engineVersion) {
        $requirements += "$engine==$engineVersion"
        $tag = "$tag@$engine=$engineVersion"
    } elseif ($engine) {
        $requirements += $engine
        $tag = "$tag@$engine"
    }
    $state.Version = $version
    $state.Engine = $engine
    $state.EngineVersion = $engineVersion
    $state.Requirements = $requirements
    $state.Tag = $tag
}

# Install the package manager in the bootstrap directory when it is not installed.
# `ewoks install` needs it as well.
function Initialize-Manager([hashtable]$state) {
    if (-not $state.Command -or $state.ManagerCommand -or (Test-Command $state.Command[0])) {
        return
    }
    $manager = $state.Manager
    $managerDir = Join-Path (Join-Path $state.Root "package-managers") $manager
    $executable = Get-ManagerExecutable $manager $managerDir
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        if (-not $state.InstallPackageManager) {
            throw "$manager is not installed (see --install-package-manager)"
        }
        Install-Manager $manager $managerDir
        if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
            throw "cannot install $manager in $managerDir"
        }
    }
    $state.Command = @($executable)
    $state.Forwarded += @("--package-manager-command", (Format-Command $executable))
}

# Set `Python` and `Location`: the interpreter and directory of the bootstrap
# environment, which is created when it does not exist
function New-BootstrapEnvironment([hashtable]$state) {
    $manager = $state.Manager
    $command = $state.Command

    # pip-venv and poetry cannot provide a python version: the interpreter decides
    $pythonVersion = $state.PythonVersion
    $basePython = @()
    if ($manager -eq "pip-venv") {
        if (-not $command) {
            $command = @(Find-Python $pythonVersion)
            $state.Command = $command
        }
        $pythonVersion = Get-PythonMajorMinor $command
    } elseif ($manager -eq "poetry") {
        $basePython = @(Find-Python $pythonVersion)
        $pythonVersion = Get-PythonMajorMinor $basePython
    }

    $name = $state.Tag
    if ($pythonVersion) {
        $name = "$name@python=$pythonVersion"
    }
    $location = Join-Path (Join-Path $state.Root $manager) $name
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
    $state.Location = $location
    $state.Python = $python
    if (Test-Path -LiteralPath $python -PathType Leaf) {
        return
    }

    Write-Info "create the bootstrap environment $location"
    # A previous attempt failed
    if (Test-Path -LiteralPath $location) {
        Remove-Item -LiteralPath $location -Recurse -Force
    }
    New-Item -ItemType Directory -Path $location -Force | Out-Null
    $pythonSpec = "python"
    if ($pythonVersion) {
        $pythonSpec = "python=$pythonVersion"
    }
    switch ($manager) {
        "uv" {
            $create = $command + @("venv", "--quiet")
            if ($pythonVersion) { $create += @("--python", $pythonVersion) }
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
            $interpreter = Get-NativeOutput ($basePython + @("-c", "import sys; print(sys.executable)"))
            # Poetry uses an active virtual or conda environment instead of the one of the project.
            # Without its own python it runs the `python` command, which can be python 2.
            $variables = @{
                VIRTUAL_ENV = $null
                CONDA_PREFIX = $null
                POETRY_VIRTUALENVS_IN_PROJECT = "true"
                POETRY_VIRTUALENVS_USE_POETRY_PYTHON = "true"
            }
            Invoke-NativeWithEnv $variables ($command + @("-C", $location, "env", "use", $interpreter))
        }
        "pip-venv" {
            Invoke-Native ($command + @("-m", "venv", $location))
        }
    }
}

# Install the requirements in the bootstrap environment unless it has their pinned versions
function Install-BootstrapRequirements([hashtable]$state) {
    $python = $state.Python
    if ($state.Version -and ((Get-DistributionVersion $python "ewoks") -eq $state.Version)) {
        if (-not $state.Engine) {
            return
        }
        $installed = Get-DistributionVersion $python $state.Engine
        if ($installed -and (-not $state.EngineVersion -or $installed -eq $state.EngineVersion)) {
            return
        }
    }

    $requirements = $state.Requirements
    Write-Info "install $(Format-Arguments $requirements) in $($state.Location)"
    try {
        if ($state.Manager -eq "uv") {
            Invoke-Native ($state.Command + @("pip", "install", "--quiet", "--upgrade", "--python", $python) + $requirements)
        } else {
            Invoke-Native (@($python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--upgrade") + $requirements)
        }
    } catch {
        throw "cannot install $(Format-Arguments $requirements) (see --bootstrap-requirement)"
    }
}

# Run `ewoks install` in the bootstrap environment, or print the command
function Invoke-EwoksInstallCommand([hashtable]$state) {
    $install = @("-m", "ewoks", "install") + $state.Forwarded
    $command = "& " + (Format-Arguments (@($state.Python) + $install))
    if ($state.PrintCommand) {
        Write-Output $command
        return
    }
    # Printed by `ewoks install` before its summary
    $header = @(
        "Bootstrap environment"
        "  Python : $($state.Python)"
        "  Install: $command"
        "  Remove : Remove-Item -Recurse -Force $(Format-Argument $state.Location)"
    ) -join "`n"
    $previous = $env:EWOKS_INSTALL_SUMMARY_HEADER
    $env:EWOKS_INSTALL_SUMMARY_HEADER = $header
    try {
        $ErrorActionPreference = "Continue"
        & $state.Python @install
    } finally {
        # Not left in the PowerShell session that runs the script block
        $env:EWOKS_INSTALL_SUMMARY_HEADER = $previous
    }
}

# Explain how to install without this script
function Write-ManualRoute([hashtable]$state) {
    $python = "python"
    if ($state.PythonVersion) { $python = "python $($state.PythonVersion)" }
    Write-Info "the bootstrap failed. To install without this script:"
    Write-Info "  1. create a $python environment and run in it: pip install $(Format-Arguments $state.Requirements)"
    Write-Info "  2. run in that environment: python -m ewoks install $(Format-Arguments $state.Forwarded)"
}

function Invoke-EwoksInstall([object[]]$arguments) {
    $state = Read-Arguments $arguments
    if ($state.Help) {
        Write-Output $usage
        return
    }
    if (-not $state.Workflow) {
        Write-Info $usage
        throw "provide the file of the workflow (no existing file in the arguments)"
    }
    Select-Manager $state
    Read-WorkflowRequirements $state

    try {
        Initialize-Manager $state
        New-BootstrapEnvironment $state
        Install-BootstrapRequirements $state
    } catch {
        # An interruption is not caught
        Write-ManualRoute $state
        throw
    }
    Invoke-EwoksInstallCommand $state
}

Invoke-EwoksInstall $args
