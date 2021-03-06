#!/usr/bin/sage
# Time-stamp: <2019-05-11 14:33:45 lperrin>

# from sage.all import RealNumber, RDF, Infinity, exp, log, binomial, factorial, mq
from sage.all import *
from sage.crypto.boolean_function import BooleanFunction
import itertools
from collections import defaultdict

# Loading fast C++ implemented functions
from sboxu_cpp import *

from utils import *

# !SECTION! Wrapping C++ functions for differential/Walsh spectrum 

# Some constants
BIG_SBOX_THRESHOLD = 128
DEFAULT_N_THREADS  = 2

def walsh_spectrum(s, n_threads=None):
    if n_threads == None:
        if len(s) > BIG_SBOX_THRESHOLD:
            n_threads = DEFAULT_N_THREADS
        else:
            n_threads = 1
    return walsh_spectrum_fast(s, n_threads)


def differential_spectrum(s, n_threads=None):
    if n_threads == None:
        if len(s) > BIG_SBOX_THRESHOLD:
            n_threads = DEFAULT_N_THREADS
        else:
            n_threads = 1
    return differential_spectrum_fast(s, n_threads)

def lat_zeroes(s, n_threads=None):
    if n_threads == None:
        if len(s) > BIG_SBOX_THRESHOLD:
            n_threads = DEFAULT_N_THREADS
        else:
            n_threads = 1
    n = int(log(len(s), 2))
    return lat_zeroes_fast(s, n, n_threads)

def proj_lat_zeroes(s, n_threads=None):
    if n_threads == None:
        if len(s) > BIG_SBOX_THRESHOLD:
            n_threads = DEFAULT_N_THREADS
        else:
            n_threads = 1
    return projected_lat_zeroes_fast(s, n_threads)


def boomerang_spectrum(s, n_threads=None):
    if n_threads == None:
        if len(s) > BIG_SBOX_THRESHOLD:
            n_threads = DEFAULT_N_THREADS
        else:
            n_threads = 1
    return bct_spectrum_fast(s, n_threads)


def boomerang_uniformity(s):
    b = bct(s)
    boom_unif = 0
    for i in xrange(1, len(s)):
        for j in xrange(1, len(s)):
            boom_unif = max(boom_unif, b[i][j])
    return boom_unif


def dlct(s):
    n = int(log(len(s), 2))
    table = [[0 for b in xrange(0, 2**n)] for a in xrange(0, 2**n)]
    for delta in xrange(0, 2**n):
        for l in xrange(0, 2**n):
            table[delta][l] = sum((-1)**(scal_prod(l, oplus(s[x], s[oplus(x, delta)])))
                              for x in xrange(0, 2**n))
    return table



# !SECTION! Properties of functions and permutations

# !SUBSECTION! Probability distributions

def lat_coeff_probability_permutation(m, n, c):
    """Returns the probability that a coefficient of the Walsh spectrum of
    a random bijective permutation mapping m bits to n is equal, in
    absolute value, to c.

    If m != n, raises an error.

    """
    if m != n:
        raise "A permutation cannot map {} bits to {}!".format(m, n)
    if c % 4 != 0:
        return 0
    elif c == 0:
        return RealNumber(Integer(binomial(2**(n-1), 2**(n-2)))**2) / Integer(binomial(2**n, 2**(n-1)))
    else:
        c = c/2
        return RealNumber(2) * RealNumber(Integer(binomial(2**(n-1), 2**(n-2) + c/2))**2) / Integer(binomial(2**n, 2**(n-1)))

    
def lat_coeff_probability_function(m, n, c):
    """Returns the probability that a coefficient of the Walsh spectrum of
    a random function mapping m bits to n is equal, in absolute value, to
    c.

    If m != n, raises an error.

    """
    if m != n:
        raise "m (={}) should be equal to n (={})!".format(m, n)
    if c % 4 != 0:
        return 0
    if c == 0:
        return RealNumber(2) * RealNumber(2**(-2**n) * binomial(2**n, 2**(n-1)))
    else:
        c = c/2
        return RealNumber(4) * RealNumber(2**(-2**n) * binomial(2**n, 2**(n-1)+c))


def ddt_coeff_probability(m, n, c):
    """Returns the probability that a coefficient of the DDT of a S-Box
    mapping m bits to n is equal to c.

    This probability is identical for random a permutation and a
    random non-bijective function.

    """
    if c % 2 == 1:
        return 0
    else:
        d = c/2
        if m >= 5 and n-m <= m/4:
            k = 2**(m-n-1)
            return RealNumber(exp(-k) * k**d / factorial(d))
        else:
            return RealNumber(binomial(2**(m-1), d) * 2**(-n*d) * (1 - 2**-n)**(2**(m-1)-d))


