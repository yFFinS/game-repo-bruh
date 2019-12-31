from terrain import TILE_SIZE

class PathFinder:
    def __init__(self, grid):
        self.grid = [[Node((x, y), grid[y][x]) for x in range(len(grid[0]))] for y in range(len(grid))]
        self.paths = [[0] * len(self.grid[0])] * len(self.grid)
        self.closedset = set()
        self.openset = set()
        self.path = None

    def children(self, node, grid):
        x, y = node.x, node.y
        links = [grid[y + dy][x + dx] for (dx, dy) in [(0, 1), (0, -1), (1, 1), (1, -1), (1, 0), (-1, 0), (-1, 1), (-1, -1)]
                 if -1 < x + dx < len(grid[0]) and -1 < y + dy < len(grid)]
        return [link for link in links if link.type != 1]

    def find(self, pos1, pos2):
        start = self.grid[pos1[1]][pos1[0]]
        end = self.grid[pos2[1]][pos2[0]]
        openset = self.openset
        closedset = self.closedset
        current = start
        openset.add(current)
        if openset:
            current = min(openset, key=lambda o: o.G + o.H)
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                self.path = [(node.x, node.y) for node in path[::-1]]
                return
            openset.remove(current)
            closedset.add(current)
            for node in self.children(current, self.grid):
                if node in closedset:
                    continue
                if node in openset:
                    new_g = current.G + current.move_cost(node)
                    if node.G > new_g:
                        node.G = new_g
                        node.parent = current
                else:
                    node.G = current.G + current.move_cost(node)
                    node.H = self.h_cost(node, end)
                    node.parent = current
                    openset.add(node)

    def h_cost(self, node, end):
        dx, dy = abs(node.x - end.x), abs(node.y - end.y)
        return 4 * min(dx, dy) + 10 * max(dx, dy)

    def next(self, pos):
        if self.path is None:
            return pos
        converted_pos = pos[0] // TILE_SIZE * TILE_SIZE, pos[1] // TILE_SIZE * TILE_SIZE
        if converted_pos in self.path:
            self.path = self.path[self.path.index(converted_pos):]
        return self.path[0]



class Node:
    def __init__(self, pos, node_type):
        self.type = node_type
        self.x, self.y = pos
        self.parent = None
        self.H = 0
        self.G = 0

    def move_cost(self, other):
        return 10 if other.x == self.x or other.y == self.y else 14