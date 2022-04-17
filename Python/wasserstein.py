import numpy

def Cumulated(vec, expect_zero = True):
    cumulated = numpy.zeros(len(vec))
    vsum = 0
    for i in range(len(vec)):
        cumulated[i] = vsum
        vsum += vec[i]
    if expect_zero:
        assert abs(vsum)<0.00001, 'Expected zero-sum vectors!'
    return cumulated

def WassersteinInterval(vec):
    # we need to compute the cumulated, that is the vector having all partials sums
    cumulated = Cumulated(vec)

    # return the value, scaled assuming the interval has length 1
    return numpy.linalg.norm(cumulated,1) / len(vec)

# a version computing the Wasserstein distance on the circle (that is, identifying [0,1) with S1):
def WassersteinCircle(vec):
    # we need to compute the cumulated, that is the vector having all partials sums
    cumulated = Cumulated(vec)

    assert abs(vec[-1]+cumulated[-1])<0.00001, 'Wasserstein distance is only for zero-sum vectors!'

    # for the wasserstein measure on the circle, compute the median
    median = numpy.median(cumulated)

    # compute the L1 norm of the cumulated vector
    return sum(abs(x-median) for x in cumulated) / len(vec)

def PPWassersteinInterval(vec, p):
    # we need to compute the cumulated, that is the vector having all partials sums
    cumulated = Cumulated(vec)

    weight = 1.0  / len(vec)
    stack = []
    stackneg = False
    distance = 0

    
    for i in range(len(vec)):
        val = cumulated[i]
        isneg = val < 0
        cmpval = -val if stackneg else val
        while len(stack)>0 and stack[-1][0] > cmpval:
            islast = len(stack)==1 or stack[-2][0] < cmpval
            stepto = max(cmpval, 0) if islast else stack[-2][0]
            
            distance += ((stack[-1][0]-stepto) * (i-stack[-1][1])*weight)**p

            if islast and cmpval > 0:
                stack[-1] = (cmpval, stack[-1][1])
            else:
                stack.pop()

        if (len(stack)==0 or stack[-1][0] < cmpval) and val != 0:
            stackneg = isneg
            stack.append( (abs(val), i) )

    while len(stack)>0:
        stepto = 0 if len(stack)==1 else stack[-2][0]
        distance += ((stack[-1][0]-stepto) * (len(vec)-stack[-1][1])*weight)**p
        stack.pop()

    return distance

def PWassersteinInterval(vec, p):
    return PPWassersteinInterval(vec, p)**(1.0/p)

def PPWassersteinCircle(vec, p):
    # we need to compute the cumulated, that is the vector having all partials sums
    n = len(vec)
    weight = 1.0/n
    cumulated = Cumulated(vec)
    
    steps = sorted([(cumulated[i],i) for i in range(len(vec))])
    
    val, pos = steps.pop()
    intervals = [(pos, (pos+1)%n, 1), ((pos+1)%n, pos, (1-n))] #positive/negative

    prev_val = val
    distance = 0
    
    # to do: speed up using a dictionary
    while len(steps):
        val, pos = steps.pop()
        positive = sum(s**p for (_,_,s) in intervals if s>0)
        negative = sum((-s)**p for (_,_,s) in intervals if s<0)
        distance += (prev_val-val) * min(positive, negative) * weight
        prev_val = val
 
        res = None
        for i in range(len(intervals)):
            l,u,s = intervals[i]
            if l < u and l <= pos and pos < u:
                res = i
                break
            elif l > u and (l <= pos or pos < u):
                res = i
                break
        assert(res != None)
        resm1 = (res-1+len(intervals)) % len(intervals)
        resp1 = (res+1) % len(intervals)
        l,u,s = intervals[res]
        if (l+1) % n == u: #eliminate
            l1,u1,s1 = intervals[resm1]
            l2,u2,s2 = intervals[resp1]
            intervals[resm1] = (l1, u2, s1+s2+1)    # merge + 1(positive)

            del intervals[max(res,resp1)] #need to remove the two, this is the
            del intervals[min(res,resp1)] #only way to do so
        elif l == pos: #shrink left
            l1,u1,s1 = intervals[resm1]
            intervals[resm1] = (l1, (u1+1)%n, s1+1) # +1
            intervals[res] = ((l+1)%n, u, s+1)      # +1
        elif u == (pos+1)%n: #shrink right
            l2,u2,s2 = intervals[resp1]
            intervals[resp1] = ((l2-1+n)%n, u2, s2+1) # +1
            intervals[res] = (l, (u-1+n)%n, s+1)      # +1
        else: #split
            intervals[res] = ((pos+1)%n, u, -((u - (pos+1) + n)%n)) # negative
            intervals.insert(res, (pos, (pos+1)%n, 1) )            # 1(positive)
            intervals.insert(res, (l, pos, -((pos - l + n)%n)) )   # negative

    return distance

def PWassersteinCircle(vec, p):
    return PPWassersteinCircle(vec, p)**(1.0/p)