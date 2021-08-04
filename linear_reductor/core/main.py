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
alpha = Fraction(15, 10)

# The set of possible labels
Sigma_string = "[0, 4/10) U [1/2, 1]"

# Do you want to split Sigma into smaller parts? This can help in some situations.
do_split = True
split_count = 40

# Value used to handle strict inequalities in calculations. Can affect possible results. (We approximate a<b  <=> a<=b-epsilon <=> b>= a+epsilon.)
epsilon = 0.0001


params = {
    'disj': ' U '
}

def read_sigma(Sigma_string):
    interval_li = list(map(lambda x: P.from_string(x, conv=Fraction), Sigma_string.split(" U ")))
    Sigma = reduce(lambda a, b: a | b, interval_li)  
    logger.info(f"Sigma: {Sigma}")
    return Sigma, interval_li

Sigma, interval_li = read_sigma(Sigma_string)

var_stack = (d, delta, beta, alpha, epsilon, Sigma)



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
            interval_list = regular_interval_split(interval_li, split_count, var_stack)
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
            


        find_reductions(neighborhoods, intervals, interval_count, var_stack)
        



if __name__== "__main__":
    run_reductor()