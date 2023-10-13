#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# appoint user who has micromamba installed. if none, install using
# curl micro.mamba.pm/install.sh | bash
user="nikki"
env_dir=".conda_env"

micromamba_script="$HOME/micromamba/etc/profile.d/micromamba.sh"

# if user does not has micromamba installed
# set the user that has micromamba installed
if [[ ! -f $micromamba_script ]] ; then
    HOME="/home/$user"
    micromamba_script="$HOME/micromamba/etc/profile.d/micromamba.sh"
fi

env_dir="$(dirname $(dirname $(realpath $0)))/$env_dir"

export MAMBA_EXE="$HOME/.local/bin/micromamba";
export MAMBA_ROOT_PREFIX="$HOME/micromamba";
source $micromamba_script

micromamba activate $env_dir
