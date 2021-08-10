import portion as P 
from fractions import Fraction
from functools import reduce
from base_logger import logger
from solver import find_reductions
from intervals import interval_list_splitter, create_neighborhoods, create_interval_df, \
    detect_unions, join_intervals, regular_interval_split, name_gen
from tqdm import tqdm




# Define some variables

# Degrees of black and white nodes
d = 3
delta = 3

# The treshold for black and white sums
beta = Fraction(10, 10)
alpha = Fraction(10, 10)

# The set of possible labels
Sigma_string = "[0, 1/3) U (1/3, 1]"

# Do you want to split Sigma into smaller parts? This can help in some situations.
do_split = False
split_count = 40

# Value used to handle strict inequalities in calculations. Can affect possible results. (We approximate a<b  <=> a<=b-epsilon <=> b>= a+epsilon.)
epsilon = 0.0001




def read_sigma(Sigma_string):
    interval_li = list(map(lambda x: P.from_string(x, conv=Fraction), Sigma_string.split(" U ")))
    Sigma = reduce(lambda a, b: a | b, interval_li)  
    logger.info(f"Sigma: {Sigma}")
    return Sigma, interval_li

Sigma, interval_li = read_sigma(Sigma_string)

var_stack = (d, delta, beta, alpha, epsilon, Sigma)



def run_reductor(var_stack, interval_li, do_split, split_count, neighborhoods = None):
    # Main program running reductions. It first checks for 0-round solutions.



    # First check for 0-round solution
    easy_solution_interval = P.closed(Fraction(alpha, delta), Fraction(beta, d))
    easy_solutions = (easy_solution_interval & Sigma)
    if not easy_solutions.empty:

        params = {
            'disj': ' U '
        }
        print("0-round solution found.")
        print(f"Choose any single value from {P.to_string(easy_solutions, **params)}.")
    
    # Create neighborhoods if they aren't given already
    else:
        print("No 0-round solutions found.")

        if do_split:
            interval_list = regular_interval_split(interval_li, split_count, var_stack)
        else:
            interval_list = interval_li
        intervals, interval_count = create_interval_df(interval_list) 
        
    # If reductor is run without neighborhoods-variable, it calculates them using var_stack.
    # Run this with neighborhoods if you're trying to do for example hardening.
    if neighborhoods is None:
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

    print_output(interval_df, neighborhoods, var_stack)

    return interval_df, neighborhoods, intervals, interval_count



def print_output(interval_df, neighborhoods, var_stack):

    if interval_df is None:
        print("No reductions found.")
        return
    
    print("Reductions found.")
    print(interval_df)

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
    
    
    print("\nRound eliminator syntax:")
    print("\n"+black_retor)
    print("\n"+white_retor)


if __name__== "__main__":
    run_reductor(var_stack, interval_li, do_split, split_count)