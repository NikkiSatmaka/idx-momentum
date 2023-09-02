#!/usr/bin/env bash

script="app.py"

# setup dir variables
project_dir="$HOME/workspace/algotrading/idxmomentumbot"

# activate micromamba environment
source "$project_dir/bin/micromamba_activate.sh"

python "$project_dir/$script"
read
