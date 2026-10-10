#!/bin/sh
# Install the python environment of an ewoks workflow with nothing but a package
# manager. For example
#
#   curl -LsSf https://ewoks.readthedocs.io/en/stable/ewoks-install.sh | sh -s -- demo.json --package-manager-name uv
#
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
EOF
}

say() {
    printf 'ewoks-install: %s\n' "$*" >&2
}

die() {
    say "error: $*"
    exit 1
}

# Value in the requirements of a workflow file, for example `ewoks.version`. The
# requirements are JSON, which can be embedded in another format, or YAML.
requirement_value() {
    value=$(json_requirement_value "$1" "$2")
    [ -n "$value" ] || value=$(yaml_requirement_value "$1" "$2")
    printf '%s' "$value"
}

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
    tr -d '\n\r' <"$1" | sed 's/&quot;/"/g' | sed -n "s/.*$pattern.*/\\$group/p"
}

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

# Version of an installed distribution, or nothing when it is not installed
distribution_version() {
    "$1" -c 'import importlib.metadata as m, sys; print(m.version(sys.argv[1]))' "$2" 2>/dev/null || true
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

# Python interpreter with this major.minor version, or the default one
find_python() {
    if [ -n "$1" ] && command -v "python$1" >/dev/null 2>&1; then
        printf 'python%s' "$1"
    elif command -v python3 >/dev/null 2>&1; then
        printf 'python3'
    else
        die "no python interpreter found"
    fi
}

# Download a URL to a file
download() {
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf -o "$2" "$1"
    elif command -v wget >/dev/null 2>&1; then
        wget -q -O "$2" "$1"
    else
        die "curl or wget is needed to download $1"
    fi
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
    say "install $1 in $2"
    rm -rf "$2"
    mkdir -p "$(dirname "$2")"
    # The Miniforge installer requires the '.sh' suffix
    installer_dir=$(mktemp -d)
    installer=$installer_dir/installer.sh
    case $1 in
        uv)
            download https://astral.sh/uv/install.sh "$installer"
            UV_INSTALL_DIR=$2/bin UV_NO_MODIFY_PATH=1 sh "$installer" >&2
            ;;
        pixi)
            download https://pixi.sh/install.sh "$installer"
            PIXI_HOME=$2 PIXI_NO_PATH_UPDATE=1 sh "$installer" >&2
            ;;
        poetry)
            download https://install.python-poetry.org "$installer"
            POETRY_HOME=$2 "$(find_python "")" "$installer" >&2
            ;;
        conda)
            system=$(uname -s)
            [ "$system" != Darwin ] || system=MacOSX
            download "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$system-$(uname -m).sh" "$installer"
            bash "$installer" -b -p "$2" >&2
            ;;
    esac
    rm -rf "$installer_dir"
}

