# bin-register

```python
def to_bin(n):
    if n == 0: return 0
    elif n == 1: return 1
    # Quotient (left side) + Remainder (right side)
    else: return to_bin(n // 2) * 10 + to_bin(n % 2)
```

Standard Binary (2^n):
The decimal number 3 in binary is 0011.

- This represents (1 _ 2^1) + (1 _ 2^0) = 2 + 1 = 3

In a hardware sense, a Binary Adder is a masterpiece of efficiency because it uses the absolute minimum number of logic gates to process a carry.

1. The Binary Full Adder (Minimalist)
   A standard binary full adder adds three bits (A, B, and a Carry-in) and outputs a Sum and a Carry-out. It only requires 5 logic gates.

- Logic Gates Used: 2 XOR, 2 AND, 1 OR.
- The "Trick": It only cares about the current column and the one to its immediate left. The carry "ripples" in one direction.

## Equation:

- $Sum = (A \oplus B) \oplus C_{in}$
  In digital electronics and Boolean algebra, the equation $Sum = (A \oplus B) \oplus C_{in}$ translates to:
  "The sum is equal to A exclusive-OR B, exclusive-OR carry-in."
  Key Components

* Sum: The result of the addition operation.
* $\oplus$ (Exclusive-OR / XOR): A logical operation that outputs true (1) only if the number of true inputs is odd.
* $A$ and $B$: The two primary input bits being added.
* $C_{in}$ (Carry-in): The carry bit received from a previous, less significant bit addition.

Context: The Full Adder
This specific formula defines the Sum output of a Full Adder circuit. In this context, the operation can also be described as:

- Parity Check: The sum bit is 1 if an odd number of inputs ($A$, $B$, and $C_{in}$) are 1.
- Modulo-2 Addition: Adding the three bits together and keeping only the remainder after dividing by 2 ($A + B + C_{in} \pmod 2$).

## Carry-out ($C_{out}$) of a full adder is typically expressed in one of two ways:

1. Standard Logic Form
   $C_{out} = (A \cdot B) + (C_{in} \cdot (A \oplus B))$
   In plain English, this translates to:
   "Carry-out is equal to (A AND B) OR (Carry-in AND (A XOR B))."
   This version is most common because it reuses the $A \oplus B$ result already calculated for the Sum, making it efficient to build with physical gates.
2. Simplified (Sum-of-Products) Form
   $C_{out} = AB + BC_{in} + AC_{in}$
   In plain English:
   "Carry-out is equal to (A AND B) OR (B AND Carry-in) OR (A AND Carry-in)."
   What this formula means
   The Carry-out bit is "1" if at least two of the three inputs are "1". [8, 10, 11]

- Generate ($A \cdot B$): If both A and B are 1, they "generate" a carry regardless of what the previous stage sent.
- Propagate ($C_{in} \cdot (A \oplus B)$): If only one of A or B is 1, they "propagate" the incoming carry to the next stage.

The truth table for a full adder shows every possible combination of the three inputs ($A$, $B$, and $C_{in}$) and the resulting Sum and Carry-out ($C_{out}$).

| $A$ | $B$ | $C_{in}$ | Sum ($S$) | Carry-out ($C_{out}$) |
| --- | --- | -------- | --------- | --------------------- |
| 0   | 0   | 0        | 0         | 0                     |
| 0   | 0   | 1        | 1         | 0                     |
| 0   | 1   | 0        | 1         | 0                     |
| 0   | 1   | 1        | 0         | 1                     |
| 1   | 0   | 0        | 1         | 0                     |
| 1   | 0   | 1        | 0         | 1                     |
| 1   | 1   | 0        | 0         | 1                     |
| 1   | 1   | 1        | 1         | 1                     |

How to read this table:

- Sum is 1 whenever there is an odd number of input 1s (1 or 3 total).
- Carry-out is 1 whenever there are two or more input 1s.
- Row 8 (All 1s): When $A$, $B$, and $C_{in}$ are all 1, the total is 3. In binary, 3 is represented as 11, meaning both the Sum and Carry-out bits are 1.

# φ-Register

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

- (6) contains a full (5) tree on the left.
- (6) contains a full (4) tree on the right.

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
| 17      | 16+1                     | 10001       | 13+3+1                           | 100101          |
| 18      | 16+2                     | 10010       | 13+5                             | 101000          |
| 19      | 16+2+1                   | 10011       | 13+5+1                           | 101001          |
| 20      | 16+4                     | 10100       | 13+5+2                           | 101010          |
| 21      | 16+4+1                   | 10101       | 21                               | 1000000         |

