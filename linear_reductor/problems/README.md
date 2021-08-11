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
 ┃ ┣ 📜problem 1.txt
 ┃ ┗ 📜problem 2.txt
 ┣ 📂exact
 ┃ ┣ 📜problem 3.txt
 ┃ ┗ 📜problem X.txt
 ┣ 📂slack
 ┃ ┣ 📜problem 4.txt
 ┃ ┗ 📜problem 5.txt
 ┗ 📜README.md
```

At the start of each problem file there should be a JSON structure like this:
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
   ┣ interval_df                // dict (interval dataframe)
   ┣ neighborhoods              // dict (neighborhoods dataframe)
   ┗ manual_neighborhoods       // bool

```

For example:
```
{
        "name": "Problem name",
        "parameters": {
                "d": 3,
                "delta": 3,
                "beta": [
                        1,
                        1
                ],
                "alpha": [
                        1,
                        1
                ],
                "Sigma_string": "[0, 1/3) U (2/3, 1]",
                "do_split": false,
                "split_count": 40,
                "epsilon": 0.0001
        },
        "solution": {
                "interval_df": {
                        "interval": {
                                "A": "[Fraction(0, 1),Fraction(1, 3))",
                                "B": "(Fraction(2, 3),Fraction(1, 1)]"
                        },
                        "reduction": {
                                "A": 0.16661667,
                                "B": 0.66676667
                        }
                },
                "neighborhoods": {
                        ... // Neighborhoods-dataframe as dict
                    }
                },
                "manual_neighborhoods": false
        }
}

Some text about the problem....
```

