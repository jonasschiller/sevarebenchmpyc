from mpyc.runtime import mpc
import re
import numpy as np
import sys

async def main(participants):
    # Load the array
    for i in range(participants):
        with open('root/sevarebenchmpyc/experiments/Benchmarks/Input-P'+str(mpc.pid)+'.txt', 'r') as file:
            string = file.read()
            #Remove first three characters
            string = string[3:]
            input[0]=np.array([int(re.sub(r'[^0-9A-Fa-f]', '', x),16) for x in string.split()])
    # Securely multiply the arrays using mpyc
    result=input[0]
    for i in range(1,participants):
        result=input[i]*result
    with open('output_verification.txt', 'w') as file:
        file.write(str(result))

if __name__ == '__main__':
    participants = int(sys.argv[1])
    main(participants)