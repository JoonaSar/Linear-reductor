# Hard problem 1 v3

## Problem setting
- $d, \delta = 3, \; 3$
- $\alpha=7/5$
- $\beta=8/5$
- $\Sigma=[0, 1/10) \cup (20/45, 21/45) \cup (30/45, 1]$
- No splits
- $\epsilon = 0.0001$

## Solution
Problem is discretizable.

$\;$| Interval | Reduction
----|---------|---------
A | $[0,1/10)$ | $0.0$
B | $(4/9,7/15)$ | $0.44454444$
C | $(2/3,1]$ | $0.71091111$



```
RE-formalism:
A C C
B B C
B C C
C C C


A A A
A A B
A A C
A B B
A B C
A C C
B B B
B B C
```

## Notes

Modification to the original [hard problem 1](../hard_problem_1/hard_problem_1.md).