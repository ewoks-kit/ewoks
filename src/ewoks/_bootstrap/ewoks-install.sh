#!/bin/sh
# Install the python environment of an ewoks workflow with nothing but a package
# manager. For example
#
#   curl -LsSf https://ewoks.readthedocs.io/en/stable/ewoks-install.sh | sh -s -- demo.json --package-manager-name uv
#
# or download the script first
#
#   curl -LsSf -o ewoks-install.sh https://ewoks.readthedocs.io/en/stable/ewoks-install.sh
#   sh ewoks-install.sh demo.json --package-manager-name uv
#
# Steps (see `main` at the end):
#
#   1. Split the arguments in options of this script and arguments of `ewoks install`.
#   2. Select the package manager.
#   3. Read the ewoks, engine and python versions from the workflow requirements.
#   4. Create a bootstrap environment with that ewoks and engine, unless it exists.
#   5. Run `ewoks install` in the bootstrap environment.
#
# The bootstrap environments are cached in ~/.ewoks/bootstrap/<manager>/<name>
# where the name is, for example, `ewoks=7.0.0@ewokscore=5.1.0@python=3.12`.
set -eu

usage() {
    cat <<'EOF'
Usage: ewoks-install.sh [OPTIONS] WORKFLOW [ARGS ...]

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
EOF
}

# =============================================================================
# Helpers
# =============================================================================

say() {
    printf 'ewoks-install: %s\n' "$*" >&2
}

die() {
    say "error: $*"
    exit 1
}

# Argument quoted for the shell when needed
quote() {
    case $1 in
        '' | *[!A-Za-z0-9_./=:@%+,-]*)
            printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
            ;;
        *)
            printf '%s' "$1"
            ;;
    esac
}

# Arguments quoted for the shell and joined with spaces
quote_all() {
    for arg in "$@"; do
        printf '%s ' "$(quote "$arg")"
    done | sed 's/ $//'
}

# Absolute path of a file
absolute_path() {
    case $1 in
        /*) printf '%s' "$1" ;;
        *) printf '%s/%s' "$(pwd)" "$1" ;;
    esac
}

# Python interpreter with this major.minor version, or the default one
find_python() {
    if [ -n "$1" ] && command -v "python$1" >/dev/null 2>&1; then
        printf 'python%s' "$1"
    elif command -v python3 >/dev/null 2>&1; then
        [ -z "$1" ] || say "warning: python$1 of the workflow is not found: using python3"
        printf 'python3'
    else
        die "no python interpreter found (see --package-manager-name uv --install-package-manager)"
    fi
}

# major.minor version of a python interpreter
python_major_minor() {
    "$@" -c 'import sys; print("%d.%d" % sys.version_info[:2])'
}

# Version of an installed distribution, or nothing when it is not installed
distribution_version() {
    "$1" -c 'import importlib.metadata as m, sys; print(m.version(sys.argv[1]))' "$2" 2>/dev/null || true
}

# Download a URL to a file
download() {
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf -o "$2" "$1" || die "cannot download $1"
    elif command -v wget >/dev/null 2>&1; then
        wget -q -O "$2" "$1" || die "cannot download $1"
    else
        die "curl or wget is needed to download $1"
    fi
}

# =============================================================================
# Workflow requirements
# =============================================================================

# Value in the requirements of a workflow file: ewoks.version, ewoks.engine.name,
# ewoks.engine.version or python.version. The requirements are JSON, which can be
# embedded in another format like the XML of .ows files, or YAML.
requirement_value() {
    value=$(json_requirement_value "$1" "$2")
    [ -n "$value" ] || value=$(yaml_requirement_value "$1" "$2")
    printf '%s' "$value"
}

# Value in JSON without a JSON parser. For example `ewoks.version` in
#
#   "ewoks": {"engine": {"name": "ewokscore", "version": "5.1.0"}, "version": "7.0.0"}
json_requirement_value() {
    q="[\"']"
    s='[[:space:]]*'
    value="${q}$s:$s${q}\([^\"']*\)${q}"
    # The members of an object, which can contain objects themselves
    members='[^{}]*\({[^{}]*}[^{}]*\)*'
    case $2 in
        ewoks.version)
            pattern="${q}ewoks${q}$s:$s{$members${q}version$value" group=2
            ;;
        ewoks.engine.name)
            pattern="${q}ewoks${q}$s:$s{[^{}]*${q}engine${q}$s:$s{[^{}]*${q}name$value" group=1
            ;;
        ewoks.engine.version)
            pattern="${q}ewoks${q}$s:$s{[^{}]*${q}engine${q}$s:$s{[^{}]*${q}version$value" group=1
            ;;
        python.version)
            pattern="${q}python${q}$s:$s{[^{}]*${q}version$value" group=1
            ;;
    esac
    # On one line, with the quotes that XML escapes
    tr -d '\n\r' <"$1" | sed 's/&quot;/"/g' | sed -n "s/.*$pattern.*/\\$group/p"
}

