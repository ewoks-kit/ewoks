#!/bin/bash


function show_help {
  echo "
        Deploy projects on pypi from gitlab artifacts

        Usage: ./deploy.sh project [-h] [-n|--namespace name]
        project         Project to be deployed.
        -n|--namespace  Gitlab namespace of the project
        -h              Help
       "
}


function download_assets {
    local gitlab="https://gitlab.esrf.fr"
    local project="$1"
    local outdir="$2"
    local namespace="$3"
    if [[ -z $namespace ]]; then
        if [[ $project == "ewoks"* ]]; then
            namespace="workflow/ewoks"
        else
            namespace="workflow"
        fi
    fi
    local refs="main"
    local job="assets"

    local datafile=$outdir/assets.zip
    local url="$gitlab/$namespace/$project/-/jobs/artifacts/$refs/download?job=$job"
    rm -rf $outdir
    mkdir -p $outdir

    echo ""
    echo "Download assets:"
    echo "$url"
    curl -s -o $datafile -L $url

    if [ ! -f $datafile ];then
        echo "Could not download the assets to deploy !!!"
        return
    fi
    unzip $datafile -d $outdir > /dev/null 2>&1
}


function latest_pypi_version {
    local project="$1"
    local line=$(python3 -m pip index versions $project --pre)

    local regex="$project \(([^\(\)]+)\)"
    if [[ $line =~ $regex ]]
    then
        echo "${BASH_REMATCH[1]}"
    fi
}


function asset_version {
    local deploydir="$1"
    local filename=$(ls $deploydir)

    local regex="$project-(.+?).tar.gz"
    if [[ $filename =~ $regex ]]
    then
        echo "${BASH_REMATCH[1]}"
    fi
}


function yesno {
    read -p "$1 (y/N)?" choice
    case "$choice" in 
    y|Y ) echo "yes";;
    n|N ) echo "no";;
    * ) echo "no";;
    esac
}


function deploy {
    local project="$1"
    local namespace="$2"
    echo ""
    echo "Deploy project: $project"

    local deployroot="/tmp/deploy/$project"
    local deploydir="$deployroot/assets"
    download_assets $project $deployroot $namespace
    if [ ! -d "$deploydir" ];then
        echo "Failed to download the assets to deploy"
        return
    fi

    echo ""
    echo "Manual deployment:"
    echo "twine upload -r testpypi --sign $deploydir/*"
    echo "twine upload -r pypi --sign $deploydir/*"

    local v1=$(latest_pypi_version $project)
    local v2=$(asset_version $deploydir)
    echo ""
    echo "Latest version on pypi: $v1"
    echo "Version to deploy: $v2"
    if [ $v1 == $v2 ];then
        return
    fi

    echo ""
    if [ $(yesno "Deploy version $v2 in pypi") == "no" ];then
        return
    fi

    twine upload -r pypi --sign $deploydir/*
}


function main {
    local project
    local namespace

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
        show_help
        return
        ;;
        -n|--namespace)
        namespace="$2"
        shift # past argument
        shift # past value
        ;;
        -*|--*)
        echo "Unknown option $1"
        exit 1
        ;;
        *)
        POSITIONAL_ARGS+=("$1") # save positional arg
        shift # past argument
        ;;
    esac
    done

    project=${POSITIONAL_ARGS[0]}

    if [ -z $project ];then
        show_help
        return
    fi

    deploy $project $namespace
}


main $@
