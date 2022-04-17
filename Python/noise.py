
import numpy as np

def cyclic_noise(vec, size):

    n = len(vec)
    up = np.ndarray(n)
    down = np.ndarray(n)

    sm = 0
    for i in range(n):
        if i % size == 0:
            sm = 0
        sm += vec[i]
        up[i] = sm

    sm = 0
    for i in range(n-1, -1, -1):
        down[i] = sm
        sm += vec[i]
        if i % size == 0:
            sm = 0

    # to make work things when n is not multiple of size.
    # if a/b are crossing `last_in`, need to add `to_add`.
    last_in = ((n-1) // size) * size
    to_add = up[n-1]
    #print ','.join(str(x) for x in up)
    #print ','.join(str(x) for x in down)

    retv = np.ndarray(len(vec))
    lstep = (size+1)//2
    rstep = (size)//2
    even_size = ((size%2) == 0)

    for i in range(len(vec)):
        a = (i + n - lstep) % n
        b = (i + rstep) % n

        val = up[b] + down[a]
        if(a < last_in and a+size >= n):
            val += to_add
        if even_size:
            val += (vec[a]-vec[b])*0.5
        retv[i] = val

    return retv/size
