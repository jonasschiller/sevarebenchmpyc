#!/bin/bash

REPO2_DIR=$(pos_get_variable repo2_dir --from-global)
set_size=$1
num_parties=$2

echo "create random set with size: $set_size"
for ((i=0; i<num_parties; i++)); do
    "$REPO2_DIR"/helpers/inputgen.py -s "$set_size" $((set_size*2)) "$i" > Input-P"$i"
done