def bct_coeff_probability(m, n, c):
    """Returns the probability that a coefficient of the BCT of an S-Box
    mapping m bits to n is equal to c.

    This probability is only defined for permutations. Thus, an error is raised if m != n.

    """
    if m != n:
        raise "the BCT is only defined when m==n"
    if c % 2 == 1:
        return RealNumber(0.0)
    B = RealNumber(2**(n-1))
    A = RealNumber(2**(2*n-2)-2**(n-1))
    # p = RealNumber(1.0/(2**n-1))
    p = 1/(2**n-1)
    q = p**2
    d = c/2
    result = RealNumber(0.0)
    base = RealNumber(2**n-1)**(B + 2*A)
    for j1, j2 in itertools.product(xrange(0, d+1), xrange(0, d+1)):
        if 2*j1 + 4*j2 == c:
            # added = Integer(binomial(B, j1)) * RealNumber(p**j1) * RealNumber((1-p)**(B-j1)) * Integer(binomial(A, j2)) * RealNumber(q**(j2) * (1-q)**(A-j2))
            added = RealNumber(binomial(B, j1)) * RealNumber((2**n-2)**(B-j1)) * RealNumber(binomial(A, j2)) * RealNumber((2**(2*n)-2**(n+1))**(A-j2))
            if added > 0 and added < Infinity:
                result += added / base
    return result

        
def expected_max_ddt(m, n):
    result = RealNumber(0.0)
    cumul = [0]
    for k in range(1, 15):
        to_add = sum(ddt_coeff_probability(m, n, 2*z) for z in xrange(0, k+1))
        to_add = to_add**RealNumber((2**m-1) * (2**n-1))
        cumul.append(to_add)
    result = []
    for i in xrange(1, len(cumul)):
        result.append(cumul[i] - cumul[i-1])
    return result


def expected_max_lat(m, n):
    result = RealNumber(0.0)
    cumul = [0]
    for k in range(1, 50):
        to_add = sum(lat_coeff_probability_permutation(m, n, 2*z) for z in xrange(0, k+1))
        to_add = to_add**RealNumber((2**m-1) * (2**n-1))
        cumul.append(to_add)
    result = []
    for i in xrange(1, len(cumul)):
        result.append(cumul[i] - cumul[i-1])
    return result

def expected_max_lat_function(m, n):
    result = RealNumber(0.0)
    cumul = [0]
    for k in range(1, 70):
        to_add = sum(lat_coeff_probability_function(m, n, z) for z in xrange(0, k+1))
        to_add = to_add**RealNumber((2**m) * (2**n))
        cumul.append(to_add)
    result = []
    for i in xrange(1, len(cumul)):
        result.append(cumul[i] - cumul[i-1])
    return result
    
    
# !SUBSECTION! Aggregated information from the tables

def probability_of_max_and_occurrences(m, n, v_max, occurrences, proba_func):
    """Returns the logarithm in base 2 of the probability that
    $(2^m-1)(2^n-1)$ trials of an experiment yielding output c with
    probability proba_func(m, n, c) will have a result equal to
    `v_max` at most `occurrences` times and be strictly smaller on all
    other trials.

    """
    p_strictly_smaller = sum(RealNumber(proba_func(m, n, i)) for i in xrange(0, v_max))
    p_equal = RealNumber(proba_func(m, n, v_max))
    result = RealNumber(0)
    n_trials = (2**m-1) * (2**n-1)
    for occ in reversed(xrange(0, occurrences+1)):
        added = RealNumber(binomial(n_trials, occ)) * (p_strictly_smaller)**((n_trials - occ)) * p_equal**(occ)
        if abs(added) < Infinity and added > 0 and (result + added > result):
            result += added
    return result


def anomaly_differential_uniformity(n, v_max):
    p_0 = RealNumber(ddt_coeff_probability(n, n, 0))
    p_non_zero = RealNumber(1-p_0)
    p_inf = RealNumber(sum(ddt_coeff_probability(n, n, c) for c in xrange(1, v_max+1)))
    proba_enough_zeroes_in_row = RealNumber(0.0)
    proba_bound_and_enough_zeroes = RealNumber(0.0)
    M = 2**(n-1)-1
    for i in xrange(2**(n-1)-1, 2**n-1):
        proba_enough_zeroes_in_row    += RealNumber(binomial(2**n-1, i)) * p_0**i * p_non_zero**(2**n-1-i)
        proba_bound_and_enough_zeroes += RealNumber(binomial(2**n-1, i)) * p_0**i * p_inf**(2**n-1-i)
    return (2**n-1)*float(log(proba_bound_and_enough_zeroes, 2) - log(proba_enough_zeroes_in_row, 2))

