#!/bin/bash

REPO_DIR=$(pos_get_variable repo_dir --from-global)
set_size=$1
num_parties=$2
filepath=$3

echo "create random set with size: $set_size"
for ((i=0; i<num_parties; i++)); do
    "$REPO2_DIR"/helpers/inputgen.py -s "$set_size" $((set_size*2)) "$i" $filepath+"$i"+".txt"
done