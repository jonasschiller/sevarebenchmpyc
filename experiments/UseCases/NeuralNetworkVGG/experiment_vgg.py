import os
import sys
import logging
import random
import gzip
import numpy as np
from mpyc.runtime import mpc
import time
import pickle
secnum = None


def scale_int(x, f2):
    return np.vectorize(round)(x * f2)


def load(name, f, a=2):
    W = np.load(os.path.join('data', 'vgg', 'W_' + name + '.npy'))
    if name.startswith('conv'):
        W = np.flip(W, axis=3)  # for use with np.convolve()
    b = np.load(os.path.join('data', 'vgg', 'b_' + name + '.npy'))
    if issubclass(secnum, mpc.SecureInteger):
        W = secnum.array(scale_int(W, 1 << f))
        b = secnum.array(scale_int(b, 1 << (a * f)))
    else:
        W = secnum.array(W, integral=False)
        b = secnum.array(b, integral=False)
    return W, b


@mpc.coroutine
async def convolvetensor(x, W, b):
    # 2D convolutions on (m,n)-shape images from x with (s,s)-shape filters from W.
    # b is a vector of dimension v
    stype = type(x)
    k, r, m, n = x.shape
    v, r, s, s = W.shape
    shape = (k, v, m, n)
    if issubclass(stype, mpc.SecureIntegerArray):
        rettype = (stype, shape)
    else:
        rettype = (stype, x.integral and W.integral and b.integral, shape)
    await mpc.returnType(rettype)
    x, W, b = await mpc.gather(x, W, b)
    x, W, b = x.value, W.value, b.value
    smaller = False
    if (m, n) < (s, s):
        smaller = True
        help=x
        x = np.zeros((k, r, s, s), dtype=object)
        x[:, :, :m, :n] = help
        store_m, store_n = m, n
        m, n = s, s
        shape = (k, r, m, n)
        print(x.shape)
    Y = np.zeros(shape, dtype=object)    
    s2 = (s-1) // 2
    for i in range(k):
        for j in range(v):
            Z = np.empty((m, n), dtype=object)
            for l in range(r):
                for I in range(m):
                    i_s2 = I - s2
                    Z[I] = sum(np.convolve(x[i, l, i_d], W[j, l, i_d - i_s2], mode='same')
                                for i_d in range(max(0, i_s2), min(i_s2+s, m)))
                Y[i, j] += Z
    if smaller:
        m, n = store_m, store_n
        Y = Y[:, :, :m, :n]
        shape = (k, v, m, n)
        print(Y.shape)
    Y += b[:, np.newaxis, np.newaxis]
    Y = stype.sectype.field.array(Y)
    Y = mpc._reshare(Y)
    if issubclass(stype, mpc.SecureFixedPointArray):
        Y = mpc.np_trunc(stype(Y, shape=shape))
    return Y


def maxpool(x):
    # maxpooling (2,2)-squares in (m,n)-shape images from x with stride 2
    x = np.maximum(x[:, :, ::2, :], x[:, :, 1::2, :])  # m //= 2
    x = np.maximum(x[:, :, :, ::2], x[:, :, :, 1::2])  # n //= 2
    return x

def avgpool(x):
    # average pooling (2,2)-squares in (m,n)-shape images from x with stride 2
    x=x[:, :, ::2, :] + x[:, :, 1::2, :]
    x=x[:, :, :, ::2] + x[:, :, :, 1::2]
    x=mpc.np_multiply(x,0.25)
    return x

def unpickle(file):

    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

