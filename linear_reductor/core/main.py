from fractions import Fraction
from functools import reduce

import portion as P
from tqdm import tqdm

from pathlib import Path
import logging
from base_logger import logger, TqdmLoggingHandler
import logging
from intervals import (create_interval_df, create_neighborhoods, detect_unions,
                       interval_list_splitter, join_intervals, name_gen,
                       regular_interval_split)
from solver import find_reductions
from problem import Problem, load_problem
import sys 
import argparse
import pickle

def create_test_problem():
    # Creates a dummy problem if the program is called without any input

    # Degrees of black and white nodes
    d = 3
    delta = 3

    # The treshold for black and white sums
    beta = Fraction(10, 10)
    alpha = Fraction(10, 10)

    # The set of possible labels
    Sigma_string = "[0, 1/3) U (1/3, 1]"

    # Do you want to split Sigma into smaller parts? This can help in some situations.
    do_split = True
    split_count = 40

    # Value used to handle strict inequalities in calculations. Can affect possible results. (We approximate a<b  <=> a<=b-epsilon <=> b>= a+epsilon.)
    epsilon = 0.0001


    p = Problem(d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon)
    return p




def run_reductor(problem, neighborhoods = None, do_print = True):
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
        neighborhoods = create_neighborhoods(intervals, var_stack, do_print)
        ready, union_list = detect_unions(neighborhoods, intervals, interval_count, var_stack, do_print)
        while not ready:
            logger.info(f"Joining intervals: {union_list}")
            interval_list = join_intervals(intervals, union_list)
            intervals, interval_count = create_interval_df(interval_list) 
            neighborhoods = create_neighborhoods(intervals, var_stack, do_print)
            ready, union_list = detect_unions(neighborhoods, intervals, interval_count, var_stack, do_print)
        
    else:
        logger.debug("Running reductor with manual neighborhoods table:")
        logger.debug(neighborhoods)

    # Try to find some reductions

    interval_df, neighborhoods = find_reductions(neighborhoods, intervals, interval_count, var_stack)

    output_string = create_output(interval_df, neighborhoods, var_stack, manual_neighborhoods, do_print)

    problem.set_solution(interval_df, neighborhoods, manual_neighborhoods)

    return problem, output_string



def create_output(interval_df, neighborhoods, var_stack, manual_neighborhoods, do_print=True):
    buffer = []
    if interval_df is None:
        buffer.append("No reductions found.")
        if do_print: tqdm.write("\n".join(buffer))
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
    if do_print: tqdm.write(output_string)
    return output_string


def main():
    # Create argument parser for CLI calls
    my_parser = argparse.ArgumentParser(description='Reduce continuous covering-packing problems to LCL:s.')

    my_parser.add_argument("-d", "--debug",
                        type = str,
                        nargs = 1,
                        metavar='level',
                        help = "select debugging level from (D)EBUG, (I)NFO, (W)ARNING, (E)RROR, (C)RITICAL")
    my_parser.add_argument("-l", "--logpath",
                        type = str,
                        nargs = 1,
                        metavar='path',
                        help = "specify a path for logfile. Otherwise logs are printed to console")
    my_parser.add_argument("-p", "--path",
                        type = str,
                        nargs = 1,
                        metavar='path',
                        help = "specify an input path to a json file containing the problem")
    my_parser.add_argument("-s", "--save",
                        type = str,
                        nargs = 2,
                        metavar=('path', 'name'),
                        help = "specify a path and name for saving the problem directory")
    args = my_parser.parse_args()

    # Disable logs as default
    logging.disable()

    if args.debug is not None:
        # Enable logging if -d flag is passed with a proper level
        logging.disable(logging.NOTSET)

        if args.debug[0].upper() in ["D", "DEBUG"]:
            tqdm.write("Selected debugging level: DEBUG")
            logger.setLevel(logging.DEBUG)

        elif args.debug[0].upper() in ["I", "INFO"]:
            tqdm.write("Selected debugging level: INFO")
            logger.setLevel(logging.INFO)

        elif args.debug[0].upper() in ["W", "WARNING"]:
            tqdm.write("Selected debugging level: WARNING")
            logger.setLevel(logging.WARNING)

        elif args.debug[0].upper() in ["E", "ERROR"]:
            tqdm.write("Selected debugging level: ERROR")
            logger.setLevel(logging.ERROR)

        elif args.debug[0].upper() in ["C", "CRITICAL"]:
            tqdm.write("Selected debugging level: CRITICAL")
            logger.setLevel(logging.CRITICAL)

        else:
            tqdm.write(f'Argument "{args.debug}" is not a valid logging level!')
            logging.disable()
    
    if args.logpath is not None:
        # Send logs to logpath aswell instead of console
        fh = logging.FileHandler(Path(args.logpath[0]))
        fh.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(fh)
    else:
        # Create console handler that works with tqdm (progress bars)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        ch = TqdmLoggingHandler()
        ch.setFormatter(formatter)

        logger.handlers = []
        logger.addHandler(ch)

    save = False
    if args.save is not None:
        # Save the problem at the specified path
        if not Path(args.save[0]).is_dir():
            tqdm.write(f"Save directory {Path(args.save[0])} was not found. Problem will not be saved.")
        else:
            tqdm.write(f"Problem will be saved to {Path(args.save[0]).resolve()} with name {args.save[1]}.")
            save = True

    if args.path is not None:
        # Load the problem described at path
        if not Path(args.path[0]).is_file():
            tqdm.write(f"No file found at {Path(args.path[0])}. Exiting program.")
            return
        else:
            p, message= load_problem(args.path[0])
            if p is None:
                tqdm.write(message)
                tqdm.write(f"No problem was found at the file in {args.path[0]}. Exiting program.")
                return
            if not p.is_valid_problem():
                tqdm.write(f"Problem was found, but it was corrupted. Exiting program.")
                return
    else:
        p = create_test_problem()

    problem, output_string = run_reductor(p, do_print=True)

    if save:
       problem.save(Path(args.save[0]), args.save[1])
    
if __name__== "__main__":
    main()