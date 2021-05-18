def manhattan(coordinate1: tuple, coordinate2: tuple) -> int:
    """Returns the manhattan distance from coordinate1 to coordinate2"""
    if coordinate1 is not None and coordinate2 is not None:
        x1, y1 = coordinate1
        x2, y2 = coordinate2
        return abs(x1 - x2) + abs(y1 - y2)
    return 0


def minnot(sequence: dict, comp_sequence: list):
    """Returns the minimum value of sequence which is not in comp_sequence."""
    for element in comp_sequence:
        try:
            del sequence[element]
        except KeyError:
            pass

    return min(sequence, key=lambda x: sequence[x])


class Infinite:

    def __gt__(self, other):
        """Infinite can only be greater than every object, not smaller"""
        return True

    def __ge__(self, other):
        return False

    def __le__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __add__(self, other):
        return other

    def __sub__(self, other):
        return other


class Maze:

    def __init__(self, filepath):
        self.filepath = filepath
        self.content = open(self.filepath, 'r').read().splitlines()
        self.width = len(max(self.content, key=len))  # the length of the widest element inside the maze
        self.height = len(self.content)

        # the start and end also count as free segments
        self.free_segments = self.find(' ') + self.find('E') + self.find('S')
        self.relations = self.get_relations()

        # A* algorithm
        self.distances = self.prep_distances()

    def __getitem__(self, index):
        """Defines what gets returned when I do self[coordinate]"""
        if isinstance(index, int):
            return self.content[index]
        elif isinstance(index, tuple):
            return self.content[index[0]][index[1]]

    def __setitem__(self, index, item: str):
        """Defines what happens when I try to assign a value to self[coordinate].
        Actually only gets used in the last step"""
        if isinstance(index, int):
            self.content[index] = item
        elif isinstance(index, tuple):
            self.content = list(map(list, self.content))
            self.content[index[0]][index[1]] = item
            self.content = list(map(lambda x: ''.join(x), self.content))

    def __str__(self):
        """Returns a nice version of the maze for printing out"""
        printout = list(map(lambda x_: list(x_), self.content))

        # insert numbers on the side of the lists
        for x, row in enumerate(printout):
            row.append(str(x))
        # insert numbers above for a coordinate system
        printout.insert(0, list(range(len(self.content[0]))))
        printout[0] = list(map(str, printout[0]))

        for x, row in enumerate(printout):
            printout[x] = '  '.join(row)
        return '\n'.join(printout)

    def find(self, to_find) -> list:
        """Simple function that returns all coordinates that have to_find as value"""
        found = []
        for x, row in enumerate(self.content):
            for y, element in enumerate(row):
                if element == to_find:
                    found.append((x, y))
        if not found:
            raise FileNotFoundError(f'{to_find} not found')
        return found

    def get_relations(self):
        """Gets all relations of all free segments (valid nodes)
        meaning that one free segment has all other free segments it touches in one list"""

        all_coordinates = {}
        sibling_coordinates = []
        for coord_ in self.free_segments:
            around = self.look_around(coord_)
            for direction in around:
                # there are values in 'around' which are not a dictionary
                if isinstance(around[direction], dict):
                    if around[direction]['free'] or around[direction]['S'] or around[direction]['E']:
                        sibling_coordinates.append(around[direction]['coordinate'])

            all_coordinates.update({coord_: sibling_coordinates})
            sibling_coordinates = []

        return all_coordinates

    def look_around(self, coordinate_: tuple) -> dict:
        """This function checks the direct surroundings of one coordinate/node"""
        x, y = coordinate_
        omit = None

        x_pair = (x - 1, x + 1)
        y_pair = (y - 1, y + 1)

        if not x:
            # we omit to look up because x is zero
            omit = 'up'
        elif x == self.height-1:
            omit = 'down'

        if not y:
            omit = 'left'
        elif y == self.width-1:
            omit = 'right'

        o = {
            "up": {
                "coordinate": (x_pair[0], y),
                "free": self[x_pair[0], y] == ' ',
                "wall": self[x_pair[0], y] == '#',
                "S": self[x_pair[0], y] == 'S',
                "E": self[x_pair[0], y] == 'E'
            } if omit != 'up' else None,
            "down": {
                "coordinate": (x_pair[1], y),
                "free": self[x_pair[1], y] == ' ',
                "wall": self[x_pair[1], y] == '#',
                "S": self[x_pair[1], y] == 'S',
                "E": self[x_pair[1], y] == 'E'
            } if omit != 'down' else None,
            "right": {
                "coordinate": (x, y_pair[1]),
                "free": self[x, y_pair[1]] == ' ',
                "wall": self[x, y_pair[1]] == '#',
                "S": self[x, y_pair[1]] == 'S',
                "E": self[x, y_pair[1]] == 'E'
            } if omit != 'right' else None,
            "left": {
                "coordinate": (x, y_pair[0]),
                "free": self[x, y_pair[0]] == ' ',
                "wall": self[x, y_pair[0]] == '#',
                "S": self[x, y_pair[0]] == 'S',
                "E": self[x, y_pair[0]] == 'E'
            } if omit != 'left' else None
        }

        if omit is not None:
            del o[omit]

        free_spaces = len([x for x in o if o[x]['free']])
        walls = len([x for x in o if o[x]['wall']])
        s = len([x for x in o if o[x]['S']])
        e = len([x for x in o if o[x]['E']])
        o.update({"free_spaces": free_spaces, "walls": walls, "s_count": s, "e_count": e})

        return o

    def is_closed(self) -> bool:
        """The closed function checks if the maze is even solvable or not"""

        e_ = self.find('E')[0]
        s_ = self.find('S')[0]
        checking = [e_]
        covered = []

        while checking:
            # checking is the queue for all the nodes that need to be checked
            # it gets smaller when it iterates over an exhausted node, otherwise it gets bigger
            # the goal of this algorithm is to exhaust all nodes until the queue is empty
            # if the start position is in the covered section, the maze is solvable
            for element in checking:
                around_ = list(set(self.relations[element]).difference(covered))
                covered.append(element)
                if not len(around_):
                    del checking[checking.index(element)]
                    continue
                for relation in around_:
                    checking.append(relation)

        return s_ not in covered

    def fill(self, coordinates_: list, filler: str = '.'):
        """Creates another maze and fills it with the input"""
        duplicate = Maze(self.filepath)
        for coord_ in coordinates_:
            duplicate[coord_] = filler
        return duplicate

    # functions relating to the A* algorithm
    def get_cost(self, coord1_, coord2_):
        """Cost function that encourages walking towards the Exit, penalizes walking away from it
        and penalizes (somehow) 'dilly-dally' (walking parallel to the Exit)"""

        e_ = self.find('E')[0]
        e_direction = None
        e_direction_opposite = None

        if not e_[0]:
            e_direction_opposite = 'down'
            e_direction = 'up'
        if e_[0] == self.height:
            e_direction_opposite = 'up'
            e_direction = 'down'
        if not e_[1]:
            e_direction_opposite = 'right'
            e_direction = 'left'
        if e_[1] == self.width:
            e_direction_opposite = 'left'
            e_direction = 'right'

        around = self.look_around(coord1_)
        for direction in around:
            if isinstance(around[direction], dict):
                if around[direction]['coordinate'] == coord2_:

                    # the cost for moving away from the exit is very high
                    if direction == e_direction_opposite:
                        return 100
                    # the cost for moving towards the exist is very low on the other hand
                    elif direction == e_direction:
                        return 1
                    # any other move (parallel to E)
                    else:
                        return 10

        # if there is no relation at all, the cost is infinite because it is not allowed to skip a field
        return Infinite()

    def h(self, coordinate_: tuple):
        """The heuristic function I chose is the manhattan distance from each object to the Exit"""
        e_ = self.find('E')[0]
        return manhattan(coordinate_, e_)

    def prep_distances(self):
        """Gives all the segments/nodes a distance of Infinite and the start node a distance of 0+h(S)"""
        distances = {}
        s = self.find('S')[0]
        for segment in self.free_segments:
            distances.update({segment: Infinite()})

        distances.update({s: 0})
        return distances

    def get_path(self):
        """According to the A* algorithm"""
        # before the algorithm starts, the maze gets validated
        if self.is_closed():
            raise BlockingIOError('The maze is not solvable')

        # we start with s
        checking = self.find('S')[0]
        covered = [checking]

        # stores only the nodes with at least two connecting nodes for a traceback
        successful_connections = []

        # stores all adjacent nodes with their relative cost
        adjacent_node_costs = {}

        e_ = self.find('E')[0]

        while checking != e_:

            # relations of all the coordinates that are not in the path
            relations_of_checking = list(set(self.relations[checking]).difference(covered))
            if not relations_of_checking:
                # checking is now the last 'successful' node
                # the code goes back and since the way is already covered it can't go there again
                try:
                    checking = successful_connections[-1]
                    del successful_connections[-1]
                    continue
                except IndexError:
                    print('E can not be reached, the maze is therefore invalid')
                    return checking

            else:
                # this means that the node has at least one connection (meaning it is 'successful')
                # and could lead to the exit, until it is exhausted
                successful_connections.append(checking)

            for relation in relations_of_checking:
                # get the distance from the start to the current node plus the heuristic
                last_distance = self.distances.get(checking, 0)
                current_distance = last_distance + self.get_cost(checking, relation)
                current_cost = current_distance + self.h(relation)

                # represents all nodes and its costs
                adjacent_node_costs[relation] = current_cost

            # the cheapest node gets chosen
            cheapest_node = min(adjacent_node_costs, key=lambda x: adjacent_node_costs[x])
            covered.append(cheapest_node)
            adjacent_node_costs = {}

            # the node connections is the last successful node (one that is not a dead end)
            checking = cheapest_node

        return successful_connections + [e_]
