from mpyc.runtime import mpc
import numpy as np
import traceback
import random


secnum = mpc.SecInt()


async def main():
    
    input=[]
    input2=[] 
    while len(input) < 64 or len(input2) < 64:
        if len(input) < 64:
            input.append(random.randint(1,400))
            input= list(set(input))
        if len(input2) < 64:
            input2.append(random.randint(1,400))
            input2= list(set(input2))
    x = list(map(secnum, input+input2))  # secret input
    async with mpc:
        x=mpc.input(x,0)
        mpc.random.shuffle(secnum, x)  # secret in-place random shuffle
        x = mpc.sorted(x)  # sort on absolute value
        for i in range(0,len(x),2):
            x[i]=mpc.if_else(x[i] == x[i + 1], x[i], 0)
            x[i+1]=secnum(0)
        mpc.random.shuffle(secnum, x)
        print('Sorted by absolute value:', await mpc.output(x))
    

if __name__ == '__main__':
    mpc.run(main())