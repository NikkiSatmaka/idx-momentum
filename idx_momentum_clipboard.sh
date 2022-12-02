#!/usr/bin/env bash

source $HOME/mambaforge/etc/profile.d/conda.sh
conda activate $HOME/workspace/algotrading/idxmomentumbot/.env
python $HOME/workspace/algotrading/idxmomentumbot/app.py
read

