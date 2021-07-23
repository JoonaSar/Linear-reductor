import portion as P 
import string
import math
import logging
from fractions import Fraction
from scipy.optimize import linprog
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable
from functools import reduce
from base_logger import logger


def find_reductions(neighborhoods, intervals, interval_count, var_stack):
    # Find discrete values in given intervals that satisfy all constraints given by neighborhoods.
    # In practice the program creates a system of linear inequalities implied by interval definitions and neighborhoods in PULP
    # and gives that system to a solver, that then returns a solution, if one exists.

    d, delta, beta, alpha, epsilon, Sigma = var_stack

    model = LpProblem(name="Reductions", sense=LpMaximize)

    variables = dict(zip(list(string.ascii_lowercase[0:interval_count]), 
                    [LpVariable(name = symbol, lowBound=0, upBound=1) for symbol in list(string.ascii_lowercase[0:interval_count])]))
    
    

    # Add the constraints of the original sets
    for index, row in intervals.iterrows():
        variable = variables[index.lower()]
        interval = row["interval"]
        
        # Check for non-atomic intervals (caused by unions)
        if interval.atomic:
            if interval.left == P.CLOSED:
                model += (variable>=interval.lower, f"Init_{index}_lower")
            else:
                model += (variable>=interval.lower + epsilon, f"Init_{index}_lower")
                
            if interval.right == P.CLOSED:
                model += (variable<=interval.upper, f"Init_{index}_upper")
            else:
                model += (variable<=interval.upper - epsilon, f"Init_{index}_upper")
        

        # Non-atomic intervals need some tricks, as the value cannot satisfy all atomic interval conditions at the same time.
        # Tricks implemented as presented in https://download.aimms.com/aimms/download/manuals/AIMMS3OM_IntegerProgrammingTricks.pdf
        else: 
            atomics = len(interval)
            trick_var_count = math.ceil(math.log(atomics, 2))
            trick_vars = [LpVariable(name = f"Trick_var_{index}_{x}", lowBound=0, upBound=1, cat="Binary") for x in range(trick_var_count)]
            # Example: x in [0, 1] U [2, 3] U [4, 5] <=>
            # x >= 0 - 1000*(0 - trick_1) - 1000*(0 - trick_0)   &&   x <= 1 + 1000*(0 - trick_1) + 1000*(0 - trick_0)
            # x >= 2 - 1000*(0 - trick_1) - 1000*(0 - trick_0)   &&   x <= 3 + 1000*(0 - trick_1) + 1000*(1 - trick_0)
            # x >= 4 - 1000*(1 - trick_1) - 1000*(0 - trick_0)   &&   x <= 5 + 1000*(1 - trick_1) + 1000*(0 - trick_0)
            # 2 * trick_1 + trick_0 <= 2 


            # Atomic intervals are distinguished by binary representation of the interval number, eg. 1:st (0:th) atomic interval is chosen when all trick_vars are 0, etc.
            for c in range(atomics):
                tricksum = None
                c_binary = format(c, f'0{trick_var_count}b')[::-1]
                for i in range(trick_var_count):
                    if c_binary[i] == "0":
                        tricksum += 1000*trick_vars[i]
                    else:
                        tricksum += 1000*(1-trick_vars[i])

                if interval[c].left == P.CLOSED:
                    model += (variable>=interval[c].lower - tricksum, f"Init_{index}_lower_{c}")
                else:
                    model += (variable>=interval[c].lower + epsilon - tricksum, f"Init_{index}_lower_{c}")
                    
                if interval[c].right == P.CLOSED:
                    model += (variable<=interval[c].upper + tricksum, f"Init_{index}_upper_{c}")
                else:
                    model += (variable<=interval[c].upper - epsilon + tricksum, f"Init_{index}_upper_{c}")
            # Prevent any trick variable configuration not encoding an atomic interval
            model += (reduce(lambda a, b: 2*a+b, trick_vars[::-1]) <= atomics-1, f"Trick_var_maximum_{index}")


    # Add the constraints imposed by summation of the original sets
    if d == delta:
        for index, row in neighborhoods.iterrows():
            if (row["W"]):
                model += (sum(map(lambda x: variables[x.lower()], row["combination"])) >= alpha, f"Constraint_{index}_W")
            if (row["B"]):
                model += (sum(map(lambda x: variables[x.lower()], row["combination"])) <= beta, f"Constraint_{index}_B")

    else:  
        for index, row in neighborhoods.iterrows():
            if (len(row["combination"])==d) and row["OK"]:
                model += (sum(map(lambda x: variables[x.lower()], row["combination"])) <= beta, f"Constraint_{index}_B")
            elif (row["OK"]):
                model += (sum(map(lambda x: variables[x.lower()], row["combination"])) >= alpha, f"Constraint_{index}_W")


    logger.debug(f"\n{model}\n")

    # Search for solutions to the given system of inequalities
    if model.solve() == -1:
        print("No reductions found.")
    
    else:
        print("Reductions found: ")
        for var in model.variables():
            if "TRICK_VAR" not in var.name.upper() and "__DUMMY" not in var.name.upper():
                intervals.loc[var.name.upper(), "reduction"] = var.value()
            
            if "TRICK_VAR" in var.name.upper():
                logger.info(f"{var.name}: {var.value()}")
            
        print(intervals)
        print_retor(neighborhoods, var_stack)
    

def print_retor(neighborhoods, var_stack):
    # Translate the problem to round-eliminator formalism. 
    # Returned LCL is at most as hard as the given problem. 
    # If the problem is discretizable, the discretization gives a zero round mapping between these problems.
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
