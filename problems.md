# Linear problems

List interesting problems in this document.



## Interesting/hard problems

$`d, \delta`$ | $`\beta, \alpha`$ | $`\Sigma`$ | Interesting part
--------| -------|---------|--------------------
3, 3 | 1, 1 | $`[0,1]\setminus \{1/3\}`$ | (W/O slack) Doesn't discretize. Harder than SO, maybe 2 coloring with choice? Two W/B rows.
3, 3 | 1, 1 | $`[0, 1/3) \cup [1/2, 1]`$ | Same as above. Any value from $`(1/3, 1/2]`$ breaks discretization.
4, 4 | 5/2, 2 | $`[0, 1/4) \cup (3/4, 1] `$  | (W/ Slack) Doesn't discretize. Two W/B rows. 
4, 4 | 5/2, 2 | $`[0, 1/4) \cup (7/8, 1] `$  | (W/ Slack) Discretizes. One W/B row. 
3, 3 | 1.6, 1.4 | $`[0, 21/45) \cup (24/45, 1]`$ | (W/ Slack) Discretizes. Baseline for next problem. Two W/B rows.
3, 3 | 1.6, 1.4 | $`[0, 1/3) \cup (1/3, 21/45) \cup (24/45, 1]`$ | ~~(W/ Slack) Doesn't discretize, but A and B are interchangeable in neighborhood table. (Splitting causes non-discretizability, check previous problem.)~~ Discretizes as of 12.7.
3, 3 | 1.6, 1.4 | $`[0, 1/10) \cup (1/3, 21/45) \cup (24/45, 1]`$ | ~~(W/ Slack) Doesn't discretize. Here the small interval $`[0, 1/10)`$ breaks discretization, but it could be joined to the next interval, as it is possible to replace it in any neighborhood.~~ Discretizes as of 14.7.
3, 3 | 1.6, 1.4 | $`[0, 1/10) \cup (20/45, 21/45) \cup (30/45, 1]`$ | (W/ Slack) Doesn't discretize. The smaller interval $`[0, 1/10)`$ cannot be replaced with $`(20/45, 21/45)`$ in all neighborhoods, so joining those intervals is not going to help. Any discretization value from the smaller part would not satisfy all of the neighborhoods accepted by the larger part, and vice versa.
3, 3 | 1, 2 | $`[0, 4/10] \cup [5/10, 8/10) \cup (8/10, 1]`$ | (W/ **Anti-Slack**) Doesn't discretize. **No W/B rows**.
3, 3 | 1, 2 | $`[0, 1/2) \cup (1/2, 1]`$ | (W/ Anti-Slack) Discretizes after splitting intervals at (1/3, 2/3).
3, 3 | 1, 1.5 | $`[0, 1/2] \cup (1/2, 1]`$ | (W/Anti-Slack) Doesn't seem to discretize, even after splitting intervals at every 1/6:th.





## Linear problems in LCL-form

Listing interesting linear problems and their reductions.

$`d, \delta`$ | $`\beta, \alpha`$ | $`\Sigma`$ | Active | Passive
--------| -------|---------|----------|----------
$`d = 3, \delta = 3`$ | $`\beta = 2, \alpha = 1`$ | $`[0, 1/9) \cup (5/6, 1]`$ | A AB AB  | B AB AB
$`d = 3, \delta = 3`$ | $`\beta = 2, \alpha = 3/2`$ | $`[0, 1/9) \cup (5/6, 1]`$ | A AB AB  | B B AB
$`d = 3, \delta = 3`$ | $`\beta = 7/4, \alpha = 3/2`$ | $`[1/3, 2/4) \cup (5/6, 1]`$ | A A AB | B AB AB








## LCL-problems in another linear form

These are usual problems transformed into the form
- Labelset $`\Sigma`$ is a finite subset of $`[0,1]`$.
- The sum of labels incident to
  - an active node is in $`\alpha \subseteq [0,1]`$
  - a passive node is in $`\beta \subseteq [0,1]`$


Problem | Active | Passive | $`\alpha`$ | $`\beta`$ | Labels
--------| -------|---------|----------|----------|-------
Sinkless orientation | $`A \; B`$ | $`A \; AB \; AB`$ | $`[1.002, 1.5005]`$ | $`[2.001, 3.0]`$ | $`A: 1.0, B: 0.5005`$
Sinkless orientation | $`A \; B \; B`$ | $`AB \; B`$ | $`[2.001, 2.6656667]`$ | $`[0.0, 1.999]`$ | $`A: 1.0, B: 0.66666667`$
Sinkless orientation | $`A \; B \; B`$ | $`B \; AB \; AB`$ | $`[0.0010000001, 1.999]`$ | $`[0.0, 2.999]`$ | $`A: 1.0, B: 0.0`$
Sinkless orientation | $`A \; B`$ | $`A \; AB \; AB \; AB \; AB`$ | $`[0.801, 1.999]`$ | $`[2.001, 5.0]`$ | $`A: 1.0, B: 0.4`$
Sinkless orientation | $`A \; B`$ | $`A \; AB \; AB \; AB \; AB`$ | $`[0.0023333335, 0.0023333333]`$ | $`[0.0043333334, 5.0]`$ | $`A: 0.0016666667, B: 0.00066666667`$
Artificial problem 3-3-3 | $`B \; B \; B \\ A \; C \; C`$ | $`C \; BC \; BC \\ C \; C \; ABC`$ | $`[0.66833333, 1.3326667]`$ | $`[0.0, 1.0]`$ | $`A: 1.0, B: 0.33366667, C: 0.0`$
Perfect matching | $`A \; B \; B`$ | $`A \; B \; B`$ | $`[0.0010000001, 1.999]`$ | $`[0.0010000001, 1.999]`$ | $`A: 1.0, B: 0.0`$
Path diagram | $`A \; B \; C`$ | $`A \; A \; AB \; ABC \\ A \; AB \; AB \; AB`$ | $`[1.6716667, 2.002]`$ | $`[3.002, 4.0]`$ | $`A: 1.0, B: 0.66766667, C: 0.33433333`$








