from mpyc.runtime import mpc
import re
import numpy as np

async def main():
    

    
    # Securely multiply the arrays using mpyc
    await mpc.start()
    # Load the array
    id=mpc.pid
    if id==0:
        with open('Input.txt', 'r') as file:
            string = file.read()
            #Remove first three characters
            string = string[4:]
    else:
        with open('Input0.txt', 'r') as file:
            string = file.read()
            #Remove first three characters
            string = string[4:]
    intarray=np.array([int(re.sub(r'[^0-9A-Fa-f]', '', x),16) for x in string.split()])
    intarray[0]=3
    secnum = mpc.SecInt(32)
    a=secnum.array(intarray)
    test=mpc.input(a,0)
    test2=mpc.input(a,1)
    result = mpc.output(test==test2)
    await mpc.shutdown()
    print(result)
if __name__ == '__main__':
    mpc.run(main())