# The Matrix Identity

The adjacency constraint, the matrix symmetry, the Fibonacci coding delimiter, and the binary-vs-Fibonacci weight sequences are all the same structural fact viewed from different projections. The matrix is the native object. Everything else is a cipher on top of it.

## The Native Object

The Fibonacci recurrence is a linear map. Applied once, it advances a pair of consecutive values by one step:

```
[F(k+1)]   [1 1]   [F(k)  ]
[F(k)  ] = [1 0] × [F(k-1)]
```

Applied n times, it produces:

```
M^n = [F(n+1)  F(n)  ]
      [F(n)    F(n-1)]
```

Four entries. Three distinct values (the matrix is symmetric). One recurrence linking them: `[0][0] = [0][1] + [1][1]`, i.e. `F(n+1) = F(n) + F(n-1)`. The recurrence isn't a rule imposed on the entries — it's readable directly off the geometry. Row/column structure _is_ the recurrence.

## Four Projections of One Fact

### 1. The Adjacency Constraint (1D Register)

In a flat Zeckendorf register, each cell is an independent switch with a Fibonacci weight. The weights have a dependency — `F(k) + F(k+1) = F(k+2)` — but the cells don't know about it. Independent addressing + dependent weights = redundancy. The no-adjacent-1s rule is duct tape over a dimensional mismatch: a 2D relationship (each weight depends on two neighbors) forced into a 1D address space.

### 2. The Matrix Symmetry (2D Index)

In the matrix, `[0,1]` and `[1,0]` both give `F(n)`. Two addresses, one value. The redundancy that the 1D register forbids, the matrix expresses as symmetry. Four states, three distinct outputs. The constraint didn't disappear — it changed form. In 1D, one of four states is _forbidden_. In 2D, one of four states is _redundant_.

### 3. The Fibonacci Coding Delimiter

The bit pattern `11` can never appear inside a valid Zeckendorf representation. So it's repurposed as an end-of-number marker in Fibonacci codes. This works because `11` corresponds to the redundant matrix state — `[1,1]` selects `F(n-1)`, which carries no information that `[0,0]` and `[0,1]` don't already determine. The delimiter falls out of the matrix's symmetry.

### 4. The Weight Sequence Fork

Let `11` live as a valid state (a matrix index selecting `F(n-1)`) and the adjacency constraint vanishes. With it goes the Fibonacci weight sequence — the next position no longer needs weight `F(k+2)` because the carry that would have produced it was absorbed. The weights collapse to powers of 2. Binary and Fibonacci aren't competing systems. They're what happens when you do or don't allow the redundant matrix state into your encoding.

```
Allow [1,1]:   weights = 1, 2, 4, 8, 16...    → binary
Forbid [1,1]:  weights = 1, 2, 3, 5, 8, 13... → Fibonacci
Same matrix. Different cipher.
```

## What Composition Looks Like on Each Side

The matrix preserves its invariants under multiplication automatically. No normalization, no sweep — the dot product structure makes invalid states unreachable:

```
M^a × M^b = M^(a+b)

Symmetry preserved:  [0][1] = [1][0]  always
Recurrence preserved: [0][0] = [0][1] + [1][1]  always
```

The 1D register preserves its invariants via normalization. Pour values in, sweep for violations, settle. The adjacency constraint is maintained by an explicit process because the flat address space doesn't enforce it structurally.

```
1D:      valid in + valid in → possibly invalid → normalize → valid out
Matrix:  valid in × valid in → valid out (guaranteed by dot product)
```

The normalization sweep in the 1D register is doing from the outside what the dot product does from the inside.

## The Dual Cost Structure

The matrix register and the 1D register are duals. Each is native where the other is expensive:

```
                        1D φ-Register         Matrix Register
Value addition          native (pour+norm)    expensive (decompose)
Index composition       expensive (matrix)    native (multiply)
Normalization           required              impossible to violate
Arbitrary integers      direct                only Fibonacci-indexed
Inspectable digits      yes                   no (opaque pair)
```

Neither is better. They're projections optimized for different operations on the same underlying structure.

## The Core Insight

The φ-register isn't an alternative to binary. Both are lossy projections of a 2D structure onto a 1D bit string, each preserving different properties and paying different costs. The matrix is where they meet — binary-indexed rows and columns, Fibonacci-valued entries. Binary as the address bus, Fibonacci as the data bus, the matrix as the interface.
