# Linear reductor program

## Packing-covering problem
Consider the following family of locally verifiable problems in (d, $\delta$)-biregular trees:
- $\Sigma \subseteq [0,1]$
- Task is to label the edges
- Sum of edge labels incident to
    - active nodes is $\leq \beta$
    - passive nodes is $\geq \alpha$
- Additionally leaf nodes accept all possible neighbourhoods.

The purpose of this program is to discretize these problems into equivevalent LCL:s, which are much more easier to argue about.

## Types of problems

It seems that the most important factor in determining if and how a given covering-packing problem is going to discretize, is the ratio between $\alpha$ and $\beta$. Problems are distributed in three classes:
- Slack: $\alpha<\beta$, i.e. any value in $[\alpha, \beta]$ satisfies both active and passive nodes.
- Exact: $\alpha = \beta$, i.e. only the value $\alpha = \beta$ satisfies both active and passive nodes.
- Anti-Slack:  $\alpha>\beta$, i.e. no value satisfies both active and passive nodes.


## File structure

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


## Vocabulary
Some vocabulary used in code and these problem listings.

Word | Meaning 
---|---
Discretize | To create a 0-round mapping from a linear problem to an equivevalent LCL.
Discretization | The 0-round mapping from a linear problem to an equivevalent LCL.
Discretization value | The value for an interval in discretization $f$, i.e. discretization value for interval $A$ is $x$ iff $x=f(a), \forall a \in A$. (Also "reduction").
Neighborhood table | Table of each possible combination of intervals, and the info whether that combination *could* satisfy the active and/or passive nodes (refered to as black/white nodes). If the problem discretizes, the information in this table is equivevalent to the information in the RE-formalism string.
Interchangeable | If two intervals $A$ and $B$ are interchangeable, their rows in the neighborhood table are equivevalent, i.e. rows $A(X...),\; B(X...)$ are equivevalent for all interval combinations $(X...)$. Interchangeability implies that the intervals can be joined.
Joining (intervals) | Two intervals $A$ and $B$ are joined in the discretization process, so that they receive the same discretization value. This can help the discretization (see [Join problem 1](slack/join_problem_1/join_problem_1.md)). If however there are multiple joins available in a neighborhood table, the order of these joins can affect results. This is an open problem.
Splitting (intervals) | Splitting intervals at some set of points divides those original intervals so that the new smaller intervals get their own discretization values. The endpoints of these intervals are distributed according to the midpoint-heuristic. For now there isn't a smart way to distinguish when splitting is required, or where those split-points are. At the time if a problem doesn't seem discretizable, it is a good idea to try and split it at every $1/n$ points, and trying different values for $n$. This can either help the discretization (see [Split problem 1](anti-slack/split_problem_1/split_problem_1.md)), or possibly break it. Splitting the interval space can create horribly complex problems, but sometimes the small intervals are automatically joined, so that the important split points remain.
Midpoint-heuristic | A handwavy heuristic used to determine in which new interval the splitpoint falls into. Midpoint is defined as $\frac{\alpha + \beta}{d + \delta}$, so that every interval containing only smaller values is "small", and vice versa for "large" intervals. The interval which contains the midpoint is "mid". Splitpoints that are smaller than the midpoint are distributed to the smaller interval, and splitpoints larger than the midpoint are distributed to the larger interval. In case of the midpoint being a splitpoint, it is distributed to the smaller interval. This way of distributing the splitpoints is designed to create as many open interval sums as possible, where those could make the difference.

## Notes

GUI is fixed so that $d = \delta$ always, but CLI should handle those cases. This is done because the implementation for problem hardening probably doesn't yet work with $d \neq \delta$.  

Any improvements to finding splitting points would probably be valuable.

In the case that $d \neq \delta$, instead of the ratio of $\alpha$ and $\beta$, one should use the ratio between $\frac{\alpha}{\delta}$ and $\frac{\beta}{d}$ instead.