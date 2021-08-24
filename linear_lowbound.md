# Deterministic low-bound for packing-covering problems

## Problem
Consider the following family of locally verifiable problems in (d, $\delta$)-biregular trees:
- $\Sigma \subseteq [0,1]$
- Task is to label the edges
- Sum of edge labels incident to
    - active nodes is $\leq \beta$
    - passive nodes is $\geq \alpha$
- Additionally leaf nodes accept all possible neighbourhoods.

## Statement

The deterministic time complexity of the problem is either $O(1)$ or $\Omega( \log n)$. 

## Proof
If $\beta=d$ or $\alpha=0$, the problem is either zero round-solvable, or not at all, as in these cases we would have to label everything with either $1$ or $0$ respectively. 

From now on, let's assume these additional inequalities:
$$
\begin{aligned}

\beta &< d  \\ 
\alpha &> 0 

\end{aligned}
$$

Additionally, if $\Sigma \cap \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right] \neq \emptyset$, the problem is solvable in zero rounds, labeling each edge with some $x \in \Sigma \cap \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right]$. From now on let $\Sigma \cap \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right] = \emptyset$. We can relax our problem to be $\Sigma = [0,1] \setminus \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right]$. 
### **Case** $\frac{\alpha}{\delta} < \frac{\beta}{d}$ (Slack):


Now we will show that this problem is equivalent to sinkless orientation and thus the original problem is $\Omega(\log n)$.

We will show that for $a\in A =\left[0, \frac{\alpha}{\delta} \right)$, $b\in B =\left(\frac{\beta}{d}, 1 \right]$ there exists a reduction $f(A) =  a, f(B) = b$ so that the problem is equivevalent to sinkless orientation in $(d, \delta)$-biregular trees.

First consider all the possible neighbourhoods that could exist, and what values they could sum up to. The possible neighbourhoods for active nodes are:
$$
\begin{aligned}
&\underbrace{A, A, ..., A}_{d \text{ times}}  &= \quad &\left[0,  \quad d\cdot \frac{\alpha}{\sigma} \right)\\
&\underbrace{A, A, ..., A}_{d-1 \text{ times}}, B &= \quad &\left(\frac{\beta}{d}, \quad (d-1)\cdot \frac{\alpha}{\sigma} +1 \right)\\
&\underbrace{A, A, ..., A}_{d-2 \text{ times}}, B, B &= \quad &\left(2\cdot \frac{\beta}{d}, \quad (d-2)\cdot \frac{\alpha}{\sigma}+2 \right)\\
&\vdots \\
& A, A, \underbrace{B, B, ...,B}_{d-2 \text{ times}}  &= \quad &\left((d-2)\cdot \frac{\beta}{d}, \quad 2\cdot \frac{\alpha}{\sigma} + (d-2) \right)\\
& A,\underbrace{B, B, ...,B}_{d-1 \text{ times}} &= \quad &\left((d-1)\cdot \frac{\beta}{d}, \quad  \frac{\alpha}{\sigma}+(d-1) \right)\\
& \underbrace{B, B, ...,B}_{d \text{ times}} &= \quad &\left(d\cdot \frac{\beta}{d}, \quad d \right]\\

\end{aligned}
$$

Each neighbourhood, except for $\underbrace{B, B, ...,B}_{d \text{ times}}$, contain values less than or equal to $\beta$, and thus could be a neighbourhood of an active node. 

The neighbourhoods for passive nodes are:
$$
\begin{aligned}
&\underbrace{A, A, ..., A}_{\delta \text{ times}}  &= \quad &\left[0,  \quad \delta \cdot \frac{\alpha}{\delta} \right)\\
&\underbrace{A, A, ..., A}_{\delta-1 \text{ times}}, B &= \quad &\left(\frac{\beta}{d}, \quad (\delta -1)\cdot \frac{\alpha}{\delta} +1 \right)\\
&\underbrace{A, A, ..., A}_{\delta-2 \text{ times}}, B, B &= \quad &\left(2\cdot \frac{\beta}{d}, \quad (\delta -2)\cdot \frac{\alpha}{\delta}+2 \right)\\
&\vdots \\
& A, A, \underbrace{B, B, ...,B}_{\delta-2 \text{ times}}  &= \quad &\left((\delta -2)\cdot \frac{\beta}{d}, \quad 2\cdot \frac{\alpha}{\delta} + (\delta -2) \right)\\
& A,\underbrace{B, B, ...,B}_{\delta-1 \text{ times}} &= \quad &\left((\delta -1)\cdot \frac{\beta}{d}, \quad  \frac{\alpha}{\delta}+(\delta -1) \right)\\
& \underbrace{B, B, ...,B}_{\delta \text{ times}} &= \quad &\left(\delta \cdot \frac{\beta}{d}, \quad \delta  \right]\\

\end{aligned}
$$

Again each neighbourhood, except for $\underbrace{A, A, ...,A}_{ \delta \text{ times}}$, contain values more than or equal to $\alpha$, and thus could be a neighbourhood of an active node. 


