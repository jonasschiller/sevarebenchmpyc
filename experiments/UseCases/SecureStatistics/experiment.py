""" Demo for Secure Statistics

This basic demo is inspired by the MPYC tutorial
It is adapted by the author to be used in the context of this thesis
It loads in the data from files and then calculates
the average, the maximum, the minimum and the total sum of the data
"""


from mpyc.runtime import mpc
import numpy as np
import mpyc
import sys

async def main():
    if len(sys.argv) > 1:
        input_size = sys.argv[1]
    else:
        print("No argument provided.")
    
    secint = mpc.SecInt(32)
    secarray = secint.array
    data = np.ones(int(input_size), dtype=np.int32)
    data = secarray(data)
    await mpc.start()
    total_sum = mpc.sum(list(data))
    min_val, max_val = mpc.min_max(data)
    avg = mpyc.statistics.mean(list(data))

    print('Sum:', await mpc.output(total_sum))
    print('Maximum:', await mpc.output(max_val))
    print('Minimum:', await mpc.output(min_val))
    print('Average:', await mpc.output(avg))

    await mpc.shutdown()
    

mpc.run(main())