# The whole script is parsed before it runs, which matters with `curl | sh`
main() {
    # --- Arguments: the bootstrap options are removed, the others are kept ---

    print_command=0
    install_package_manager=0
    # Quoted for the shell
    requirements=""
    root=$HOME/.ewoks/bootstrap
    manager=""
    manager_command=""
    workflow=""
    remaining=$#
    while [ "$remaining" -gt 0 ]; do
        arg=$1
        shift
        remaining=$((remaining - 1))
        case $arg in
            -h | --help)
                usage
                exit 0
                ;;
            --print-command)
                print_command=1
                continue
                ;;
            --install-package-manager)
                install_package_manager=1
                continue
                ;;
            --ewoks-requirement)
                [ "$remaining" -gt 0 ] || die "$arg requires a value"
                requirements="$requirements $(quote "$1")"
                shift
                remaining=$((remaining - 1))
                continue
                ;;
            --ewoks-requirement=*)
                requirements="$requirements $(quote "${arg#*=}")"
                continue
                ;;
            --bootstrap-dir)
                [ "$remaining" -gt 0 ] || die "$arg requires a value"
                root=$1
                shift
                remaining=$((remaining - 1))
                continue
                ;;
            --bootstrap-dir=*)
                root=${arg#*=}
                continue
                ;;
        esac
        set -- "$@" "$arg"
        case $arg in
            --package-manager-name | --package-manager-command)
                [ "$remaining" -gt 0 ] || die "$arg requires a value"
                value=$1
                shift
                remaining=$((remaining - 1))
                set -- "$@" "$value"
                if [ "$arg" = --package-manager-name ]; then
                    manager=$value
                else
                    manager_command=$value
                fi
                ;;
            --package-manager-name=*)
                manager=${arg#*=}
                ;;
            --package-manager-command=*)
                manager_command=${arg#*=}
                ;;
            -*) ;;
            *)
                if [ -z "$workflow" ] && [ -f "$arg" ]; then
                    workflow=$arg
                fi
                ;;
        esac
    done

    if [ -z "$workflow" ]; then
        usage >&2
        die "provide the file of the workflow"
    fi

    # --- Package manager ---

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
        pip-venv) cmd=${manager_command:-} ;;
        *) die "package manager '$manager' is not supported" ;;
    esac

    # `ewoks install` needs the package manager this script installed
    if [ -n "$cmd" ] && [ -z "$manager_command" ] && ! command -v "$cmd" >/dev/null 2>&1; then
        manager_dir=$root/package-managers/$manager
        cmd=$(manager_executable "$manager" "$manager_dir")
        if [ ! -x "$cmd" ]; then
            [ "$install_package_manager" = 1 ] ||
                die "$manager is not installed (see --install-package-manager)"
            install_manager "$manager" "$manager_dir"
            [ -x "$cmd" ] || die "cannot install $manager in $manager_dir"
        fi
        set -- "$@" --package-manager-command "$cmd"
    fi

    # --- Ewoks, engine and python versions of the workflow requirements ---

    version=$(requirement_value "$workflow" ewoks.version)
    engine=$(requirement_value "$workflow" ewoks.engine.name)
    engine_version=$(requirement_value "$workflow" ewoks.engine.version)
    python_version=$(requirement_value "$workflow" python.version)
    python_major_minor=$(printf '%s' "$python_version" | sed -n 's/^\([0-9]*\.[0-9]*\).*/\1/p')
    [ -n "$engine_version" ] || engine=""

    # The bootstrap environment of pinned requirements is up to date when it has their versions
    pinned=0
    if [ -n "$requirements" ]; then
        tag=custom-$(printf '%s' "$requirements" | cksum | cut -d ' ' -f 1)
    elif [ -n "$version" ]; then
        pinned=1
        tag=$version
        requirements=$(quote "ewoks==$version")
        if [ -n "$engine" ]; then
            tag=$tag-$engine-$engine_version
            requirements="$requirements $(quote "$engine==$engine_version")"
        fi
    else
        say "the workflow does not provide the ewoks version: using the latest one"
        tag=latest
        requirements=$(quote "ewoks>=7")
    fi
    requirements=${requirements# }

    # pip-venv and poetry cannot provide a python version: the interpreter decides
    case $manager in
        pip-venv)
            if [ -z "$cmd" ]; then
                cmd=$(find_python "$python_major_minor")
            fi
            # shellcheck disable=SC2086
            python_major_minor=$($cmd -c 'import sys; print("%d.%d" % sys.version_info[:2])')
            ;;
        poetry)
            base_python=$(find_python "$python_major_minor")
            python_major_minor=$("$base_python" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
            ;;
    esac

    location=$root/$manager/ewoks-$tag${python_major_minor:+-python$python_major_minor}

    # --- Bootstrap environment ---

    case $manager in
        pixi) python=$location/.pixi/envs/default/bin/python ;;
        poetry) python=$location/.venv/bin/python ;;
        *) python=$location/bin/python ;;
    esac

    # shellcheck disable=SC2086
    if [ ! -x "$python" ]; then
        say "create the bootstrap environment $location"
        # A previous attempt failed
        rm -rf "$location"
        mkdir -p "$location"
        case $manager in
            uv)
                $cmd venv --quiet ${python_major_minor:+--python "$python_major_minor"} "$location" >&2
                ;;
            pixi)
                $cmd init "$location" >&2
                $cmd add --manifest-path "$location/pixi.toml" "python${python_major_minor:+=$python_major_minor}" pip >&2
                ;;
            conda)
                $cmd create --yes --quiet --prefix "$location" "python${python_major_minor:+=$python_major_minor}" pip >&2
                ;;
            poetry)
                printf '[tool.poetry]\npackage-mode = false\n\n[tool.poetry.dependencies]\npython = "*"\n' >"$location/pyproject.toml"
                interpreter=$("$base_python" -c 'import sys; print(sys.executable)')
                # Poetry uses an active virtual or conda environment instead of the one of the project.
                # Without its own python it runs the `python` command, which can be python 2.
                (
                    unset VIRTUAL_ENV CONDA_PREFIX
                    POETRY_VIRTUALENVS_IN_PROJECT=true POETRY_VIRTUALENVS_USE_POETRY_PYTHON=true \
                        $cmd -C "$location" env use "$interpreter" >&2
                )
                ;;
            pip-venv)
                $cmd -m venv "$location" >&2
                ;;
        esac
    fi

    up_to_date=0
    if [ "$pinned" = 1 ] && [ "$(distribution_version "$python" ewoks)" = "$version" ]; then
        if [ -z "$engine" ] || [ "$(distribution_version "$python" "$engine")" = "$engine_version" ]; then
            up_to_date=1
        fi
    fi

    if [ "$up_to_date" = 0 ]; then
        say "install $requirements in $location"
        # The requirements are quoted and `cmd` can have arguments
        if [ "$manager" = uv ]; then
            eval "\$cmd pip install --quiet --upgrade --python \"\$python\" $requirements" >&2 ||
                die "cannot install $requirements (see --ewoks-requirement)"
        else
            eval "\"\$python\" -m pip install --quiet --disable-pip-version-check --upgrade $requirements" >&2 ||
                die "cannot install $requirements (see --ewoks-requirement)"
        fi
    fi

    # --- ewoks install ---

    set -- "$python" -m ewoks install "$@"

    if [ "$print_command" = 1 ]; then
        command=""
        for arg in "$@"; do
            command="$command $(quote "$arg")"
        done
        printf '%s\n' "${command# }"
    elif [ ! -t 0 ] && (exec </dev/tty) 2>/dev/null; then
        # Confirmation prompts do not read stdin, which is this script with `curl | sh`
        exec "$@" </dev/tty
    else
        exec "$@"
    fi
}

main "$@"
