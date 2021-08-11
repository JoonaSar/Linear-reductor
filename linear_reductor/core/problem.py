import json
from fractions import Fraction
from functools import reduce

import pandas as pd
import portion as P


class Problem:

    def __init__(self, d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon, name = "Unnamed problem"):
        # Degrees of black and white nodes
        self.name = name
        self.parameters = {}
        self.parameters["d"] = d
        self.parameters["delta"] = delta

        # The treshold for black and white sums
        self.parameters["beta"] = beta
        self.parameters["alpha"] = alpha

        # The set of possible labels
        self.parameters["Sigma_string"] = Sigma_string

        # Do you want to split Sigma into smaller parts? This can help in some situations.
        self.parameters["do_split"] = do_split
        self.parameters["split_count"] = split_count

        # Value used to handle strict inequalities in calculations. Can affect possible results. (We approximate a<b  <=> a<=b-epsilon <=> b>= a+epsilon.)
        self.parameters["epsilon"] = epsilon
        
        self.solution = None
    

    def set_solution(self, interval_df, neighborhoods, manual_neighborhoods = False):
        self.solution = {}
        self.solution["interval_df"] = interval_df
        self.solution["neighborhoods"] = neighborhoods
        self.solution["manual_neighborhoods"] = manual_neighborhoods

    def get_parameters(self):
        Sigma, interval_li = read_sigma(self.parameters["Sigma_string"])
        var_stack = (self.parameters["d"], self.parameters["delta"], self.parameters["beta"], self.parameters["alpha"], self.parameters["epsilon"], Sigma)
        return (var_stack, interval_li, self.parameters["do_split"], self.parameters["split_count"])

    def toJson(self):
        #try: 
        #    self.solution["interval_df"] = self.solution["interval_df"].to_dict()
        #except:
        #    self.solution["interval_df"] = None
        
        #self.solution["neighborhoods"] = self.solution["neighborhoods"].to_dict()
        def encoder(o):
            if isinstance(o, Fraction):
                return (o.numerator, o.denominator)
            if isinstance(o, P.Interval):
                return (str(o))
            if o is None:
                return None
            if isinstance(o, pd.DataFrame):
                return o.to_dict()
            try:
                return o.__dict__
            except:
                return json.JSONEncoder.default(self, o)

        return json.dumps(self, default=encoder, indent="\t")

    def __str__(self):
        return self.toJson()


def read_sigma(Sigma_string):
    interval_li = list(map(lambda x: P.from_string(x, conv=Fraction), Sigma_string.split(" U ")))
    Sigma = reduce(lambda a, b: a | b, interval_li)  
    return Sigma, interval_li
