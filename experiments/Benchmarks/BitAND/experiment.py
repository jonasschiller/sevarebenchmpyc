import numpy as np
from mpyc.runtime import mpc
async def main():
    size=1000
    intarray=np.ones(size,np.int64)
    secnum = mpc.SecInt(1)
    await mpc.start()
    test=secnum.array(intarray)
    for i in range(size-1):
        mpc.and_(test[i],test[i])
        print(i)
    result= await mpc.output(mpc.and_(test[-1],test[-1]))
    await mpc.shutdown()
    print(result)
if __name__ == '__main__':
    mpc.run(main())