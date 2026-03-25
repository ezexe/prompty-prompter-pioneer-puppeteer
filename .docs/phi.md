```python
# List comprehension: A compact way to create a list by running
# the function for every 'i' in the range
# result = [fib(i) for i in range(10)]
# print(result) # Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
def fib(n):
    if n <= 0: return 0
    elif n == 1: return 1
    else: return fib(n-1) + fib(n-2)
```
Every time you go up one number (e.g., from 5 to 6), you aren't just adding one branch—you are re-growing the entire tree from two steps ago as a side branch.
* (6) contains a full (5) tree on the left.
* (6) contains a full (4) tree on the right.

Exactly how many **(1)**s and **(0)**s (the base cases) it takes to build the final number?
Here is the full, un-cached expansion for each step:
```md
* fib(0) --> 0 -> 0
* fib(1) --> 1 -> 1

* fib(2) --> 1 -> 1
  (2)
  / \
 1 + 0

* fib(3) --> 2 -> 10
    (3)
    / \
  (2)+ 1
  / \
 1 + 0

* fib(4) --> 3 -> 100 > 4 -> 101
       _(4)_
      /     \
    (3)  +  (2)
    / \     / \
  (2)+ 1   1 + 0
  / \
 1 + 0

* fib(5) --> 5 -> 1000 > 6 -> 1001 > 7 -> 1010
             ___(5)___
            /         \
       _(4)_     +    (3)
      /     \         / \
    (3)  +  (2)     (2)+ 1
    / \     / \     / \
  (2)+ 1   1 + 0   1 + 0
  / \
 1 + 0

* (6) --> 8 -> 10000
                   _______(6)_______
                  /                 \
             ___(5)___     +       _(4)_
            /         \           /     \
       _(4)_     +    (3)       (3)  +  (2)
      /     \         / \       / \     / \
    (3)  +  (2)     (2)+ 1    (2)+ 1   1 + 0
    / \     / \     / \       / \
  (2)+ 1   1 + 0   1 + 0     1 + 0
  / \
 1 + 0
```
| Decimal | Binary Weights (8,4,2,1) | Binary Code | Fibonacci Weights (13,8,5,3,2,1) | Zeckendorf Code |
| ------- | ------------------------ | ----------- | -------------------------------- | --------------- |
| 1       | 1                        | 0001        | 1                                | 000001          |
| 2       | 2                        | 0010        | 2                                | 000010          |
| 3       | 2+1                      | 0011        | 3                                | 000100          |
| 4       | 4                        | 0100        | 3+1                              | 000101          |
| 5       | 4+1                      | 0101        | 5                                | 001000          |
| 6       | 4+2                      | 0110        | 5+1                              | 001001          |
| 7       | 4+2+1                    | 0111        | 5+2                              | 001010          |
| 8       | 8                        | 1000        | 8                                | 010000          |
| 9       | 8+1                      | 1001        | 8+1                              | 010001          |
| 10      | 8+2                      | 1010        | 8+2                              | 010010          |
| 11      | 8+2+1                    | 1011        | 8+3                              | 010100          |
| 12      | 8+4                      | 1100        | 8+3+1                            | 010101          |
| 13      | 8+4+1                    | 1101        | 13                               | 100000          |
| 14      | 8+4+2                    | 1110        | 13+1                             | 100001          |
| 15      | 8+4+2+1                  | 1111        | 13+2                             | 100010          |
| 16      | 16                       | 10000       | 13+3                             | 100100          |
