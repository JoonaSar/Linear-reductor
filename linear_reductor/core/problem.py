import json
from fractions import Fraction
from functools import reduce
from pathlib import Path
import pandas as pd
import portion as P
import re
import sys
from base_logger import logger


class Problem:

    def __init__(self, d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon):

        self.parameters = {}

        self.parameters["d"] = d
        self.parameters["delta"] = delta

        self.parameters["beta"] = beta
        self.parameters["alpha"] = alpha

        self.parameters["Sigma_string"] = Sigma_string

        self.parameters["do_split"] = do_split
        self.parameters["split_count"] = split_count

        self.parameters["epsilon"] = epsilon
        
        # Solution is set only if one is found
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

    def save_to_dir(self, dirpath, savename):
        if not dirpath.is_dir():
            raise NotADirectoryError()
        
        filename = "".join(x for x in list(savename.replace(" ", "_")) if x.isalnum() or x=="_").lower()
        if filename in ["", None]: raise Exception(f"Filename {savename} is not allowed, use alphanumeric characters.")
        try:
            md_path = dirpath / filename / f"{filename}.md"
            with md_path.open(mode="r") as f:
                markdown_file_contents = f.readlines()
                i = 0
                while i < len(markdown_file_contents):
                    if "## Notes" in markdown_file_contents[i]: break
                    i += 1
                    
                notes = "".join(markdown_file_contents[i::])
                
        except:
            notes = "## Notes"
        a = r"\a"
        b = r"\b"
        name = savename.replace("_", " ").capitalize()
        sigma = self.parameters["Sigma_string"].replace("U", r"\cup")

        splits = "No splits"
        if self.parameters["do_split"]:
            split_count = self.parameters['split_count']
            splits = f"Sigma is split at k/{split_count} for each k in 1...{split_count-1}"
            
        interval_df = self.solution["interval_df"]
        white_retor = ""
        black_retor = ""

        if interval_df is None: 
            solved = "Problem is not discretizable."
            interval_df_str = ""
        else:
            solved = "Problem is discretizable."
            interval_df_str = "$\;$| Interval | Reduction\n----|---------|---------\n"
            for index, row in interval_df.iterrows():
                interval_df_str += f"{str(index)} | $" 
                interval_df_str += re.sub('Fraction\(([0-9]+), ([0-9]+)\),Fraction\(([0-9]+), ([0-9]+)\)', r'\1/\2, \3/\4', str(row["interval"]))
                interval_df_str += "$ | $" + str(row["reduction"]) +"$\n"

            white_retor = "```\nRE-formalism:\n"
            black_retor = ""
            for index, row in self.solution["neighborhoods"].iterrows():
                if row["W"]:
                    white_retor += " ".join(row["combination"])
                    white_retor += "\n"
                if row["B"]:
                    black_retor += " ".join(row["combination"])
                    black_retor += "\n"

            black_retor += "```"

        try:
            # Try to write the files
            md_path = dirpath / filename / f"{filename}.md"
            md_path.parent.mkdir(parents = True, exist_ok = True)
            with md_path.open(mode="w") as f:
                logger.debug(f"Writing markdown file to {md_path}")
                f.write(f"""# {name}

## Problem setting
- $d, \delta = {self.parameters["d"]}, \; {self.parameters["delta"]}$
- ${a}lpha={self.parameters["alpha"]}$
- ${b}eta={self.parameters["beta"]}$
- $\Sigma={self.parameters["d"]}$
- {splits}
- $\epsilon = {self.parameters["epsilon"]}$

## Solution
{solved}

{interval_df_str}


{white_retor}

{black_retor}

{notes}
""")
            json_path = dirpath / filename / f"{filename}.json"
            with json_path.open(mode="w") as f:
                logger.debug(f"Writing json file to {json_path}")
                f.write(self.toJson())

            # Return true if everything was saved
            return True, None
        except Exception as e:
            logger.debug(e)
            return False, e
        
        
            


def read_sigma(Sigma_string):
    interval_li = list(map(lambda x: P.from_string(x, conv=Fraction), Sigma_string.split(" U ")))
    Sigma = reduce(lambda a, b: a | b, interval_li)  
    return Sigma, interval_li