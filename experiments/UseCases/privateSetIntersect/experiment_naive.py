import sys
import numpy as np
from mpyc.runtime import mpc

secint=mpc.SecInt(32)
async def main():               
    # Create market instance and test orders
    if len(sys.argv) > 1:
        input_size = int(sys.argv[1])
        #price_range = int(sys.argv[2])
    else:
        print("No argument provided.")
    start = 1  # Start range
    end = 10000  # End range
    input1 = np.array(np.random.permutation(np.arange(start, end+1))[:input_size],dtype=np.int32)  
    input2 = np.array(np.random.permutation(np.arange(start, end+1))[:input_size],dtype=np.int32)
    result = [0]*input_size
    print(input1.shape)
    print(result.__len__())
    await mpc.start() 
    
    input1 = mpc.input(secint.array(input1),0) # secret input
    input2 = mpc.input(secint.array(input2),0)  # secret input
    for i in range(0,len(input1)):
        comp=mpc.np_equal(input1[i],input2)
        sum=mpc.np_sum(comp)
        result[i]=mpc.if_else(sum>0,input1[i],0)
    
    for i in range(input_size):
        print(await mpc.output(result[i]))
    await mpc.shutdown()
    
       
if __name__ == '__main__':
    mpc.run(main())