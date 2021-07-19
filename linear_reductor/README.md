# Finding reductions for linear problems
Consider the following locally verifiable problem in (d, $`\delta`$)-biregular trees:
- $`\Sigma \subseteq [0,1]`$
- Task is to label the edges
- Sum of edge labels incident to
    - white nodes is $`\geq \alpha`$
    - black nodes is $`\leq \beta`$
- Additionally leaf nodes accept all possible neighborhoods.

This program tries to find a value $`\{a, b, ...\}`$ in each maximal separate continuous interval $`A, B, C, ... \subseteq \Sigma = [0, 1]`$, so that any valid labeling can be transformed to another valid labeling by **simultaneously** replacing all labels with the value corresponding to their interval. This reduces the set of labels down to $`\Sigma = \{a, b, ...\}`$.





The basic idea is to check every combination of these intervals and note which of these combinations could be neighborhoods of white and/or black nodes. Using these combinations we can form a system of linear inequalities that the simultanious reductions must satisfy. Lastly we use linear programming to search for a set of values.


## Example 1:

Locally verifiable problem $`\Pi`$ in (3,3)-biregular trees:
- $`\Sigma = [0, 1/3) \cup (2/3, 1]`$
- $`\alpha = 1`$
- $`\beta = 2`$

Clearly there are no 0-round solutions, as $`[1/3, 2/3] \cap \Sigma = \emptyset`$. Let $`A= [0, 1/3)`$ and $`B= (2/3, 1]`$. The possible combinations for a neighborhood are:

- A, A, A 
- A, A, B 
- A, B, B 
- B, B, B

We can also calculate the range of the sum of any given neighborhood:

- $`A, A, A = \left[0, 1 \right)`$
- $`A, A, B = \left(\frac{2}{3}, \frac{5}{3}\right)`$
- $`A, B, B = \left(\frac{4}{3}, \frac{7}{3}\right)`$
- $`B, B, B = \left(2, 3\right]`$

This table shows us, for example, that that the neighbourhood $`A, A, B`$ can be a neighbourhood of a black or a white node. This however doesn't yet mean that **any** three values from the corresponding ranges can surround both white and black nodes. It just means that if we were to collapse these ranges into single values, that collapsed neighbourhood would need to be suitable for both white and black nodes. Using this idea we can create a system of inequalities that any suitable reduction must satisfy.

```math
\begin{aligned}

a \in A \iff 0\leq a &< \frac{1}{3} \\
b \in B \iff \frac{2}{3} < b &\leq 1 \\
3a &\leq 2 \\
1 \leq 2a+b  &\leq 2 \\
1 \leq a+2b &\leq 2 \\
3b &\geq 1
\end{aligned}
```
Now any pair $`(a,b)`$ satisfying these inequalities will be a valid reducion. Using linear programming, we can find for example the solution $`(0.161667, 0.676667)`$. Now the problem just as easy as the LCL problem (in RE syntax):
```
A A A
A A B
A B B


A A B
A B B
B B B
```

Note that these reductions **cannot** be found separately: if we choose any value for $`a\in A`$, we can find values $`b_1, b_2, b_3 \in B`$ so that a white node has the neighbourhood $`a+a+b_1<1`$ or a black node has the neighbourhood $`a+b_2+b_3>2`$, which breaks our labeling. Same logic applies to fixing $`b`$ first.