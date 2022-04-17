
import numpy as np
import random
import sys

class RandomDistribution:
    """A random number"""
    def __init__(self, distr):
        size = len(distr)
        cumulated = []
        vsum = 0
        for x in distr:
            cumulated.append(vsum)
            vsum += x*size
        cumulated.append(vsum) #0 to 1

        assert(abs(cumulated[-1] - size) < 0.01)

        cumulated = np.array(cumulated)
        inv_cumulated_idx = [] #compute inverse
        idx = 0

        # cumulated is considered as piecewise linear (distr was piecewise constant).
        # we find the inverse
        for i in range(size):
            lev = cumulated[i+1]
            while lev > idx:
                inv_cumulated_idx.append(i)
                idx += 1
        #print(len(inv_cumulated_idx),size)
        if len(inv_cumulated_idx) <= size:
            inv_cumulated.append(size)
        assert(len(inv_cumulated_idx) == size+1)

        self.size = size
        self.cumulated = cumulated
        self.inv_cumulated_idx = np.array(inv_cumulated_idx)

    def quantile_position(self, x):
        x = x * self.size
        xint  = int(x)
        xfrac = x-xint
        i = self.inv_cumulated_idx[xint]
        while self.cumulated[i+1] <= x:
            i+=1
        retv = i + (x - self.cumulated[i]) / (self.cumulated[i+1] - self.cumulated[i])
        return retv / self.size

    def generate(self):
        return self.quantile_position(random.random())
        return retv / self.size

    def generate_n_points(self, meas_prec, n):
        retv = np.zeros(meas_prec)
        val = 1.0 / n
        for i in range(n):
            x = self.quantile_position(random.random())
            retv[int(x * meas_prec)] += val
        return retv


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    if count == 0:
        return
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()
