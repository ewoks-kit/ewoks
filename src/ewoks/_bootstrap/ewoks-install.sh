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
EOF
}

say() {
    printf 'ewoks-install: %s\n' "$*" >&2
}

die() {
    say "error: $*"
    exit 1
}

# Version of an object in a JSON file, for example `"ewoks": {"version": "7.0.0"}`
json_version() {
    tr -d '\n\r' <"$1" | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*{[[:space:]]*\"version\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
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

# The whole script is parsed before it runs, which matters with `curl | sh`
main() {
    # --- Arguments: the bootstrap options are removed, the others are kept ---

    print_command=0
    requirement=""
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
            --ewoks-requirement)
                [ "$remaining" -gt 0 ] || die "$arg requires a value"
                requirement=$1
                shift
                remaining=$((remaining - 1))
                continue
                ;;
            --ewoks-requirement=*)
                requirement=${arg#*=}
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

    # --- Ewoks and python versions of the workflow requirements ---

    version=$(json_version "$workflow" ewoks)
    python_version=$(json_version "$workflow" python)
    python_minor=$(printf '%s' "$python_version" | sed -n 's/^\([0-9]*\.[0-9]*\).*/\1/p')

    if [ -n "$requirement" ]; then
        tag=custom-$(printf '%s' "$requirement" | cksum | cut -d ' ' -f 1)
    elif [ -n "$version" ]; then
        tag=$version
        requirement="ewoks==$version"
    else
        say "the workflow does not provide the ewoks version: using the latest one"
        tag=latest
        requirement="ewoks>=7"
    fi

    # pip-venv and poetry cannot provide a python version: the interpreter decides
    case $manager in
        pip-venv)
            if [ -z "$cmd" ]; then
                cmd=$(find_python "$python_minor")
            fi
            # shellcheck disable=SC2086
            python_minor=$($cmd -c 'import sys; print("%d.%d" % sys.version_info[:2])')
            ;;
        poetry)
            base_python=$(find_python "$python_minor")
            python_minor=$("$base_python" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
            ;;
    esac

    root=${EWOKS_BOOTSTRAP_DIR:-$HOME/.ewoks/bootstrap}
    location=$root/$manager/ewoks-$tag${python_minor:+-python$python_minor}

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
                $cmd venv --quiet ${python_minor:+--python "$python_minor"} "$location" >&2
                ;;
            pixi)
                $cmd init "$location" >&2
                $cmd add --manifest-path "$location/pixi.toml" "python${python_minor:+=$python_minor}" pip >&2
                ;;
            conda)
                $cmd create --yes --quiet --prefix "$location" "python${python_minor:+=$python_minor}" pip >&2
                ;;
            poetry)
                printf '[tool.poetry]\npackage-mode = false\n\n[tool.poetry.dependencies]\npython = "*"\n' >"$location/pyproject.toml"
                # Poetry uses an active virtual or conda environment instead of the one of the project
                (
                    unset VIRTUAL_ENV CONDA_PREFIX
                    POETRY_VIRTUALENVS_IN_PROJECT=true $cmd -C "$location" env use "$base_python" >&2
                )
                ;;
            pip-venv)
                $cmd -m venv "$location" >&2
                ;;
        esac
    fi

    installed=$("$python" -c 'import importlib.metadata as m; print(m.version("ewoks"))' 2>/dev/null || true)

    # shellcheck disable=SC2086
    if [ "$tag" != "$version" ] || [ "$installed" != "$version" ]; then
        say "install $requirement in $location"
        if [ "$manager" = uv ]; then
            $cmd pip install --quiet --upgrade --python "$python" "$requirement" >&2 ||
                die "cannot install $requirement (see --ewoks-requirement)"
        else
            "$python" -m pip install --quiet --disable-pip-version-check --upgrade "$requirement" >&2 ||
                die "cannot install $requirement (see --ewoks-requirement)"
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
