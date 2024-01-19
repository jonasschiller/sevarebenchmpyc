import numpy as np
from mpyc.runtime import mpc
async def main():
    size=1000000
    intarray=np.ones(size,np.int64)
    secnum = mpc.SecInt(1)
    await mpc.start()
    test=secnum.array(intarray)
    for i in range(size-1):
        test[i]=mpc.and_(test[i],test[i])
    await mpc.shutdown()
if __name__ == '__main__':
    mpc.run(main())