async def main():
    global secnum
    # sysargv[1] is used to determin the number of images to process as well as the type of secure number to use
    #if sysargv[1] is not provided, the default value is 1
    # if sysargv[1] is a fixed poijt number with .5 at the end fixed point values are used with 4 fractional bits and 10 integer bits
    # batch size is always number in front of decimal point
    k = 1 if len(sys.argv) == 1 else float(sys.argv[1])
    if k - int(k) == 0.5:
        secnum = mpc.SecFxp(12, 4)
    else:
        secnum = mpc.SecInt(37)
    batch_size = round(k - 0.01)

    await mpc.start()

    offset=16

    f = 6

    logging.info('--------------- INPUT   -------------')
    print(f'Type = {secnum.__name__}, range = ({offset}, {offset + batch_size})')
    # read batch_size labels and images at given offset
    # on local pc takes roughly 0.16 seconds could be optimized but not to important?
    starttime=time.time()
    df = unpickle('data/test_batch')
    d = df[b'labels'][offset:offset + batch_size]
    labels = list(map(int, d))
    print('Labels:', labels)
    df = unpickle('data/test_batch')
    d = df[b'data'][offset:offset+batch_size]
    
    endtime=time.time()
    print(f'Elapsed time for reading labels and images: {endtime-starttime}')
    
    x = np.array(d,np.ubyte)/ 255
    x = np.reshape(x, (batch_size, 3, 32, 32))
    if batch_size == 1:
        print(np.array2string(np.vectorize(lambda a: int(bool(a)))(x[0, 0]), separator=''))
    x = secnum.array(x, integral=False)
    
    
    logging.info('--------------- Block 1 -------------')
    W, b = load('block_1_0', f)
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-1')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_1_2', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    logging.info('- - - - - - - - maxpool - - - - - - -')
    x = maxpool(x)
    await mpc.barrier('after-layer-1')

    logging.info('--------------- Block 2 -------------')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_2_0', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-2')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_2_2', f, 3)
    x = convolvetensor(x, W, b)
    x = (x >= 0) * x
    logging.info('- - - - - - - - maxpool - - - - - - -')
    x = maxpool(x)
    
    await mpc.barrier('after-layer-2')
    
    logging.info('--------------- Block 3 -------------')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_3_0', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-1')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_3_2', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_3_4', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    logging.info('- - - - - - - - maxpool - - - - - - -')
    x = maxpool(x)
    
    await mpc.barrier('after-layer-3')
    
    logging.info('--------------- Block 4 -------------')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_4_0', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-1')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_4_2', f, 3)
    x = convolvetensor(x, W, b)
    x = (x >= 0) * x
    await mpc.barrier('after-layer-1')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_4_4', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    logging.info('- - - - - - - - maxpool - - - - - - -')
    x = maxpool(x)
    
    await mpc.barrier('after-layer-4')
    
    logging.info('--------------- Block 5 -------------')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_5_0', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-1')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_5_2', f, 3)
    x = convolvetensor(x, W, b)
    x = (x >= 0) * x
    await mpc.barrier('after-layer-1')
    logging.info('- - - - - - - - conv2d  - - - - - - -')
    W, b = load('block_5_4', f, 3)
    x = convolvetensor(x, W, b)
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    logging.info('- - - - - - - - maxpool - - - - - - -')
    x = maxpool(x)
    print(x.shape)
    await mpc.barrier('after-layer-5')
    
    # Reshaping for Fully connected layer
    x = x.reshape(batch_size, 512)

    logging.info('--------------- LAYER 6 -------------')
    W, b = load('classifier_0', f, 4)
    logging.info('- - - - - - - - fc 512 x 4096  - - -')
    x = x @ W + b
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-6')
    
    logging.info('--------------- LAYER 7 -------------')
    W, b = load('classifier_2', f, 4)
    logging.info('- - - - - - - - fc 4096 x 4096  - - -')
    x = x @ W + b
    logging.info('- - - - - - - - ReLU    - - - - - - -')
    x = (x >= 0) * x
    await mpc.barrier('after-layer-7')

    logging.info('--------------- LAYER 8 -------------')
    W, b = load('classifier_4', f, 5)
    logging.info('- - - - - - - - fc 4096 x 10  - - - -')
    x = x @ W + b
    await mpc.barrier('after-layer-8')

    #using arg max and printing output
    for i in range(batch_size):
        prediction = int(await mpc.output(np.argmax(x[i])))
        error = '******* ERROR *******' if prediction != labels[i] else ''
        print(f'Image #{offset+i} with label {labels[i]}: {prediction} predicted. {error}')
        print(await mpc.output(x[i]))

    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())