from mpyc.runtime import mpc
import numpy as np

async def main():
    intarray=np.ones(100000,np.int64)
    secnum = mpc.SecInt(32)
    # Securely multiply the arrays using mpyc
    await mpc.start()
    # Load the array
    a=secnum.array(intarray)
    intermed=mpc.np_less(a,a)
    result = await mpc.output(intermed[-1])
    await mpc.shutdown()
    print(result)
if __name__ == '__main__':
    mpc.run(main())