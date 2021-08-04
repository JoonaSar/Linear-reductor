import numpy as np 
import pandas as pd
import portion as P 
import string
import itertools
import logging
from fractions import Fraction
from functools import reduce
from base_logger import logger


def create_interval_df(interval_list):
    # Create the dataframe containing the list of intervals, their name (A, B, ...) and their possible future reduction. 

    interval_count = len(interval_list)
    
    intervals = pd.DataFrame({"interval": [x for x in interval_list]}, index=name_gen(interval_count))
    intervals["reduction"] = None

    logger.info(f"Created following interval dataframe:\n{intervals}")
    return intervals, interval_count



def create_neighborhoods(intervals, var_stack):
    # Create all of the possible neighborhoods that could exist, and check which of them could surround active or passive nodes (B/W).
    # If d =/= delta, it's not possible for a neighborhood to be suitable for both nodes.

    d, delta, beta, alpha, epsilon, Sigma = var_stack
    # First create all neighborhoods.
    if d==delta:
        combinations = list(itertools.combinations_with_replacement(intervals.index, d))
        neighborhoods = pd.DataFrame({"combination": combinations})
        neighborhoods["W"] = None 
        neighborhoods["B"] = None

    else:
        combinations = list(itertools.combinations_with_replacement(intervals.index, delta))
        combinations.extend(list(itertools.combinations_with_replacement(intervals.index, d)))
        neighborhoods = pd.DataFrame({"combination": combinations})
        neighborhoods["OK"] = None
        
    logger.debug(f"Created following neighborhood dataframe:\n{neighborhoods}")

    white_range = P.closedopen(alpha, P.inf)
    black_range = P.openclosed(-P.inf, beta)

    logger.debug(f"Black range: {black_range}")
    logger.debug(f"White range: {white_range}")
    logger.debug("\nRanges of neighbourhood sums")


    # Then calculate the intervals, that the sum of these neighborhoods could have. 
    # If they contain any values suitable for active/passive nodes, the neighbourhood is considered as suitable for that color.
    for index, row in neighborhoods.iterrows():
        interval = sum_intervals(row["combination"], list(map(lambda x: intervals.loc[x, "interval"], row["combination"])))
        
        c = " ".join(row["combination"])
        logger.debug(f'{c}: {interval}')

        # See if we have to check both white and black ranges or only one
        if d==delta:
            neighborhoods.at[index, "W"] = not (white_range & interval).empty
            neighborhoods.at[index, "B"] = not (black_range & interval).empty
            
        else: 
            if len(row["combination"]) == d:
                neighborhoods.at[index, "OK"] = not (black_range & interval).empty
                
            else: neighborhoods.at[index, "OK"] = not (white_range & interval).empty
            
    logger.info(f"Created following neighbourhoods:\n{neighborhoods}")
    return neighborhoods