# Value in YAML without a YAML parser: the last `key: value` line whose key path
# ends with requirements.<key>
yaml_requirement_value() {
    awk -v wanted="requirements.$2" -v sq="'" '
        {
            sub(/\r$/, "")
            if ($0 ~ /^[ \t]*(#|$)/) next
            # The dash of a list item belongs to the indentation of its first key
            match($0, /^[ -]*/)
            indent = RLENGTH
            rest = substr($0, indent + 1)
            if (rest !~ /^[A-Za-z0-9_]+:/) next
            key = rest
            sub(/:.*/, "", key)
            value = rest
            sub(/^[^:]*:[ \t]*/, "", value)
            # Key path of this line, from the keys of the lines with less indentation
            while (depth > 0 && indents[depth] >= indent) depth--
            depth++
            indents[depth] = indent
            keys[depth] = key
            path = keys[1]
            for (i = 2; i <= depth; i++) path = path "." keys[i]
            n = length(path) - length(wanted)
            if (value == "" || n < 0 || substr(path, n + 1) != wanted) next
            if (n > 0 && substr(path, n, 1) != ".") next
            gsub("^[\"" sq "]|[\"" sq "]$", "", value)
            found = value
        }
        END { printf "%s", found }
    ' "$1"
}

# =============================================================================
# Package managers
# =============================================================================

# Run the package manager command `cmd`, which is quoted for the shell like the
# '--package-manager-command' argument of `ewoks install`
run_manager() {
    eval "set -- $cmd \"\$@\""
    "$@"
}

# Executable of a package manager installed in a directory by this script
manager_executable() {
    case $1 in
        uv) printf '%s/bin/uv' "$2" ;;
        pixi) printf '%s/bin/pixi' "$2" ;;
        poetry) printf '%s/bin/poetry' "$2" ;;
        conda) printf '%s/bin/conda' "$2" ;;
    esac
}

# Install a package manager in a directory with its official installer
install_manager() {
    if [ "$1" = conda ]; then
        case $2 in
            *" "*) die "Miniforge cannot be installed in a directory with spaces: $2 (see --bootstrap-dir)" ;;
        esac
    fi
    say "install $1 in $2"
    rm -rf "$2"
    mkdir -p "$(dirname "$2")"
    # Removed by `on_exit` when the installation fails.
    # The Miniforge installer requires the '.sh' suffix.
    installer_dir=$(mktemp -d)
    installer=$installer_dir/installer.sh
    case $1 in
        uv)
            download https://astral.sh/uv/install.sh "$installer"
            UV_INSTALL_DIR=$2/bin UV_NO_MODIFY_PATH=1 sh "$installer" >&2 ||
                die "the uv installer failed"
            ;;
        pixi)
            download https://pixi.sh/install.sh "$installer"
            PIXI_HOME=$2 PIXI_NO_PATH_UPDATE=1 sh "$installer" >&2 ||
                die "the pixi installer failed"
            ;;
        poetry)
            download https://install.python-poetry.org "$installer"
            POETRY_HOME=$2 "$(find_python "")" "$installer" >&2 ||
                die "the poetry installer failed"
            ;;
        conda)
            system=$(uname -s)
            [ "$system" != Darwin ] || system=MacOSX
            download "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$system-$(uname -m).sh" "$installer"
            bash "$installer" -b -p "$2" >&2 ||
                die "the Miniforge installer failed"
            ;;
    esac
    rm -rf "$installer_dir"
    installer_dir=""
}

# =============================================================================
# Steps of `main`, which share their variables
# =============================================================================

