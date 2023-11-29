#!/bin/bash

REPO_DIR=$(pos_get_variable repo_dir --from-global)
amount=1000
partysize=$2

echo "create tuple with base-size: $amount"
for i in $(seq 0 $((partysize-1))); do
    "$REPO_DIR"/helpers/inputgen.py -t "$amount" 65000 "$i" > Data/Input.txt
done