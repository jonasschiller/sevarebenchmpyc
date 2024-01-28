# Bitwise operation for 1.000.000 leads to a system fautlt due to too much RAM usage
import numpy as np
from mpyc.runtime import mpc
async def main():
    size=1000000
    intarray=np.ones(size,dtype=int)
    secnum = mpc.SecInt(32)
    await mpc.start()
    test=secnum.array(intarray)
    mpc.input(test,0)
    await mpc.shutdown()
if __name__ == '__main__':
    mpc.run(main())