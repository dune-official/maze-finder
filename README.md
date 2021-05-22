# maze-finder
## My very own algorithm specified on solving 2D mazes 

Okay, consider this: you are held at gunpoint and need to find the shortest path of a 2d maze. Well, worry no more, because I got you.

Imagine a maze with '#' as walls, 'S' as start point and 'E' as exit. There are no diagonal shifts allowed, the start and end point mustn't be in an edge of the maze
and there must be at least one solution. 
The use of any third party lib is prohibited.

For example:
```
###S####
# # #  #
# # ####
E #    #
# # ## #
# # ## #
#      #
########
```

Solved:
```
###.####
# #.#  #
# #.####
..#.   #
#.#.## #
#.#.## #
#...   #
########
```

Maybe you can draw some inspiration from my code about the A* algorithm I used to solve the problem.

- Algorithm used: A* (my heuristic is the manhattan distance from the point to the end point 'E')
- Language used: python
- Bugs left: probably some (maybe not put the 'S' across the 'E' yet, yes, I know where the bug lies but I am too lazy to fix it rn)

Please provide feedback or try it with your own maze
