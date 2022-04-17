
import numpy
from math import sqrt

# computes the Wasserstein distance on the interval
def WassersteinDistInterval(vec):
    vsum, l1norm = reduce(lambda sr,x: (sr[0]+x,sr[1]+abs(sr[0])), vec, (0,0))
    assert abs(vsum)<0.00001, 'Wasserstein distance is only for zero-sum vectors!'
    return l1norm / len(vec)


# a non-cryptografied and commented version of the above function WassersteinDistInterval:
def WassersteinDistIntervalAlt(vec):
    # we need to compute the cumulated, that is the vector having all partials sums
    cumulated = []
    vsum = 0
    for x in vec:
        cumulated.append(vsum)
        vsum += x
    assert abs(vsum)<0.00001, 'Wasserstein distance is only for zero-sum vectors!'

    # compute the L1 norm of the cumulated vector
    l1norm = 0
    for x in cumulated:
        l1norm += abs(x)

    # return the value, scaled assuming the interval has length 1
    return l1norm / len(vec)


# a version computing the Wasserstein distance on the circle (that is, identifying [0,1) with S^1):
def WassersteinDistCircle(vec):
    # we need to compute the cumulated, that is the vector having all partials sums
    cumulated = []
    vsum = 0
    for x in vec:
        cumulated.append(vsum)
        vsum += x

    assert abs(vsum)<0.00001, 'Wasserstein distance is only for zero-sum vectors!'

    # for the wasserstein measure on the circle, compute the median
    median = numpy.median(cumulated)

    # compute the L1 norm of the cumulated vector
    return sum(abs(x-median) for x in cumulated) / len(vec)


# a version computing the Discrepancy on the circle (that is, identifying [0,1) with S^1):
def DiscrepancyCircle(vec):
    cumulated = []
    vsum = 0
    for x in vec:
        cumulated.append(vsum)
        vsum += x

    assert abs(vsum)<0.0001, 'Discrepancy is only for zero-sum vectors!'

    # for the wasserstein measure on the circle, compute the mean
    meann = numpy.mean(cumulated)

    # compute the L1 norm of the cumulated vector
    return sqrt(sum((x-meann)**2 for x in cumulated) / len(vec))
