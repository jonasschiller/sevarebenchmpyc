from mpyc.runtime import mpc
# async def main():
#     m = len(mpc.parties)
#     data=[]
    
#     await mpc.start()
#     for i in range(1000):
#         data.append(mpc.input(mpc.SecInt(16)(i)))
#     for da in data:
#         print('m    =', await mpc.output(mpc.prod(da)))
#     await mpc.shutdown()

import numpy as np
import random

async def main():
    m = len(mpc.parties)
    data=[]
    
    await mpc.start()
    for i in range(10000):
        data.append(random.randint(0,1))
    
    secnum = mpc.SecFld(2)
    test1=mpc.input(secnum.array(np.array(data)),0)
    test2=mpc.input(secnum.array(np.array(data)),1)
    mpc.output(mpc.xor(test1,test2))
    await mpc.shutdown()
if __name__ == '__main__':
    mpc.run(main())