# Set the options of this script and `forwarded`: the other arguments, which are
# for `ewoks install`, quoted for the shell
parse_arguments() {
    print_command=0
    install_package_manager=0
    custom_requirements="" # Quoted for the shell
    root=$HOME/.ewoks/bootstrap
    manager=""
    manager_command=""
    workflow=""
    forwarded=""
    while [ $# -gt 0 ]; do
        arg=$1
        shift
        case $arg in
            -h | --help)
                usage
                exit 0
                ;;
            --print-command)
                print_command=1
                ;;
            --install-package-manager)
                install_package_manager=1
                ;;
            --bootstrap-requirement)
                [ $# -gt 0 ] || die "$arg requires a value"
                custom_requirements="$custom_requirements $(quote "$1")"
                shift
                ;;
            --bootstrap-requirement=*)
                custom_requirements="$custom_requirements $(quote "${arg#*=}")"
                ;;
            --bootstrap-dir)
                [ $# -gt 0 ] || die "$arg requires a value"
                root=$1
                shift
                ;;
            --bootstrap-dir=*)
                root=${arg#*=}
                ;;
            --package-manager-name | --package-manager-command)
                [ $# -gt 0 ] || die "$arg requires a value"
                if [ "$arg" = --package-manager-name ]; then
                    manager=$1
                else
                    manager_command=$1
                fi
                forwarded="$forwarded $arg $(quote "$1")"
                shift
                ;;
            --package-manager-name=*)
                manager=${arg#*=}
                forwarded="$forwarded $(quote "$arg")"
                ;;
            --package-manager-command=*)
                manager_command=${arg#*=}
                forwarded="$forwarded $(quote "$arg")"
                ;;
            *)
                # The workflow is the first argument that is an existing file.
                # Its absolute path makes the printed commands work from any directory.
                if [ -z "$workflow" ] && [ -f "$arg" ]; then
                    arg=$(absolute_path "$arg")
                    workflow=$arg
                fi
                forwarded="$forwarded $(quote "$arg")"
                ;;
        esac
    done
    custom_requirements=${custom_requirements# }
    forwarded=${forwarded# }

    if [ -z "$workflow" ]; then
        usage >&2
        die "provide the file of the workflow (no existing file in the arguments)"
    fi
}

# Set `manager` and `cmd`: the command of the package manager, quoted for the shell.
# `cmd` is empty for pip-venv without '--package-manager-command'.
select_manager() {
    manager=$(printf '%s' "$manager" | tr '[:upper:]' '[:lower:]')
    if [ "$install_package_manager" = 1 ] && [ -z "$manager" ]; then
        die "--install-package-manager requires --package-manager-name"
    fi
    if [ -z "$manager" ]; then
        [ -z "$manager_command" ] || die "--package-manager-command requires --package-manager-name"
        for name in uv pixi conda poetry; do
            if command -v "$name" >/dev/null 2>&1; then
                manager=$name
                break
            fi
        done
        manager=${manager:-pip-venv}
    fi

    case $manager in
        uv | pixi | conda | poetry) cmd=${manager_command:-$manager} ;;
        pip-venv) cmd=$manager_command ;;
        *) die "package manager '$manager' is not supported" ;;
    esac
}

# Set `python_version` (major.minor), `requirements` of the bootstrap environment
# (quoted for the shell), `tag` (the name of the bootstrap environment without the
# python version) and, to check whether an existing bootstrap environment is up to
# date, `version`, `engine` and `engine_version`
read_workflow_requirements() {
    python_version=$(requirement_value "$workflow" python.version)
    python_version=$(printf '%s' "$python_version" | sed -n 's/^\([0-9]*\.[0-9]*\).*/\1/p')

    # The `@` and `=` separators of the tag cannot be part of a distribution name or version
    if [ -n "$custom_requirements" ]; then
        version=""
        engine=""
        requirements=$custom_requirements
        tag=custom=$(printf '%s' "$requirements" | cksum | cut -d ' ' -f 1)
        return
    fi

    version=$(requirement_value "$workflow" ewoks.version)
    engine=$(requirement_value "$workflow" ewoks.engine.name)
    engine_version=$(requirement_value "$workflow" ewoks.engine.version)
    [ -n "$engine_version" ] || engine=""
    if [ -z "$engine" ]; then
        case $workflow in
            *.ows)
                # Workflows saved before ewoks recorded the engine
                say "the workflow does not provide its engine: using the latest ewoksorange"
                engine=ewoksorange
                ;;
        esac
    fi

    if [ -n "$version" ]; then
        requirements=$(quote "ewoks==$version")
        tag=ewoks=$version
    else
        say "the workflow does not provide the ewoks version: using the latest one"
        requirements=$(quote "ewoks>=7")
        tag=ewoks=latest
    fi
    if [ -n "$engine" ]; then
        requirements="$requirements $(quote "$engine${engine_version:+==$engine_version}")"
        tag=$tag@$engine${engine_version:+=$engine_version}
    fi
}

# Install the package manager in the bootstrap directory when it is not installed.
# `ewoks install` needs it as well.
ensure_manager() {
    if [ -z "$cmd" ] || [ -n "$manager_command" ] || command -v "$cmd" >/dev/null 2>&1; then
        return
    fi
    manager_dir=$root/package-managers/$manager
    executable=$(manager_executable "$manager" "$manager_dir")
    if [ ! -x "$executable" ]; then
        [ "$install_package_manager" = 1 ] ||
            die "$manager is not installed (see --install-package-manager)"
        install_manager "$manager" "$manager_dir"
        [ -x "$executable" ] || die "cannot install $manager in $manager_dir"
    fi
    cmd=$(quote "$executable")
    forwarded="$forwarded --package-manager-command $(quote "$cmd")"
}

