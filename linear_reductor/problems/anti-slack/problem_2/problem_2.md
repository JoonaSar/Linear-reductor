# Problem 2

## Problem setting
- $d, \delta = 3, \; 3$
- $\alpha=2$
- $\beta=1$
- $\Sigma=3$
- Sigma is split at k/3 for each k in 1...2
- $\epsilon = 0.0001$

## Solution
Problem is discretizable.

$\;$| Interval | Reduction
----|---------|---------
A | $[0,Fraction(1, 3))$ | $0.0$
B | $[1/2, 2/3)$ | $0.5$
C | $[Fraction(2, 3),1]$ | $1.0$



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
```

## Notes
