""" Demo for Secure Statistics

This basic demo is inspired by the MPYC tutorial
It is adapted by the author to be used in the context of this thesis
It loads in the data from files and then calculates
the average, the maximum, the minimum and the total sum of the data
"""


# This use case calculates secure statistics, namely min,max, mean and the sum in secure computation
# It uses the framework MPyC to do so
# The only parameter is the size of the input data
# Input is generated randomly and not secret shared but provided at compile time

from mpyc.runtime import mpc
import numpy as np
import mpyc
import sys

async def main():
    if len(sys.argv) > 1:
        input_size = int(sys.argv[1])
    else:
        print("No argument provided.")
    secarray=mpc.SecFxp(32,8).array
    input=secarray(np.ones(input_size,np.float32))
    await mpc.start()
    avg = mpyc.statistics.mean(list(input))

    print('Average:', await mpc.output(avg))

    await mpc.shutdown()
    

mpc.run(main())