def detect_unions(neighborhoods, intervals, interval_count, var_stack):
    # Detect intervals in combinations-table that could be joined without breaking labelings.
    # This can happen in two cases: If two intervals have exactly the same rows, or rows of one interval is a strict subset of the other.
    # Using a single discretization value for them can enable discretization.
   
    # This is a brute force solution, any smarter ideas are welcome.
    
    # We can only look at neighborhoods with maximal amounts of either label of the pair, as labels are are absolutely ordered:
    #   Let A < B. Now A^nB^mXY is white --> A^(n-i)B^(m+i)XY is white for all 0<=i<=n. Same for black, except in the other direction.
    # Basically if the truth value for active-/passiveness of a neighborhood changes in middle of some series (AAA, AAB, ABB, BBB),
    # then the endpoints have different truth values. 
        
    d, delta, beta, alpha, epsilon, Sigma = var_stack
    
    pairs = [name_gen(interval_count)[i:i+2] for i in range(interval_count-1)]

    new_intervals = "A"
    join_found = False
    join_ended = False

    for pair in pairs:
        # Handle at most one joinable set in each round, so that two joins don't break each other,
        # eg. AB is a join if intervals C and D are not joined, and CD can be joined if A and B aren't.
        
        if not (join_found and join_ended):
            low_worse = False
            high_worse = False
            problem_df = pd.DataFrame()
            
            others = [c for c in name_gen(interval_count) if c not in pair]

            for i in range(d, 0, -1):
                for end in itertools.combinations_with_replacement(others, d-i):

                    low_index = tuple(sorted(tuple(itertools.repeat(pair[0], i)) + end))
                    high_index = tuple(sorted(tuple(itertools.repeat(pair[1], i)) + end))
                    
                    low_row = neighborhoods.loc[neighborhoods["combination"] == low_index,  :]
                    high_row = neighborhoods.loc[neighborhoods["combination"] == high_index, :]

                    if d == delta:

                        if low_row["W"].iloc[0] != high_row["W"].iloc[0] and not low_worse:
                            low_worse = True
                            problem_df = problem_df.append(low_row, ignore_index=True)
                            problem_df = problem_df.append(high_row, ignore_index=True)

                        
                        if low_row["B"].iloc[0] != high_row["B"].iloc[0] and not high_worse:
                            high_worse = True
                            problem_df = problem_df.append(low_row, ignore_index=True)
                            problem_df = problem_df.append(high_row, ignore_index=True)
                        
                        if low_worse and high_worse:
                            logger.debug(f"{pair} is not interchangeable:\n{problem_df}")
                            break
                    
                    else:
                        if not low_row["OK"].iloc[0] and high_row["OK"].iloc[0] and not low_worse:
                            low_worse = True
                            problem_df.append(low_row, ignore_index=True)
                            problem_df.append(high_row, ignore_index=True)

                        
                        if low_row["OK"].iloc[0] and not high_row["OK"].iloc[0] and not high_worse:
                            high_worse = True
                            problem_df.append(low_row, ignore_index=True)
                            problem_df.append(high_row, ignore_index=True)
                        
                        if low_worse and high_worse:
                            logger.debug(f"{pair} is not interchangeable:\n{problem_df}")
                            # Breaks innermost loop (end)
                            break
                # Breaks outermost loop (i)
                if low_worse and high_worse: break 

            if d != delta:
                for i in range(delta, 0, -1):
                    for end in itertools.combinations_with_replacement(others, delta-i):
                        low_index = tuple(sorted(tuple(itertools.repeat(pair[0], i)) + end))
                        high_index = tuple(sorted(tuple(itertools.repeat(pair[1], i)) + end))

                        low_row = neighborhoods.loc[neighborhoods["combination"] == low_index,  :]
                        high_row = neighborhoods.loc[neighborhoods["combination"] == high_index, :]
                        
                        if not low_row["OK"].iloc[0] and high_row["OK"].iloc[0] and not low_worse:
                            low_worse = True
                            problem_df = problem_df.append(low_row, ignore_index=True)
                            problem_df = problem_df.append(high_row, ignore_index=True)

                        
                        if low_row["OK"].iloc[0] and not high_row["OK"].iloc[0] and not high_worse:
                            high_worse = True
                            problem_df = problem_df.append(low_row, ignore_index=True)
                            problem_df = problem_df.append(high_row, ignore_index=True)
                        
                        if low_worse and high_worse:
                            logger.debug(f"{pair} is not interchangeable:\n{problem_df}")
                            break
        
        
            if low_worse and high_worse: 
                new_intervals += " "
                if join_found: join_ended = True
            else:
                join_found = True
            new_intervals += pair[1]
        # If we've found one joinable area which has ended, just add the rest of the intervals to listing.
        else:
            new_intervals += " "
            new_intervals += pair[1]

    new_intervals = new_intervals.split(" ")

    # Are some intervals interchangeable (union needed)?
    return (len(new_intervals) == interval_count, new_intervals)


def join_intervals(intervals, union_list):
    # Create a new set of intervals after combining previous intervals, as directed by detect_unions.

    interval_list = []
    
    for chars in union_list:
        new_interval = intervals.at[chars[0], "interval"]
        for char in chars[1:]:
            new_interval = new_interval.union(intervals.at[char, "interval"])
        interval_list.append(new_interval)
    
    return interval_list

def regular_interval_split(interval_list, split_count, var_stack):
    # Split the interval list at points (1/splits, 2/splits, ... , (splits-1)/splits)

    splits = [Fraction(x+1, split_count) for x in range(split_count-1)]
    
    return interval_list_splitter(interval_list, splits, var_stack)