## The Axiom

One identity generates everything:

**F(n) = F(n-1) + F(n-2)**

This isn't a formula you derive — it's the law of the machine. The carry rule, the borrow rule, addition, subtraction, normalization, and error detection all fall out of reading this identity in different directions.

## The Register

A register is an ordered sequence of cells. Each cell holds 0 or 1. Cell _k_ has weight F(k). A register is **valid** when no two adjacent cells both hold 1.

Here's the first self-referential property: the number of valid states in an _n_-cell register is F(n+2). The machine counts its own capacity in its own number system. Nothing external is needed to describe it.

## Arithmetic from the Single Identity

Three operations, all just the axiom rewritten:

**Upward (carry):** Cells k and k+1 both hold 1? Clear both, set cell k+2. That's just F(k) + F(k+1) = F(k+2) — the axiom read left to right.

**Downward (borrow):** Cell k holds 1 and you need to decompose it? Clear k, set cells k-1 and k-2. That's F(k) = F(k-1) + F(k-2) — the axiom read right to left.

**Doubling (resolve a 2):** Raw addition can produce a cell holding "2." Since 2·F(k) = F(k+1) + F(k-2), clear the 2 and set those two cells. This is the axiom applied to F(k) + F(k) = F(k) + F(k-1) + F(k-2) = F(k+1) + F(k-2).

That's the complete arithmetic engine. Addition is raw cell-wise sum followed by sweeping these three rules until the register is valid. Subtraction is alignment plus downward expansion plus normalization. Every operation terminates because carries propagate strictly upward and the register is finite.

## The Clock is Convergence

There's no external clock. You pour values into a register, and the normalization rules cascade like a wavefront until the system settles into a valid state. **Computation is settling.** The settling time is bounded by register width, so it always halts — but the machine's natural rhythm is the propagation speed of carries, not an imposed tick.

This is closer to how physical systems actually compute. A crystal grows until it's stable. A river finds its channel. The φ-register normalizes.

## Error Detection is Free

In any positional system with unconstrained digits, every bit pattern is valid and corruption is silent. Here, the "no adjacent 1s" invariant means any corruption that creates an adjacency is **immediately visible** — and self-correcting by applying the carry rule. The representation itself is a checksum. You don't bolt on parity bits; structural integrity is native.

## Multiplication

Left-shift by one position scales a value by approximately φ. Not exactly — the result may need normalization — but the _structure_ is that shifting is φ-scaling, and the normalization cleanup is bounded.

Multiplying by F(k) specifically: decompose via the recurrence. F(k) = F(k-1) + F(k-2), so `x · F(k) = x · F(k-1) + x · F(k-2)`. This recurses down to `x · F(1) = x` and `x · F(2) = x` (shift-by-one). Multiplication is a tree of additions shaped exactly like the Fibonacci call tree from your original observation. **The algorithm's structure mirrors the number system's structure.** General multiplication between two arbitrary values decomposes the multiplier into its Zeckendorf digits and sums the shifted copies — analogous to long multiplication, but with φ-spaced shifts instead of uniform ones.

## Comparison, Branching, Division

**Comparison** is scan-from-top: first cell that differs determines order. Same principle as any positional system; the non-adjacency constraint doesn't interfere.

**Division** is repeated subtraction with φ-scaled shifting. Long division, but each trial subtraction shifts by Fibonacci positions. The quotient accumulates in Zeckendorf form naturally.

**The native gate** that doesn't exist elsewhere: **NORMALIZE.** Every other logic operation (AND, OR, NOT on raw cells) can produce invalid states. NORMALIZE sweeps the register back to validity. It's the primitive. It _is_ the computation.

## What This Machine is Good At

The φ-machine isn't a worse version of something else. It has intrinsic properties:

**Self-similar scaling.** Every substructure at scale n contains the structure at n-1 and n-2. This maps naturally to problems that are themselves recursive or fractal — tree traversals, branching processes, growth models.

**Built-in redundancy detection.** The adjacency constraint means the representation space is sparser than the raw bit space. This is a feature — it means encoding carries more structure per symbol, at the cost of more symbols per value.

**Natural compression delimiter.** The sequence `11` can never appear inside a valid number, so it's a free end-of-number marker. You can concatenate φ-encoded values in a stream with zero framing overhead. This is why Fibonacci codes already exist in data compression — they fell out of this system, not out of the legacy one.

**Gentle overflow.** When a register fills, it grows by one cell, increasing capacity by a factor of φ ≈ 1.618 rather than doubling. Growth is spiral, not exponential.
