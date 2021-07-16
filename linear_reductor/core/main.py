#import numpy as np 
#import pandas as pd
import portion as P 
#import string
#import itertools
#import math
#import re
from fractions import Fraction
#from scipy.optimize import linprog
#from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable
from functools import reduce
from base_logger import logger


from solver import find_reductions
from intervals import interval_list_splitter, create_neighborhoods, create_interval_df, \
    detect_unions, join_intervals



# Define some variables

# Degrees of black and white nodes
d = 3
delta = 3

# The treshold for black and white sums
beta = Fraction(10, 10)
alpha = Fraction(15, 10)

# The set of possible labels
Sigma_string = "[0, 4/10] U [5/10, 1]"

# Do you want to split Sigma into smaller parts? This can help in some situations.
do_split = False
split_count = 12

# Value used to handle strict inequalities in calculations. Can affect possible results. (We approximate a<b  <=> a<=b-epsilon <=> b>= a+epsilon.)
epsilon = 0.000001

def convert(s):
    try:
        return float(s)
    except ValueError:
        return (s)

params = {
    'disj': ' U '
}

interval_li = list(map(lambda x: P.from_string(x, conv=Fraction), Sigma_string.split(" U ")))
Sigma = reduce(lambda a, b: a | b, interval_li)  

var_stack = (d, delta, beta, alpha, epsilon, Sigma)

# Create logger. Logging levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL (not all are necessarily used) 


# Define parser for Sigma
      

logger.info(f"Sigma: {Sigma}")

def run_reductor():
    # Main program running reductions. It first checks for 0-round solutions, then 

    # First check for 0-round solution
    easy_solution_interval = P.closed(Fraction(alpha, delta), Fraction(beta, d))
    easy_solutions = (easy_solution_interval & Sigma)
    if not easy_solutions.empty:
        print("0-round solution found.")
        print(f"Choose any single value from {P.to_string(easy_solutions, **params)}.")
    
    # Try to find some reductions
    else:
        print("No 0-round solutions found.")

        if do_split:
            interval_list = interval_list_splitter(interval_li, split_count, var_stack)
        else:
            interval_list = interval_li
        intervals, interval_count = create_interval_df(interval_list) 
        
        neighborhoods = create_neighborhoods(intervals, var_stack)
        ready, union_list = detect_unions(neighborhoods, intervals, interval_count, var_stack)
        while not ready:
            logger.info(f"Joining intervals: {union_list}")
            interval_list = join_intervals(intervals, union_list)
            intervals, interval_count = create_interval_df(interval_list) 
            neighborhoods = create_neighborhoods(intervals, var_stack)
            ready, union_list = detect_unions(neighborhoods, intervals, interval_count, var_stack)
            


        reduced_intervals = find_reductions(neighborhoods, intervals, interval_count, var_stack)
        print(reduced_intervals)
        print_retor(neighborhoods)
        


def print_retor(neighborhoods):
    # Translate the problem to round-eliminator formalism. 
    # Returned LCL is at most as hard as the given problem. 
    # If the problem is discretizable, the discretization gives a zero round mapping between these problems.

    if d == delta:
        white_retor = ""
        black_retor = ""
        for index, row in neighborhoods.iterrows():
            if row["W"]:
                white_retor += " ".join(row["combination"])
                white_retor += "\n"
            if row["B"]:
                black_retor += " ".join(row["combination"])
                black_retor += "\n"

    else:
        white_retor = ""
        black_retor = ""
        for index, row in neighborhoods.iterrows():
            if len(row["combination"]) == d and row["OK"]:
                black_retor += " ".join(row["combination"])
                black_retor += "\n"
            elif row["OK"]:
                white_retor += " ".join(row["combination"])
                white_retor += "\n"
    
    
    print("\nRound eliminator syntax:")
    print("\n"+black_retor)
    print("\n"+white_retor)


if __name__== "__main__":
    run_reductor()