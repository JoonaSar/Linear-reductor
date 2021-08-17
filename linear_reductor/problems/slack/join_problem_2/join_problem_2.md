# Join problem 2

## Problem setting
- $d, \delta = 3, \; 3$
- $\alpha=7/5$
- $\beta=8/5$
- $\Sigma=[0, 1/10) \cup (1/3, 21/45) \cup (24/45, 1]$
- No splits
- $\epsilon = 0.0001$

## Solution
Problem is discretizable.

$\;$| Interval | Reduction
----|---------|---------
A | $[0,1/10) \cup (1/3,7/15)$ | $0.46656667$
B | $(8/15,1]$ | $0.53343333$



```
RE-formalism:
A A B
A B B
B B B


A A A
A A B
A B B
```

## Notes
This is an example problem where intervals $[0/1, 1/10)$ and  $(1/3, 7/15)$ are not interchangeable (see [Join problem 1](../join_problem_1/join_problem_1.md)), but the table for $[0/1, 1/10)$ is a subset of the table for $(1/3, 7/15)$, so they are joined.
