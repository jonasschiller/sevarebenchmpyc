""" Demo for Secure Statistics

This basic demo is inspired by the MPYC tutorial
It is adapted by the author to be used in the context of this thesis
It loads in the data from files and then calculates
the average, the maximum, the minimum and the total sum of the data
"""


from mpyc.runtime import mpc
import numpy as np
import mpyc

async def main():
    secint = mpc.SecInt(32)
    secarray = secint.array
    m = len(mpc.parties)
    data=np.zeros(10000,np.int32)
    await mpc.start()
    data=secarray(data)
    data=mpc.input(data,0)
    total_sum = mpc.sum(list(data))
    min,max = mpc.min_max(data)
    avg = mpyc.statistics.mean(list(data))

    print('Sum:', await mpc.output(total_sum) )
    print('Maximum:', await mpc.output(max))
    print('Minimum:', await mpc.output(min))
    print('Average', await mpc.output(avg))

    await mpc.shutdown()

mpc.run(main())