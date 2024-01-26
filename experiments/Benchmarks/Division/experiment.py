import numpy as np
from mpyc.runtime import mpc
import mpyc.gmpy as gmpy2
async def main():
    # Securely multiply the arrays using mpyc
    await mpc.start()
    secarray=mpc.SecFxp(32,8).array
    size=10
    input=secarray(np.ones(size,np.int32))
    for i in range(size):
        intermed=mpc.np_divide(input[i],input[i])
    result = await mpc.output(intermed[-1])
    print(result)
    await mpc.shutdown()
if __name__ == '__main__':
    mpc.run(main())