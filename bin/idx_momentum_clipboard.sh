#!/usr/bin/env bash

script="app.py"

# setup dir variables
project_dir="$(dirname "$(dirname "$(realpath "$0")")")"

pixi run --manifest-path="$project_dir/pixi.toml" "$project_dir/$script"
