import numpy as np
import random
from mpyc.runtime import mpc
async def main():
    m = len(mpc.parties)
    data=[]
    await mpc.start()
    for i in range(10000000):
        data.append(random.randint(0,1))
    secnum = mpc.SecFld(2)
    test1=mpc.input(secnum.array(np.array(data)),0)
    test2=mpc.input(secnum.array(np.array(data)),1)
    result=mpc.output(test1*test2)
    await mpc.shutdown()
    print(result)
if __name__ == '__main__':
    mpc.run(main())