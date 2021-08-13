# Linear reductor problem listing

## Types of problems

The most important factor in determining if and how a given covering-packing problem is going to discretize, is the ratio between $\alpha$ and $\beta$. Problems are distributed in three classes:
- Slack: $\alpha<\beta$, i.e. any value in $[\alpha, \beta]$ satisfies both active and passive nodes.
- Exact: $\alpha = \beta$, i.e. only the value $\alpha = \beta$ satisfies both active and passive nodes.
- Anti-Slack:  $\alpha>\beta$, i.e. no value satisfies both active and passive nodes.


## Structure

Problems are listed in a directory in the following format:
```
📦problems
 ┣ 📂anti-slack
 ┃ ┣ 📂problem_1
 ┃ ┃ ┣ 📜problem_1.json
 ┃ ┃ ┗ 📜problem_1.md
 ┃ ┗ 📂problem_2
 ┃ ┃ ┣ 📜problem_2.json
 ┃ ┃ ┗ 📜problem_2.md
 ┣ 📂exact
 ┃ ┗ 📂problem_X
 ┃ ┃ ┣ 📜problem_X.json
 ┃ ┃ ┗ 📜problem_X.md
 ┣ 📂slack
 ┃ ┗ 📂problem_3
 ┃ ┃ ┣ 📜problem_3.json
 ┃ ┃ ┗ 📜problem_3.md
 ┗ 📜README.md
```

Each problem directory contains one human readable markdown file describing the problem, and one computer-readable file containing the problem as a pickled object.

## Generating and commenting problems

Problems can be generated using the graphical UI. Enter the problem parameters, hit "Find reductions", and harden the problem if you want to. The proper save directory should automatically be determined according to the `slack/exact/anti-slack`-category of your problem, but this can be changed. When saving, remember to give the problem a name.

Problems can also be generated using the command line interface to the program. Run the `main.py` with `-h` flag for instructions:
```
usage: main.py [-h] [-d level] [-l path] [-p path] [-s path name]

Reduce continuous covering-packing problems to LCL:s.

optional arguments:
  -h, --help            show this help message and exit
  -d level, --debug level
                        select debugging level from (D)EBUG, (I)NFO, (W)ARNING, (E)RROR, (C)RITICAL
  -l path, --logpath path
                        specify a path for logfile. Otherwise logs are printed to console
  -p path, --path path  specify an input path to a json file containing the problem
  -s path name, --save path name
                        specify a path and name for saving the problem directory
```

Anything written after `## Notes` in the human readable markdown-files is preserved. All other markings are overwritten each time the problem files are rewritten, which you might want to do if a new discretization is found to an old problem.
