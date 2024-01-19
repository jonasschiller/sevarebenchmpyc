from mpyc.runtime import mpc
import mpyc.gmpy as gmpy2
import numpy as np

async def main():
    # Securely multiply the arrays using mpyc
    secarray=mpc.SecInt(32).array
    input=np.zeros(1000000,np.int32)
    await mpc.start()
    intermed=mpc.np_multiply(secarray(input),secarray(input))
    result = await mpc.output(intermed[-1])
    await mpc.shutdown()
if __name__ == '__main__':
    mpc.run(main())