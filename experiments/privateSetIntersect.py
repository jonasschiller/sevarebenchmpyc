from mpyc.runtime import mpc
import numpy
import traceback
secint=mpc.SecInt()

#bitonic sort from https://github.com/lschoe/mpyc/blob/master/demos/SecureSortingNetsExplained.ipynb
def bitonic_sort(up, x):
    if len(x) <= 1:
        return x
    else: 
        first = bitonic_sort(True, x[:len(x) // 2])
        second = bitonic_sort(False, x[len(x) // 2:])
        return bitonic_merge(up, first + second)

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


async def main():
    
    await mpc.start()
    x = list(map(secint, [2, 4, 3, 5, 6, 1, 7, 8]))
    try:
        print(mpc.output(bitonic_sort(True, x)))
    except:
        traceback.print_exc()
    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())