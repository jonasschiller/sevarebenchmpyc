#!/bin/bash

REPO_DIR=$(pos_get_variable repo_dir --from-global)
amount=1000
partysize=$1
player=$2


echo "create tuple with base-size: $amount"
"$REPO_DIR"/helpers/inputgen.py -t "$amount" 65000 "$player" > Data/Input.txt