def anomaly_ddt(n, v_max, occ):
    p_0 = RealNumber(ddt_coeff_probability(n, n, 0))
    p_non_zero = RealNumber(1-p_0)
    p_inf = RealNumber(sum(ddt_coeff_probability(n, n, c) for c in xrange(1, v_max+1)))
    proba_enough_zeroes_in_row = RealNumber(0.0)
    proba_bound_and_enough_zeroes = RealNumber(0.0)
    M = 2**(n-1)-1
    for i in xrange(2**(n-1)-1, 2**n-1):
        proba_enough_zeroes_in_row    += RealNumber(binomial(2**n-1, i)) * p_0**i * p_non_zero**(2**n-1-i)
        proba_bound_and_enough_zeroes += RealNumber(binomial(2**n-1, i)) * p_0**i * p_inf**(2**n-1-i)
    return -(2**n-1)*float(log(proba_bound_and_enough_zeroes, 2) - log(proba_enough_zeroes_in_row, 2))
    

def table_anomaly(s, table):
    if table not in ["DDT", "LAT", "BCT"]:
        raise "The table-based anomaly is defined for the LAT, DDT and BCT. table={} is unknown.".format(table)
    else:
        spec = {}
        proba_func = None
        n = int(log(len(s), 2))
        if table == "DDT":
            spec = differential_spectrum(s)
            proba_func = ddt_coeff_probability
        elif table == "LAT":
            spec = walsh_spectrum(s)
            proba_func = lat_coeff_probability_permutation
        else:
            spec = boomerang_spectrum(s)
            proba_func = bct_coeff_probability
        v_max = 0
        occurrences = 0
        for k in spec.keys():
            if abs(k) == v_max:
                occurrences += spec[k]
            elif abs(k) > v_max:
                v_max = abs(k)
                occurrences = spec[k]
        return -float(log(probability_of_max_and_occurrences(n, n, v_max, occurrences, proba_func), 2))

    
def table_negative_anomaly(s, table):
    if table not in ["DDT", "LAT", "BCT"]:
        raise "The table-based negative anomaly is defined for the LAT, DDT and BCT. table={} is unknown.".format(table)
    else:
        spec = {}
        proba_func = None
        n = int(log(len(s), 2))
        if table == "DDT":
            spec = differential_spectrum(s)
            proba_func = ddt_coeff_probability
        elif table == "LAT":
            spec = walsh_spectrum(s)
            proba_func = lat_coeff_probability_permutation
        else:
            spec = boomerang_spectrum(s)
            proba_func = bct_coeff_probability
        v_max = 0
        occurrences = 0
        for k in spec.keys():
            if abs(k) == v_max:
                occurrences += spec[k]
            elif abs(k) > v_max:
                v_max = abs(k)
                occurrences = spec[k]
        p_anomaly = probability_of_max_and_occurrences(n, n, v_max, occurrences, proba_func)
        p_equal = proba_func(n, n, v_max)
        p_strictly_smaller = sum(proba_func(n, n, i) for i in xrange(0, v_max))
        card = (2**n-1)**2
        p_precise_equal = RealNumber(binomial(card, occurrences))*p_equal**occurrences*p_strictly_smaller**(card-occurrences)
        p_precise_equal = min(p_precise_equal, RealNumber(1.0))
        p_anomaly       = min(p_anomaly, RealNumber(1.0))
        return -float(log(p_precise_equal-p_anomaly+1, 2))



# def probability_of_goodness(s):
#     """Returns the probabilities that the distribution of the coefficients
#     in the DDT and the LAT of a random permutation are at least as
#     good as those of `s`.

#     The criteria used to define "goodness" is the maximum value in the
#     DDT (resp. LAT) and its number of occurrences. Smaller maximum
#     value is better and, given to S-Boxes with the same max value, a
#     smaller number of occurrences is better.

