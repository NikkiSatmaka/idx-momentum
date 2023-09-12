#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# appoint user who has micromamba installed. if none, install using
# curl micro.mamba.pm/install.sh | bash
user="nikki"

micromamba_script="$HOME/micromamba/etc/profile.d/micromamba.sh"
micromamba_script_backup="/home/$user/micromamba/etc/profile.d/micromamba.sh"
env_dir="$(dirname $(dirname $(realpath $0)))/.conda_env"

# if user has micromamba installed, use it
# otherwise, set the user that has micromamba installed
if [[ -f $micromamba_script ]] ; then
    source $micromamba_script
else
    export MAMBA_EXE="/home/$user/.local/bin/micromamba";
    export MAMBA_ROOT_PREFIX="/home/$user/micromamba";
    source $micromamba_script_backup
fi

micromamba activate $env_dir
