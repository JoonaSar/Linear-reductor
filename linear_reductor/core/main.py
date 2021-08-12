from fractions import Fraction
from functools import reduce

import portion as P
from tqdm import tqdm

from base_logger import logger
from intervals import (create_interval_df, create_neighborhoods, detect_unions,
                       interval_list_splitter, join_intervals, name_gen,
                       regular_interval_split)
from solver import find_reductions
from problem import Problem

# Define some variables

# Degrees of black and white nodes
d = 3
delta = 3

# The treshold for black and white sums
beta = Fraction(20, 10)
alpha = Fraction(10, 10)

# The set of possible labels
Sigma_string = "[0, 1/3) U (1/3, 1]"

# Do you want to split Sigma into smaller parts? This can help in some situations.
do_split = False
split_count = 40

# Value used to handle strict inequalities in calculations. Can affect possible results. (We approximate a<b  <=> a<=b-epsilon <=> b>= a+epsilon.)
epsilon = 0.0001


p = Problem(d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon)






def run_reductor(problem, neighborhoods = None):
    # Main program running reductions. It first checks for 0-round solutions.

    var_stack, interval_li, do_split, split_count = problem.get_parameters()
    d, delta, beta, alpha, epsilon, Sigma = var_stack

    # First check for 0-round solution
    easy_solution_interval = P.closed(Fraction(alpha, delta), Fraction(beta, d))
    easy_solutions = (easy_solution_interval & Sigma)
    


    if do_split:
        interval_list = regular_interval_split(interval_li, split_count, var_stack)
    else:
        interval_list = interval_li
    intervals, interval_count = create_interval_df(interval_list) 
        
    # If reductor is run without neighborhoods-variable, it calculates them using var_stack.
    # Run this with neighborhoods if you're trying to do for example hardening.
    manual_neighborhoods = True
    if neighborhoods is None:
        manual_neighborhoods = False
        neighborhoods = create_neighborhoods(intervals, var_stack)
        ready, union_list = detect_unions(neighborhoods, intervals, interval_count, var_stack)
        while not ready:
            logger.info(f"Joining intervals: {union_list}")
            interval_list = join_intervals(intervals, union_list)
            intervals, interval_count = create_interval_df(interval_list) 
            neighborhoods = create_neighborhoods(intervals, var_stack)
            ready, union_list = detect_unions(neighborhoods, intervals, interval_count, var_stack)
        
    else:
        logger.debug("Running reductor with manual neighborhoods table:")
        logger.debug(neighborhoods)

    # Try to find some reductions

    interval_df, neighborhoods = find_reductions(neighborhoods, intervals, interval_count, var_stack)

    output_string = create_output(interval_df, neighborhoods, var_stack, manual_neighborhoods)

    problem.set_solution(interval_df, neighborhoods, manual_neighborhoods)

    return problem, output_string



def create_output(interval_df, neighborhoods, var_stack, manual_neighborhoods, do_print=True):
    buffer = []
    if interval_df is None:
        buffer.append("No reductions found.")
        if do_print: print("\n".join(buffer))
        return "\n".join(map(lambda x: str(x), buffer))
    
    buffer.append("Reductions found.")
    buffer.append(interval_df)
    buffer.append("\n")

    # Translate the problem to round-eliminator formalism. 
    d, delta, beta, alpha, epsilon, Sigma = var_stack

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
    
    if manual_neighborhoods: buffer.append("Neighborhoods set manually! Original problem is at least as easy as the following.")
    buffer.append("Round eliminator syntax:")
    buffer.append("\n" + black_retor)
    buffer.append("\n" + white_retor)

    output_string = "\n".join(map(lambda x: str(x), buffer))
    if do_print: print(output_string)
    return output_string


if __name__== "__main__":
    run_reductor(p)
