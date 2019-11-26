# Kaleidoscope Solver

This is an attempt to make a basic solver for the Kaleidoscope Classic, a polynomino packing puzzle with an 8x8 board and 18 checkered pieces, that can be arranged in over billlions of ways, and any single pattern formed can have anywhere from millions to a single solution. Given a specific pattern, a solution is an arrangement of the pieces, flipped or otherwise, that form the pattern.

![Screenshot 2019-11-26 at 1 54 32 PM](https://user-images.githubusercontent.com/5196925/69641184-bfa24900-1085-11ea-8c4a-b00718bf666a.png)

The algorithm makes use of finding islands, edge matching, piece size and crookedness heuristics and backtracking to find the best fitting pieces.

Solver runs for a few patterns:

### The Car Reflection
![car](https://user-images.githubusercontent.com/5196925/69641936-05134600-1087-11ea-99d5-e5d5d6ce3bd6.png)

![Screenshot 2019-11-26 at 9 28 56 AM](https://user-images.githubusercontent.com/5196925/69641497-5242e800-1086-11ea-959b-6522eab39d62.png)
![Screenshot 2019-11-26 at 9 26 32 AM](https://user-images.githubusercontent.com/5196925/69641500-53741500-1086-11ea-9773-c3db74b9bb2a.png)

### The Number 12
![12_patt](https://user-images.githubusercontent.com/5196925/69641921-004e9200-1087-11ea-8c48-700c48ce5cbb.png)

![Screenshot 2019-11-26 at 9 34 07 AM](https://user-images.githubusercontent.com/5196925/69641567-743c6a80-1086-11ea-9171-a7c76d254c4d.png)
![Screenshot 2019-11-26 at 9 33 58 AM](https://user-images.githubusercontent.com/5196925/69641573-76062e00-1086-11ea-8cdd-02a3ad4baacf.png)

### No single squares
![no_single_squares_sol](https://user-images.githubusercontent.com/5196925/69641942-093f6380-1087-11ea-917e-a02f97a26209.png)

![Screenshot 2019-11-26 at 9 32 55 AM](https://user-images.githubusercontent.com/5196925/69641705-b2d22500-1086-11ea-8f8b-c3c9cf9dbe40.png)
![Screenshot 2019-11-26 at 9 32 47 AM](https://user-images.githubusercontent.com/5196925/69641713-b49be880-1086-11ea-92e3-5bff6fcf0701.png)
![no_single_squares](https://user-images.githubusercontent.com/5196925/69643268-1eb58d00-1089-11ea-972e-4f88b97108a3.png)

### Algorithm:

Try a set of moves until the board has no remaing holes and no remaining pieces, or no moves.

Preprocess:
1. Define teritory (Separate holes) by adjacent same color cell edges.
2. [unquestionable] Check if any holes have single-piece solution, and place them
3. see if the magic wand (octomino) fits any of the holes (practically done in the first step)

While pieces remaining:
1. Make a size progression for each hole by cell count, wrt available pieces.
2. Look for the densest windows across holes. Rank by edge/cell density.
3. Fit pieces to each hole,  rank each window-hole combination by
    a. edges matched
    b. crookedness hueristic of pieces 
    c. span (only small_wand, or in rare cases magic wand)
4. Select the winner piece, but keep a set of other next best moves
5. If no moves: 
    a. Try a different sized piece, according to a different progression
    b. If still no moves, backtrack to parent and try its sibling.

Performance is still a bit choppy for highly checkered patterns, which can be solved with more robust pruning in the backtracking tree.

Can be upgraded into a playable web-app :)
