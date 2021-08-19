# Hard problem 1 v2

## Problem setting
- $d, \delta = 3, \; 3$
- $\alpha=7/5$
- $\beta=8/5$
- $\Sigma=[0, 0] \cup (20/45, 21/45) \cup (30/45, 1]$
- Sigma is split at k/15 for each k in 1...14
- $\epsilon = 0.0001$

## Solution
Problem is discretizable.

$\;$| Interval | Reduction
----|---------|---------
A | $[0]$ | $0.0$
B | $(4/9,7/15)$ | $0.44454444$
C | $(2/3,14/15)$ | $0.7$
D | $[14/15,1]$ | $1.0$



```
RE-formalism:
A B D
A C C
A C D
A D D
B B C
B B D
B C C
B C D
B D D
C C C
C C D
C D D
D D D


A A A
A A B
A A C
A A D
A B B
A B C
A B D
A C C
B B B
B B C
```

## Notes

Modification to the original [hard problem 1](../hard_problem_1/hard_problem_1.md).