#     """
#     result = {}
#     n = int(log(len(s), 2))
#     # Looking at the DDT
#     diff = differential_spectrum(s)
#     uniformity = max(diff.keys())
#     uniformity_occurences = diff[uniformity]
#     result["differential"] = probability_of_measure(
#         n,
#         n,
#         uniformity,
#         uniformity_occurences,
#         ddt_coeff_probability)
#     # Looking at the LAT
#     w = walsh_spectrum(s)
#     linearity = max([abs(k) for k in w.keys()])
#     linearity_occurences = 0
#     if linearity in w.keys():
#         linearity_occurences += w[linearity]
#     if -linearity in w.keys():
#         linearity_occurences += w[-linearity]
#     result["linear"] = probability_of_measure(
#         n,
#         n,
#         linearity,
#         linearity_occurences,
#         lat_coeff_probability_permutation)
#     return result



def BP_criteria(s):
    """Returns the quantity used by Biryukov and Perrin to generate
    S-Boxes imitating the properties of the S-Box of Skipjack.

    """
    if not isinstance(s, mq.SBox):
        s = mq.SBox(s)
    lat = s.linear_approximation_matrix()
    result = 0
    for i, j in itertools.product(xrange(1, lat.nrows()),
                                  xrange(1, lat.ncols())):
        result += 2**(abs(lat[i, j]))
    return result


# def differential_uniformity(s):
#     if not isinstance(s, mq.SBox):
#         s = mq.SBox(s)
#     if is_permutation(s):
#         return max(differential_coefficients(s).keys())
#     else:
#         diff = differential_coefficients(s)
#         if diff[2**s.m] > 1:
#             return 2**s.m
#         else:
#             coeffs = diff.keys()
#             coeffs.sort()
#             return coeffs[-2]


# def linearity(s):
#     if not isinstance(s, mq.SBox):
#         s = mq.SBox(s)
#     if is_permutation(s):
#         return int(max(linear_coefficients(s).keys()))
#     else:
#         lin = linear_coefficients(s)
#         if lin[2**(s.m-1)] > 1:
#             return int(2**(s.m-1))
#         else:
#             coeffs = lin.keys()
#             coeffs.sort()
#             return int(coeffs[-2])
    


# def differential_branch_number(s):
#     if not isinstance(s, mq.SBox):
#         s = mq.SBox(s)
#     result = 2**s.n
#     for delta_in in xrange(1, 2**s.n):
#         w_in = hamming_weight(delta_in)
#         line = [0 for x in xrange(0, 2**s.m)]
#         for x in xrange(0, 2**s.m):
#             line[oplus(s[x], s[oplus(x,delta_in)])] += 1
#         for delta_out in xrange(0, 2**s.m):
#             if line[delta_out] != 0:
#                 w = w_in + hamming_weight(delta_out)
#                 if w < result:
#                     result = w
#     return result

# def linear_branch_number(s):
#     if not isinstance(s, mq.SBox):
#         s = mq.SBox(s)
#     result = 2**s.n
#     lat = s.linear_approximation_matrix()
#     for a in xrange(1, 2**s.n):
#         w_a = hamming_weight(a)
#         for b in xrange(0, 2**s.m):
#             if lat[a, b] != 0:
#                 w = w_a + hamming_weight(b)
#                 if w < result:
#                     result = w
#     return result


# !SUBSECTION! Algebraic properies

@parallel
def algebraic_normal_form_coordinate(s, i):
    """Returns the algebraic normal form of the `i`th coordinate of the
    SBox s.

    """
    coordinate = BooleanFunction([(x >> i) & 1 for x in list(s)])
    return coordinate.algebraic_normal_form()


def algebraic_normal_form(s_in):
    """Returns the algebraic normal form of the coordinates of the S-Box
    `s`.

    If we let each of the n output bits of `s` be a Boolean function
    s_i so that $s(x) = s_{n-1}(x) s_{n-2}(x) ... s_{0}(x)$, then
    returns a list l such that l[i] is the ANF of s_i.

    """
    result = {}
    s = mq.SBox(s_in)
    outputs = algebraic_normal_form_coordinate([(s, b) for b in range(0, s.n)])
    for entry in outputs:
        result[entry[0][0][1]] = entry[1]
    return [result[k] for k in range(0, s.n)]


def algebraic_degree(s):
    """Returns the algebraic degree of `s`, i.e. the maximum algebraic
    degree of its coordinates.

    """
    anf = algebraic_normal_form(s)
    result = 0
    for i in xrange(0, len(anf)):
        result = max(result, anf[i].degree())
    return result


# !SECTION! Inverting a LAT

def invert_lat(l):
    """Assuming that l is a valid function LAT, returns this function.

    Only works for functions with the same input and output length."""
    n = int(log(len(l), 2))
    return invert_lat_fast(l, n)


# !SECTION! Tests

if __name__ == '__main__':
    s = random_permutation(5)
    print s
    l = lat(s)
    s_prime = invert_lat(l)
    print s_prime