# Set `python`: the interpreter of the bootstrap environment, which is created when
# it does not exist
create_bootstrap_environment() {
    # pip-venv and poetry cannot provide a python version: the interpreter decides
    env_python_version=$python_version
    case $manager in
        pip-venv)
            [ -n "$cmd" ] || cmd=$(find_python "$python_version")
            env_python_version=$(python_major_minor run_manager)
            ;;
        poetry)
            base_python=$(find_python "$python_version")
            env_python_version=$(python_major_minor "$base_python")
            ;;
    esac

    location=$root/$manager/$tag${env_python_version:+@python=$env_python_version}
    case $manager in
        pixi) python=$location/.pixi/envs/default/bin/python ;;
        poetry) python=$location/.venv/bin/python ;;
        *) python=$location/bin/python ;;
    esac
    if [ -x "$python" ]; then
        return
    fi

    say "create the bootstrap environment $location"
    # A previous attempt failed
    rm -rf "$location"
    mkdir -p "$location"
    case $manager in
        uv)
            run_manager venv --quiet ${env_python_version:+--python "$env_python_version"} "$location" >&2
            ;;
        pixi)
            run_manager init "$location" >&2
            run_manager add --manifest-path "$location/pixi.toml" "python${env_python_version:+=$env_python_version}" pip >&2
            ;;
        conda)
            run_manager create --yes --quiet --prefix "$location" "python${env_python_version:+=$env_python_version}" pip >&2
            ;;
        poetry)
            printf '[tool.poetry]\npackage-mode = false\n\n[tool.poetry.dependencies]\npython = "*"\n' >"$location/pyproject.toml"
            interpreter=$("$base_python" -c 'import sys; print(sys.executable)')
            # Poetry uses an active virtual or conda environment instead of the one of the project.
            # Without its own python it runs the `python` command, which can be python 2.
            (
                unset VIRTUAL_ENV CONDA_PREFIX
                export POETRY_VIRTUALENVS_IN_PROJECT=true POETRY_VIRTUALENVS_USE_POETRY_PYTHON=true
                run_manager -C "$location" env use "$interpreter" >&2
            )
            ;;
        pip-venv)
            run_manager -m venv "$location" >&2
            ;;
    esac
}

# Install the requirements in the bootstrap environment unless it has their pinned versions
install_bootstrap_requirements() {
    if [ -n "$version" ] && [ "$(distribution_version "$python" ewoks)" = "$version" ]; then
        if [ -z "$engine" ]; then
            return
        fi
        installed=$(distribution_version "$python" "$engine")
        if [ -n "$installed" ] && [ "${engine_version:-$installed}" = "$installed" ]; then
            return
        fi
    fi

    say "install $requirements in $location"
    if [ "$manager" = uv ]; then
        eval "run_manager pip install --quiet --upgrade --python \"\$python\" $requirements" >&2 ||
            die "cannot install $requirements (see --bootstrap-requirement)"
    else
        eval "\"\$python\" -m pip install --quiet --disable-pip-version-check --upgrade $requirements" >&2 ||
            die "cannot install $requirements (see --bootstrap-requirement)"
    fi
}

# Run `ewoks install` in the bootstrap environment, or print the command
run_ewoks_install() {
    eval "set -- \"\$python\" -m ewoks install $forwarded"
    if [ "$print_command" = 1 ]; then
        quote_all "$@"
        printf '\n'
        return
    fi

    # Printed by `ewoks install` before its summary
    EWOKS_INSTALL_SUMMARY_HEADER=$(
        printf 'Bootstrap environment\n'
        printf '  Python : %s\n' "$python"
        printf '  Install: %s\n' "$(quote_all "$@")"
        printf '  Remove : rm -rf %s' "$(quote "$location")"
    )
    export EWOKS_INSTALL_SUMMARY_HEADER
    if [ ! -t 0 ] && (exec </dev/tty) 2>/dev/null; then
        # Confirmation prompts do not read stdin, which is this script with `curl | sh`
        exec "$@" </dev/tty
    fi
    exec "$@"
}

# Remove temporary files and, after a failure, explain how to install without this script
on_exit() {
    status=$?
    [ -z "$installer_dir" ] || rm -rf "$installer_dir"
    # Not after an interruption
    if [ "$status" != 0 ] && [ "$status" -lt 128 ] && [ "$explain_failure" = 1 ]; then
        say "the bootstrap failed. To install without this script:"
        say "  1. create a python${python_version:+ $python_version} environment and run in it: pip install $requirements"
        say "  2. run in that environment: python -m ewoks install $forwarded"
    fi
    exit "$status"
}

# The whole script is parsed before it runs, which matters with `curl | sh`
main() {
    installer_dir=""
    explain_failure=0
    trap on_exit EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM

    parse_arguments "$@"
    select_manager
    read_workflow_requirements

    explain_failure=1
    ensure_manager
    create_bootstrap_environment
    install_bootstrap_requirements
    run_ewoks_install
}

main "$@"
