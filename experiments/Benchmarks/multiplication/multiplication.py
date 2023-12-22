from mpyc.runtime import mpc
import mpyc.gmpy as gmpy2
import numpy as np

async def main():
    # Securely multiply the arrays using mpyc
    secarray=mpc.SecInt(32).array
    input=np.zeros(100000,np.int64)
    await mpc.start()
    intermed=mpc.np_multiply(secarray(input),secarray(input))
    result = mpc.output(intermed[-1])
    await mpc.shutdown()
if __name__ == '__main__':
    mpc.run(main())