
import numpy, random

def mod(x,y):
    retv = x % y
    if retv<0: retv += y
    return retv

def Map(D, x):
    return D.quick_f(x)
    # return float(D.f(D.field(x)).center())

# this base class comes with the method `to_measure` and `initial_equidistributed`
class GridMeasureBase(object):
    """Base class for all discretizations where I have measure concentrated on a grid"""

    def __init__(self, D, N):
        self.D, self.N = D, N

    # start with a grid with all elements 1/N
    def initial_equidistributed(self):
        return numpy.ones(self.N)/float(self.N)

    # start with a grid with all elements 1/N
    def initial_random(self, distr):
        Mprec = len(distr)
        cumulated = []
        vsum = 0
        for x in distr:
            cumulated.append(vsum)
            vsum += x
        cumulated.append(vsum)
        cumulated = numpy.array(cumulated)

        inv_cumulated = []
        idx = 0
        for i in range(1,len(distr)+1):
            lev = cumulated[i]*Mprec
            while lev > idx:
                prev_lev = cumulated[i-1]*Mprec
                inv_cumulated.append( i + (idx - prev_lev) / (lev - prev_lev) )
                idx += 1
        if len(inv_cumulated) <= len(distr):
            inv_cumulated.append(Mprec)
        print('cm:',cumulated[-2:], Mprec)
        assert(len(inv_cumulated) == Mprec+1)
        inv_cumulated = numpy.array(inv_cumulated)

        retv = numpy.zeros(self.N)
        fact = 1.0/float(self.N)
        for i in range(self.N):
            rnum = random.random()*Mprec
            ridx = min(int(rnum), Mprec-1)
            rmod = rnum - ridx
            myidxM = inv_cumulated[ridx] + rmod*(inv_cumulated[ridx+1] - inv_cumulated[ridx])
            myidx = min(int(self.N * myidxM / Mprec), self.N-1)
            retv[myidx] += fact
        return retv

    # maps the values into the box they fall, filling the array meas
    def to_measure(self, vect, meas):
        meas.fill(0)
        M = len(meas)
        rat = M/float(self.N)
        for i in range(len(vect)):
            meas[int(i*rat)] += vect[i]


class OnceDecidedRandom(GridMeasureBase):
    """A once-randomized discretization of the map: for i such that i/N < f(x) < (i+1)/N,
    is chosen once and for all to be i/N with prob (i+1)-N*f(x) and (i+1)/N with proba N*f(x)-i.
    """

    color = 'orange'

    def __init__(self, D, N):
        super(type(self), self).__init__(D, N)
        self.once_random = None
        self.init_once_random()

    def init_once_random(self):
        self.once_random = numpy.zeros(self.N, numpy.int)

        iN = 1.0 / float(self.N)
        for x in range(self.N):
            y   = self.N * Map(self.D, x * iN)
            z   = int(random.random()<mod(y,1)) # 0 or 1 accordingly
            self.once_random[x] = mod(int(y)+z, self.N)

    # returns the state after one iteration
    def push_forward(self, vect, reuse = None):
        assert(len(vect) == self.N)
        if not reuse is None:
            assert(len(reuse) == self.N)
            reuse.fill(0)
            vectTemp = reuse
        else:
            vectTemp = numpy.zeros(self.N)

        if self.once_random is None:
            self.init_once_random()

        for x in range(0,self.N):
            try:
                idx = self.once_random[x]
                vectTemp[idx] += vect[x]
            except Exception as e:
                print('idx:',idx)
                raise e
        return vectTemp

