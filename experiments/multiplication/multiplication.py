from mpyc.runtime import mpc
import numpy as np
import re

async def main():
    # Load the array
    # Load the array
    i=mpc.pid
    file = '/root/servarebenchmpyc/Data/Input-P' + str(i) + '.txt'
    with open(file, 'r') as f:
        string = f.read()
        # Remove first three characters
        string = string[3:]
    array = np.array([int(re.sub(r'[^0-9A-Fa-f]', '', x), 16) for x in string.split()])
    result = np.array()
    # Securely multiply the arrays using mpyc
    await mpc.start()
    
    for t in len(array):
        result[i]=mpc.output(mpc.mult(mpc.input(mpc.SecInt(32)(array[i]))))
    await mpc.shutdown()
    print(result)
if __name__ == '__main__':
    mpc.run(main())