Now if we were able to choose values $a\in A$, $b\in B$ so that we can replace each interval with one label without breaking any labelings, our problem will be exactly sinkless orientation.


Let us choose values $\epsilon =  \frac{\beta\,\delta-\alpha\,d}{\delta^2\, d^2}>0$, $a=\frac{\alpha}{\delta}-\epsilon$ and $b=\frac{\beta}{d}+\epsilon$, and show that reduction $A\to a$, $B\to b$ won't break any labelings.

For active nodes, we can focus on the reduction of the neighbourhood 
$$
A,\underbrace{B, B, ...,B}_{d-1 \text{ times}} = a+(d-1)b,
$$
as $a+(d-1)b\leq \beta$ and $a<b$ imply $(1+m)a+(d-1-m)b\leq \beta$ for all $m\in\N$.

$$
\begin{aligned}

a+(d-1)b &= \frac{\alpha}{\delta} - \epsilon + (d-1)\left(\frac{\beta}{d}+\epsilon\right) \\
&= \frac{\alpha}{\delta} + \beta - \frac{\beta}{d} + (d-2)\epsilon \\
&= \beta - \frac{\beta}{d} + \frac{\alpha}{\delta} + (d-2)\epsilon
\end{aligned}
$$
Now $a+(d-1)b\leq\beta$ if and only if $(d-2)\epsilon \leq \frac{\beta}{d} - \frac{\alpha}{\delta}$. As $d, \delta \geq 2$:

$$
\begin{aligned}

(d-2)\epsilon &= (d-2)\cdot \frac{\beta\,\delta-\alpha\,d}{\delta^2\, d^2} \\
&< \frac{\beta\,\delta-\alpha\,d}{\delta\, d} \\
&= \frac{\beta}{d} - \frac{\alpha}{\delta}

\end{aligned}
$$
and thus $a+(d-1)b\leq \beta$.

Now we've proven that all active constraints are satisfied after the reduction. Same deduction applies for passive nodes: we can concentrate on the neighbourhood
$$
\underbrace{A, A, ..., A}_{\delta-1 \text{ times}}, B = (\delta-1)a+b,
$$
as neighbourhoods with more B:s will then clearly be satisfied.

$$
\begin{aligned}

(\delta-1)a+b &= (\delta-1)\left(\frac{\alpha}{\delta} - \epsilon\right) + \frac{\beta}{d}+\epsilon \\
&= \alpha - \frac{\alpha}{\delta} + \frac{\beta}{d} - (\delta-2)\epsilon \\
&= \alpha + \frac{\beta}{d} - \frac{\alpha}{\delta} - (\delta-2)\epsilon
\end{aligned}
$$
Now $(\delta-1)a+b\geq \alpha$ if and only if $(\delta-2)\epsilon \leq \frac{\beta}{d} - \frac{\alpha}{\delta}$. As $d, \delta \geq 2$:

$$
\begin{aligned}

(\delta-2)\epsilon &= (\delta-2)\cdot \frac{\beta\,\delta-\alpha\,d}{\delta^2\, d^2} \\
&< \frac{\beta\,\delta-\alpha\,d}{\delta\, d} \\
&= \frac{\beta}{d} - \frac{\alpha}{\delta}

\end{aligned}
$$

Thus we have proven that the reduction $A\to a, B\to b$ won't break any labelings and so the relaxed problem is just as hard as its discretization:
$$
\begin{aligned}
a &= \frac{\alpha}{\delta} - \frac{\beta\,\delta-\alpha\,d}{\delta^2\, d^2} \\
b &= \frac{\beta}{d} + \frac{\beta\,\delta-\alpha\,d}{\delta^2\, d^2} \\
\Sigma &= \{a,b\} \\

S_A &= \left\{\{x_1, x_2, x_3,..., x_d\} \;|\; \sum_{x_i} \leq \beta, x_i \in \Sigma\right\} \\
S_P &= \left\{\{x_1, x_2, x_3,..., x_\delta\} \;|\; \sum_{x_i} \geq \alpha, x_i \in \Sigma\right\},
\end{aligned}
$$
which happens to be exactly the same problem as sinkless orientation:
$$
\begin{aligned}
\Sigma &= \{A,B\} \\
S_A &= \left\{\{A, x_2, x_3,..., x_d\} \;|\; x_i\in \Sigma \right\} \\
S_P &= \left\{\{B, x_2, x_3,..., x_\delta\} \;|\; x_i\in \Sigma \right\}.
\end{aligned}
$$

### **Cases** $\frac{\alpha}{\delta} = \frac{\beta}{d}$ (Exact) and $\frac{\alpha}{\delta} > \frac{\beta}{d}$ (Anti-slack):

An algorithm solving these cases would also be able to solve the easier problem $\frac{\alpha}{\delta} < \frac{\beta}{d}$ (Slack), which is equivevalent to sinkless orientation. 


Thus the lower bound $\Omega(\log n)$ holds.