import numpy as np
from mpyc.runtime import mpc
async def main():
    # Securely multiply the arrays using mpyc
    await mpc.start()
    secarray=mpc.SecInt(32).array
    input=np.ones(100000,np.int32)
    intermed=mpc.np_divide(secarray(input),secarray(input))
    result = mpc.output(intermed[-1])
    await mpc.shutdown()
    print(await result)
if __name__ == '__main__':
    mpc.run(main())