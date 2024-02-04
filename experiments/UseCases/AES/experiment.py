"""Demo Threshold AES cipher.

From the authors of the MPyC framework
It performs a single AES-128 encryption using arithmetic secret sharing
and a threshold of 3 players. The players are numbered 0, 1, 2.
"""

import sys
from mpyc.runtime import mpc

secfld = mpc.SecFld(2**8)  # Secure AES field GF(2^8) for secret values.
f256 = secfld.field        # Plain AES field GF(2^8) for public values.


def circulant_matrix(r):
    """Circulant matrix with first row r."""
    r = list(map(f256, r))
    return [r[-i:] + r[:-i] for i in range(len(r))]


A = circulant_matrix([1, 0, 0, 0, 1, 1, 1, 1])   # 8x8 matrix A over GF(2)
A1 = circulant_matrix([0, 0, 1, 0, 0, 1, 0, 1])  # inverse of A
B = list(map(f256, [1, 1, 0, 0, 0, 1, 1, 0]))    # vector B over GF(2)
C = circulant_matrix([2, 3, 1, 1])               # 4x4 matrix C over GF(2^8)
C1 = circulant_matrix([14, 11, 13, 9])           # inverse of C


def sbox(x):
    """AES S-Box."""
    y = mpc.to_bits(x**254)
    z = mpc.matrix_prod([y], A, True)[0]
    w = mpc.vector_add(z, B)
    v = mpc.from_bits(w)
    return v


def sbox1(v):
    """AES inverse S-Box."""
    w = mpc.to_bits(v)
    z = mpc.vector_add(w, B)
    y = mpc.matrix_prod([z], A1, True)[0]
    x = mpc.from_bits(y)**254
    return x


def key_expansion(k):
    """AES key expansion for 128/256-bit keys."""
    w = list(map(list, zip(*k)))
    Nk = len(w)  # Nk is 4 or 8
    Nr = 10 if Nk == 4 else 14
    for i in range(Nk, 4*(Nr+1)):
        t = w[-1]
        if i % Nk in {0, 4}:
            t = [sbox(x) for x in t]
        if i % Nk == 0:
            a, b, c, d = t
            t = [b + (f256(1) << i // Nk - 1), c, d, a]
        w.append(mpc.vector_add(w[-Nk], t))
    K = [list(zip(*_)) for _ in zip(*[iter(w)]*4)]
    return K

def key_expansion_parallel(k,n):
    """AES key expansion for 128/256-bit keys."""
    w = list(map(list, zip(*k)))
    Nk = len(w)  # Nk is 4 or 8
    Nr = 10 if Nk == 4 else 14
    for i in range(Nk, 4*(Nr+1)):
        t = w[-1]
        if i % Nk in {0, 4}:
            t = [sbox(x) for x in t]
        if i % Nk == 0:
            a, b, c, d = t
            t = [b + (f256(1) << i // Nk - 1), c, d, a]
        w.append(mpc.vector_add(w[-Nk], t))
    K = [list(zip(*_)) for _ in zip(*[iter(w)]*4)]
    K = [K for _ in range(n)]
    return K

def encrypt(K, s):
    """AES encryption of s given key schedule K."""
    Nr = len(K) - 1  # Nr is 10 or 14
    s = mpc.matrix_add(s, K[0])
    for i in range(1, Nr+1):
        s = [[sbox(x) for x in _] for _ in s]
        s = [s[j][j:] + s[j][:j] for j in range(4)]
        if i < Nr:
            s = mpc.matrix_prod(C, s)
        s = mpc.matrix_add(s, K[i])
    return s

def encrypt(K, s):
    """AES encryption of s given key schedule K."""
    Nr = len(K) - 1  # Nr is 10 or 14
    s = mpc.matrix_add(s, K[0])
    for i in range(1, Nr+1):
        s = [[sbox(x) for x in _] for _ in s]
        s = [s[j][j:] + s[j][:j] for j in range(4)]
        if i < Nr:
            s = mpc.matrix_prod(C, s)
        s = mpc.matrix_add(s, K[i])
    return s


def decrypt(K, s):
    """AES decryption of s given key schedule K."""
    Nr = len(K) - 1  # Nr is 10 or 14
    for i in range(Nr, 0, -1):
        s = mpc.matrix_add(s, K[i])
        if i < Nr:
            s = mpc.matrix_prod(C1, s)
        s = [s[j][-j:] + s[j][:-j] for j in range(4)]
        s = [[sbox1(x) for x in _] for _ in s]
    s = mpc.matrix_add(s, K[0])
    return s


async def xprint(text, s):
    """Print matrix s transposed and flattened as hex string."""
    s = list(map(list, zip(*s)))
    s = await mpc.output(sum(s, []))
    print(f'{text} {bytes(map(int, s)).hex()}')

import numpy as np
async def main():
    if len(sys.argv) > 1:
        input_size = int(sys.argv[1])
        #price_range = int(sys.argv[2])
    else:
        print("No argument provided.")
    
    await mpc.start()
    p = [[secfld(17 * (4*j + i)) for j in range(4)] for i in range(4)]
    k128 = [[secfld(4*j + i) for j in range(4)] for i in range(4)]
    K = key_expansion(k128)
    for i in range(input_size):
        encrypted = encrypt(K, p)
    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())