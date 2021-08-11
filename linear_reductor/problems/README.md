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

Each problem directory contains one human readable markdown file and one JSON-file of the following format:
```
File
 ┣ name                         // string
 ┣ parameters
 ┃ ┣ d                          // int 
 ┃ ┣ delta                      // int
 ┃ ┣ beta                       // [numerator, denominator], int, int
 ┃ ┣ alpha                      // [numerator, denominator], int, int
 ┃ ┣ Sigma_string               // string
 ┃ ┣ do_split                   // bool
 ┃ ┣ split_count                // int
 ┃ ┗ epsilon                    // float
 ┗ Solution
 ┃ ┣ interval_df                // dict (interval dataframe)
 ┃ ┣ neighborhoods              // dict (neighborhoods dataframe)
 ┃ ┗ manual_neighborhoods       // bool
```

Examples of interval and neighborhoods dataframes:<br>


$\;$| Interval | Reduction
----|---------|---------
A |$[0, 1/3)$ | $0.16661667$
B |$(2/3, 1]$ | $0.66676667$

<br><br>

$\;$| W | B
----|---|--
A A A | `false` | `true`
A A B | `true` | `true`
A B B | `true` | `false`
B B B | `true` | `false`



## Generating problems


Anything written after `## Notes` in the human readable markdown-files is preserved. All other markings are overwritten each time the problem files are saved there.