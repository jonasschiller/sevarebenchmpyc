from mpyc.runtime import mpc
import re
import numpy as np

async def main():
    
    with open('/root/sevarebenchmpyc/experiments/Benchmarks/Input-P'+str(mpc.pid)+'.txt', 'r') as file:
        string = file.read()
    # Securely multiply the arrays using mpyc
    await mpc.start()
    input=np.array([int(re.sub(r'[^0-9A-Fa-f]', '', x),16) for x in string.split()])
    secnum = mpc.SecInt(32)
    secret_array=secnum.array(input)

    shared_test_1=mpc.input(secret_array,0)
    shared_test_2=mpc.input(secret_array,1)
    shared_test_3=mpc.input(secret_array,2)
    result = mpc.output(shared_test_1*shared_test_2*shared_test_3)
    await mpc.shutdown()
    with open('output.txt', 'w') as file:
        file.write(str(result))
if __name__ == '__main__':
    mpc.run(main())