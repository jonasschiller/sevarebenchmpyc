import sys
import subprocess
import numpy as np
import re

if len(sys.argv) != 3:
    print("Usage: python verify.py <player> <parties>")
    sys.exit(1)
# Get the parameters from the command line arguments
n_parties = int(sys.argv[2])

array = np.empty((n_parties,), dtype=object)

# Run the bash script
for i in range(0, n_parties):
    # Load the array
    file = '/root/servarebenchmpyc/Data/Input-P' + str(i) + '.txt'
    with open(file, 'r') as f:
        string = f.read()
        # Remove first three characters
        string = string[3:]
    array[i] = np.array([int(re.sub(r'[^0-9A-Fa-f]', '', x), 16) for x in string.split()])

for i in range(0,n_parties):
    result=result*array[i]

print(result)

    




    

