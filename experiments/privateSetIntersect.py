from mpyc.runtime import mpc
import numpy as np
import traceback
import random

secint=mpc.SecInt()

def bitonic_merge(up, x): 
    # assume input x is bitonic, and sorted list is returned 
    if len(x) == 1:
        return x
    else:
        bitonic_compare(up, x)
        first = bitonic_merge(up, x[:len(x) // 2])
        second = bitonic_merge(up, x[len(x) // 2:])
        return first + second

def bitonic_compare(up, x):
    dist = len(x) // 2
    up = secint(up)                                    # convert public Boolean up into `secint` bit 
    for i in range(dist):
        b = (x[i] > x[i + dist]) ^ ~up                 # secure xor of comparison bit and negated up
        d = b * (x[i + dist] - x[i])                   # d = 0 or d = x[i + dist] - x[i]
        x[i], x[i + dist] = x[i] + d, x[i + dist] - d  # secure swap

async def find_intersect(x):
    # identify all elements in x that are equal to the next element
    # assume x is sorted
    result = mpc.seclist([],secint)
    for i in range(len(x) - 1):
        result.append( x[i] * (x[i] == x[i + 1]) )
    mpc.if_else(x[i]==x[i+1],x[i],None)    

async def main():
    
    await mpc.start()
    input=[]
    input2=[] 
    while len(input) < 64 or len(input2) < 64:
        if len(input) < 64:
            input.append(random.randint(1,1000))
            input= list(set(input))
        if len(input2) < 64:
            input2.append(random.randint(1,1000))
            input2= list(set(input2))
    input.sort()
    input2.sort(reverse=True)
    x = list(map(secint,input))  # Sort the input list in ascending order
    y = list(map(secint, input2))
    try:
        print(await mpc.output(await find_intersect(bitonic_merge(True, x+y))))
    except:
        traceback.print_exc()
    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())