class MapToCombination(GridMeasureBase):
    """measure on the grid is split: a delta_x is sent on the measure
      p*delta_{i/N} + (1-p)*delta_{(i+1)/N}, with i/N < f(x) < (i+1)/N, and p = (i+1)-N*f(x)
    """

    color = 'green'

    def __init__(self, D, N):
        super(type(self), self).__init__(D, N)

    def push_forward(self, vect, reuse = None):
        assert(len(vect) == self.N)
        if not reuse is None:
            assert(len(reuse) == self.N)
            reuse.fill(0)
            vectTemp = reuse
        else:
            vectTemp = numpy.zeros(self.N)

        for i in range(self.N):
            j = self.N * Map(self.D, i/float(self.N))
            j0 = int(j)
            fact1 = j-j0
            fact0 = 1-fact1
            j0 = mod(j0, self.N)
            j1 = mod(j0+1, self.N)
            vectTemp[j0] += fact0 * vect[i]
            vectTemp[j1] += fact1 * vect[i]
        return vectTemp


class MapToClosest(GridMeasureBase):
    """Sent to closest grid element"""

    color = 'blue'

    def __init__(self, D, N):
        super(type(self), self).__init__(D,N)

    def push_forward(self, vect, reuse = None):
        assert(len(vect) == self.N)
        if not reuse is None:
            assert(len(reuse) == self.N)
            reuse.fill(0)
            vectTemp = reuse
        else:
            vectTemp = numpy.zeros(self.N)

        iN = 1.0 / float(self.N)
        for x in range(self.N):
            val = mod(int(round(Map(self.D, x * iN) * self.N)), self.N)
            vectTemp[val] += vect[x]
        return vectTemp
    
    def get_map(self):
        iN = 1.0 / float(self.N)
        return numpy.array([mod(int(round(Map(self.D, x * iN) * self.N)), self.N)
                            for x in range(self.N)])


class StepwiseRandom(GridMeasureBase):
    """Sent to a random one between the two closest points"""

    color = 'cyan'

    def __init__(self, D, N):
        super(type(self), self).__init__(D,N)

    def push_forward(self, vect, reuse = None):
        assert(len(vect) == self.N)
        if not reuse is None:
            assert(len(reuse) == self.N)
            reuse.fill(0)
            vectTemp = reuse
        else:
            vectTemp = numpy.zeros(self.N)

        iN = 1.0 / float(self.N)
        for x in range(self.N):
            y   = self.N * Map(self.D, x * iN)
            z   = int(random.random()<mod(y,1)) # 0 or 1 accordingly
            val = mod(int(y)+z, self.N)
            vectTemp[val] += vect[x]
        return vectTemp

class PointSetBase(object):
    """Base class for all discretizations based on a set of points"""

    def __init__(self, D, N):
        self.D, self.N = D, N

    def initial_equidistributed(self, size = None):
        size = size or self.N
        return numpy.arange(size)/float(size)

    def to_measure(self, points, meas):
        meas.fill(0)
        M = len(meas)
        iN = 1.0/len(points)
        for i in range(len(points)):
            idx = mod(int(points[i]*M), M)
            meas[idx] += iN

class PointsRandomOnGrid(PointSetBase):
    """All points are travelling independently at random (that is, deltas are split)"""

    color = 'pink'

    def __init__(self, D, N):
        super(type(self), self).__init__(D, N)

    def push_forward(self, points, reuse = None):
        if not reuse is None:
            assert(len(reuse) == len(points))
            pointsTemp = reuse
        else:
            pointsTemp = numpy.ndarray(len(points))

        iN = 1.0 / float(self.N)
        for x in range(len(points)):
            y = self.N * Map(self.D, points[x])
            z = int(random.random()<mod(y,1))
            pointsTemp[x] = mod(int(y)+z, self.N) * iN

        return pointsTemp


class PointsPerturbed(PointSetBase):
    """All points are travelling independently outside any grid, with random perturbation of size 1/N"""

    color = 'red'

    def __init__(self, D, N):
        super(type(self), self).__init__(D, N)

    def push_forward(self, points, reuse = None):
        if not reuse is None:
            assert(len(reuse) == len(points))
            pointsTemp = reuse
        else:
            pointsTemp = numpy.ndarray(len(points))

        iN = 1.0 / float(self.N)
        for x in range(len(points)):
            pointsTemp[x] = mod(Map(self.D, points[x]) + random.triangular(-1, 0, 1) * iN, 1)

        return pointsTemp
