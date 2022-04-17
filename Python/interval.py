"""
Functions to work with intervals (only Newton remained for now, there used to be other stuff but it's obsolete)
"""

__all__ = ["interval_newton,NewtonException,func_range,func_range_with_der,newton_non_rigorous,bisection"]

class NoZeroException(Exception):
	pass

def interval_newton(f, fprime, I, alpha, epsilon, debug=False):
	"""
	Finds a smaller interval inside I where f(x)-alpha has a zero, i.e., when f(x)=alpha. 
	f is supposed to be monotonic. f and fprime must take and return intervals.

	Stops when (if) the interval has width smaller than epsilon.
	Raises ValueError (intersection of non-overlapping intervals) if the function can be proved
	to have no zero in the interval.
	Returns an interval containing I.lower() or I.upper() if the function *may* have no zero
	in the interval.
	"""
	intervalfield = I.parent()
	origI = I
	
	alpha = intervalfield(alpha)
	
	iterations = 0
	while I.absolute_diameter() > epsilon:
		iterations += 1
		if iterations > 100:
			raise ValueError('Interval Newton did not converge. Use higher precision?')
		m = intervalfield(I.center())
		intwith = m - (f(m)-alpha)/fprime(I)
		if intwith.lower() >= I.upper():
			return intervalfield(origI.upper())
		if intwith.upper() <= I.lower():
			return intervalfield(origI.lower())
		I = I.intersection(intwith)
	return I

def newton_non_rigorous(f, fprime, I, alpha, iterate=10, debug=False):
	"""
	Finds an interval of width epsilon where f(x)-alpha has a zero. f is supposed to be monotonic.
	f and fprime must take and return intervals.
	If alpha is not contained in f(I), returns [I.lower(), I.lower()] or [I.upper(), I.upper()]
	"""
	intervalfield = I.parent()
	
	alpha = intervalfield(alpha)
	
	iterations = 0
	origI = I
	
	alpha = intervalfield(alpha)
	
	iterations = 0
	while I.absolute_diameter() > epsilon:
		iterations += 1
		if iterations > 100:
			raise ValueError('Interval Newton did not converge. Use higher precision?')
		m = intervalfield(I.center())
		intwith = m - (f(m)-alpha)/fprime(I)
		if intwith.lower() >= I.upper():
			return intervalfield(origI.upper())
		if intwith.upper() <= I.lower():
			return intervalfield(origI.lower())
		I = I.intersection(intwith)
                
	return I

def bisection(f,I,alpha,epsilon):
	f_alpha=lambda x : f(x)-alpha
	intervalfield = I.parent()
	print(I.absolute_diameter(),epsilon)
	if (I.absolute_diameter()>epsilon):
		print("bisect")
		x_left,x_right = I.bisection()
		f_prod_left=(f_alpha(intervalfield(x_left.lower())))*(f_alpha(intervalfield(x_left.upper())))
		print(f_prod_left.endpoints())
		if (f_prod_left<=0):
			print("left", x_left.endpoints())
			I=bisection(f,x_left,alpha,epsilon)
		else:
			print("right",x_right.endpoints())
			I=bisection(f,x_right,alpha,epsilon)
	else:
		return I

def func_range(f,x,epsilon):
		if (x.absolute_diameter()>epsilon):
			x_left,x_right = x.bisection()
			a = func_range(f,x_left,epsilon)
			b = func_range(f,x_right,epsilon)
			return a.union(b)
		else:
			return f(x)

def func_range_with_der(f,f_prime,x,epsilon):
		#print(x.endpoints())
		IntervalField=x.parent()
		if (x.absolute_diameter()>epsilon):
			x_left,x_right = x.bisection()
			#print("x_left",x_left.endpoints(),"x_right", x_right.endpoints())
			a = func_range_with_der(f,f_prime,x_left,epsilon)
			b = func_range_with_der(f,f_prime,x_right,epsilon)
			return a.union(b)
		else:
			r=x.absolute_diameter()/2
			#print "r", r
			return f(IntervalField(x.center()))+f_prime(x)*IntervalField(-r,r)
