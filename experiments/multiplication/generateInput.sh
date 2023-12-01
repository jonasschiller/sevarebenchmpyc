#!/bin/bash

REPO_DIR=$(pos_get_variable repo_dir --from-global)
amount=$1
partysize=$2
player=$3
data_path=$4

echo "create tuple with base-size: $amount"
touch Data/Input.txt
for ((i=0; i<=$partysize; i++))
do
    "$REPO_DIR"/helpers/inputgen.py -t "$amount" 65000 "$i" > "$4-P-$i".txt
done