def interval_list_splitter(interval_list, splits, var_stack):
    # Split the interval list at points given in splits.
    # This can help in some cases, especially when beta<alpha (anti-slack).
    # TODO: fix splitted interval endpoints, now both splits contain the endpoint. Can have a huge effect.
    # Now implemented as half-open intervals (] until "midpoint" and [) onwards, where also first and last are closed intervals []. This is some handwavy variable, there may be some better way to determine these. 
    
    d, delta, beta, alpha, epsilon, Sigma = var_stack
    new_int_li = []
    
    # Handwavy heuristic value
    midpoint = np.mean([alpha, beta])/np.mean([d, delta])    
    
    # Previous split value
    prev = 0
    
    for x in splits:

        left_in = prev==0 or prev > midpoint
        
        right_in = x <= midpoint

        if left_in and right_in:
            interval = P.closed(prev, x) & Sigma
        if left_in and not right_in:
            interval = P.closedopen(prev, x) & Sigma
        if not left_in and right_in:
            interval = P.openclosed(prev, x) & Sigma
        if not left_in and not right_in:
            interval = P.open(prev, x) & Sigma
        
        if not interval.empty: new_int_li.extend(interval)

        prev = x
    # Handle the last interval [last_split, 1]
    interval = P.closed(prev, 1) & Sigma
    if not interval.empty: new_int_li.extend(interval)

    
    # Verify that splitting didn't create or miss any points:
    splitted_sigma = reduce(lambda a, b: a | b, new_int_li)
    if splitted_sigma != Sigma:
        logger.error("Interval splitter dropped/added some point(s)!")
        logger.error(f"Sigma:\n{Sigma}\nUnion of splitted intervals:\n{splitted_sigma}")

    logger.debug(f"Interval was split at {splits}. The midpoint heuristic value was {midpoint}.")
    return new_int_li

def sum_intervals(combination, interval_list):
    # Basic_sum_intervals can only handle a list of atomic intervals, eg. not [[1,2], (3,4) U (4,5)].
    # This will translate a sum of more complicated intervals to atomic summations, while also considering the intervals that we are adding.

    # For example, [0, 1] U [5,6] + [0, 1] U [5,6] is not [0, 2] U [5, 7] U [10, 12], as they are the same original interval and thus must be discretized to the same value, so [5, 7] is not possible. 

    ints = []
    c = 0
    # Combination is some neighborhood eg. AAABBC, which is grouped to (A, (A,A,A)), (B, (B,B)), (C, (C))
    # Basically multiply the boundaries of all atomic intervals of a single interval by the number it's repeated in the neighborhood.
    # After that add that new multiplied interval to a list of different intervals, that are then combined and summed (cartesian product). 
    for i, g in itertools.groupby(combination):
        count = len("".join(g))
        intervals = [interval.apply(lambda x: (x.left, x.lower*count, x.upper*count, x.right)) for interval in interval_list[c]]
        c += count
        ints.append(intervals)

    return reduce(lambda a, b: a | b, map(lambda li: basic_sum_intervals(li), itertools.product(*ints)))


def basic_sum_intervals(interval_list):
    # Given a list of atomic intervals, determine the sum of those intervals, eg. the interval where the sum could end up to.
    
    min = 0
    max = 0
    min_in = True
    max_in = True
    for interval in interval_list:
        min_in = min_in and interval.left == P.CLOSED
        max_in = max_in and interval.right == P.CLOSED
        min += interval.lower
        max += interval.upper
    if min_in and max_in:
        return P.closed(min, max)
    if min_in and not max_in:
        return P.closedopen(min, max)
    if not min_in and max_in:
        return P.openclosed(min, max)
    return P.open(min, max)


# Return the list of interval names
def name_gen(count = 56):
    # Intervals are named in the following order:
    # 0-25 get uppercase letters,
    # 26-51 get lowercase letters,
    # 52-61 get digits 0-9
    # If there are more than 94 intervals, this will throw an error.
    # Then a more sophisticated solution should be created.

    s = string.ascii_uppercase + string.ascii_lowercase

    return list(s[0 : count])
    