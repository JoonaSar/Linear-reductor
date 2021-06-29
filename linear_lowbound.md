# Low-bound for packing-covering problems

## Problem
Consider the following family of locally verifiable problems in (d, $\delta$)-biregular trees:
- $\Sigma \subseteq [0,1]$
- Task is to label the edges
- Sum of edge labels incident to
    - active nodes is $\leq \beta$
    - passive nodes is $\geq \alpha$
- Additionally leaf nodes accept all possible neighbourhoods.

## Statement

If $\frac{\alpha}{\delta} < \frac{\beta}{d}$, then the time complexity of the problem is either $O(1)$ or $\Omega( \log n)$.

### Proof
Let $\frac{\alpha}{\delta} < \frac{\beta}{d}$. 

If $\beta=d$ or $\alpha=0$, the problem is either zero round-solvable, or not at all. 

Now assume these additional inequalities and their implications:
$$
\begin{aligned}

\beta &< d  &(1)\\ 
\alpha &> 0 &(2)\\
0 < \frac{\alpha}{\delta} &< \frac{\beta}{d} < 1 &(3)

\end{aligned}

$$

If $\Sigma \cap \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right] \neq \emptyset$, the problem is solvable in zero rounds, labeling each edge with some $x \in \Sigma \cap \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right]$.

Now let $\Sigma \cap \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right] = \emptyset$. We can relax our problem to be $\Sigma = [0,1] \setminus \left[\frac{\alpha}{\delta}, \frac{\beta}{d}\right]$. Now this problem is equivalent to sinkless orientation and thus the original problem is $\Omega(\log n)$.

We will show that there will always be values $a\in A =\left[0, \frac{\alpha}{\delta} \right)$ and $b\in B =\left(\frac{\beta}{d}, 1 \right]$ so if every label from sets $A$ and $B$ is replaced by the corresponding values $a$ and $b$, the solution remains valid, and that the problem is equivalent to sinkless orientation in $(d, \delta)$-biregular trees.

First consider all the possible neighbourhoods that could exist, and what values they could sum up to. The possible neighbourhoods for active nodes are:
$$
\begin{aligned}
&\underbrace{A, A, ..., A}_{d \text{ times}}  &= \quad &\left[0,  \quad d\cdot \frac{\alpha}{\sigma} \right)\\
&\underbrace{A, A, ..., A}_{d-1 \text{ times}}, B &= \quad &\left(\frac{\beta}{d}, \quad (d-1)\cdot \frac{\alpha}{\sigma} +1 \right)\\
&\underbrace{A, A, ..., A}_{d-2 \text{ times}}, B, B &= \quad &\left(2\cdot \frac{\beta}{d}, \quad (d-2)\cdot \frac{\alpha}{\sigma}+2 \right)\\
&\vdots \\
& A, A, \underbrace{B, B, ...,B}_{d-2 \text{ times}}  &= \quad &\left((d-2)\cdot \frac{\beta}{d}, \quad 2\cdot \frac{\alpha}{\sigma} + (d-2) \right)\\
& A,\underbrace{B, B, ...,B}_{d-1 \text{ times}} &= \quad &\left((d-1)\cdot \frac{\beta}{d}, \quad  \frac{\alpha}{\sigma}(d-1) \right)\\
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
& A,\underbrace{B, B, ...,B}_{\delta-1 \text{ times}} &= \quad &\left((\delta -1)\cdot \frac{\beta}{d}, \quad  \frac{\alpha}{\delta}(\delta -1) \right)\\
& \underbrace{B, B, ...,B}_{\delta \text{ times}} &= \quad &\left(\delta \cdot \frac{\beta}{d}, \quad \delta  \right]\\

\end{aligned}
$$

Again each neighbourhood, except for $\underbrace{A, A, ...,A}_{ \delta \text{ times}}$, contain values more than or equal to $\alpha$, and thus could be a neighbourhood of an active node. 


Now if we were able to choose values $a\in A$, $b\in B$ so that we can replace each interval with one label without breaking any labelings, our problem will be exactly sinkless orientation.


Let us choose values $a=\frac{\alpha}{\delta}\left(1-\frac{\beta}{d}\right)$ and $b=\frac{\beta}{d}\left(1-\frac{\alpha}{\delta}\right)$, and show that reduction $A\to a$, $B\to b$ won't break any labelings.

For active nodes, we can focus on the reduction of the neighbourhood 
$$
A,\underbrace{B, B, ...,B}_{d-1 \text{ times}} = a+(d-1)b,
$$
as $a+(d-1)b\leq \beta$ and $a<b$ imply the same inequality for all other neighbourhoods.

$$
\begin{aligned}

a+(d-1)b &= \frac{\alpha}{\delta} - \frac{\beta\, \alpha}{d\, \delta} + (d-1)\left(\frac{\beta}{d}+\frac{\beta\, \alpha}{d\, \delta}\right) \\
&= \frac{\alpha}{\delta} - \frac{\beta\, \alpha}{d\, \delta} + \beta-\frac{\beta}{d}+(d-1)\frac{\beta\, \alpha}{d\, \delta} \\
&= \beta+\frac{\alpha}{\delta}  -\frac{\beta}{d}+(d-2)\frac{\beta\, \alpha}{d\, \delta}

\end{aligned}
$$