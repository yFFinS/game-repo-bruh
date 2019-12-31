from terrain import TILE_SIZE
from entities import CANPATHFIND


class PathFinder:
    def __init__(self, grid):
        self.grid = [[0 if grid[y][x].transparent else 1 for x in range(len(grid[0]))] for y in range(len(grid))]
        self.grids = dict()
        self.closedsets = dict()
        self.opensets = dict()
        self.paths = dict()
        self.cached_paths = dict()
        self.ends = dict()
        self.currents = dict()

    def children(self, node, grid):
        x, y = node.x, node.y
        links = [grid[y + dy][x + dx] for (dx, dy) in
                 [(0, 1), (0, -1), (1, 1), (1, -1), (1, 0), (-1, 0), (-1, 1), (-1, -1)]
                 if -1 < x + dx < len(grid[0]) and -1 < y + dy < len(grid)]
        return [link for link in links if link.type != 1]

    def find(self, parent, pos1, pos2):
        if not parent.conditions[CANPATHFIND]:
            return
        if parent not in self.grids:
            self.grids[parent] = [[Node((x, y), self.grid[y][x]) for x in range(len(self.grid[0]))] for y in
                                  range(len(self.grid))]
            self.paths[parent] = [None, 0]
        x1, y1 = map(lambda x: round(x) // TILE_SIZE, pos1)
        x2, y2 = map(lambda x: round(x) // TILE_SIZE, pos2)
        start = self.grids[parent][y1][x1]
        end = self.grids[parent][y2][x2]
        if parent not in self.ends or self.ends[parent] != end:
            start.reset()
            end.reset()

            self.opensets[parent] = set()
            self.closedsets[parent] = set()
            self.ends[parent] = end
            self.currents[parent] = start
            self.opensets[parent].add(self.currents[parent])
        if self.opensets[parent]:
            self.currents[parent] = min(self.opensets[parent], key=lambda o: o.G + o.H)
            if self.currents[parent] == end:
                path = []
                while self.currents[parent].parent:
                    path.append(self.currents[parent])
                    self.currents[parent] = self.currents[parent].parent
                path.append(self.currents[parent])
                self.paths[parent] = [[(node.x * TILE_SIZE + TILE_SIZE // 2, node.y * TILE_SIZE + TILE_SIZE // 2) for
                                      node in path[::-1]], 0]
                parent.conditions[CANPATHFIND] = False
                parent.timers['pathfind'].start()
                return
            self.opensets[parent].remove(self.currents[parent])
            self.closedsets[parent].add(self.currents[parent])
            for node in self.children(self.currents[parent], self.grids[parent]):
                if node in self.closedsets[parent]:
                    continue
                adj1, adj2 = self.grids[parent][self.currents[parent].y][node.x],\
                             self.grids[parent][node.y][self.currents[parent].x]
                if node in self.opensets[parent]:
                    new_g = self.currents[parent].G + self.currents[parent].move_cost(node, adj1, adj2)
                    if node.G > new_g:
                        node.G = new_g
                        node.parent = self.currents[parent]
                else:
                    node.G = self.currents[parent].G + self.currents[parent].move_cost(node, adj1, adj2)
                    node.H = self.h_cost(node, end)
                    node.parent = self.currents[parent]
                    self.opensets[parent].add(node)

    def h_cost(self, node, end):
        dx, dy = abs(node.x - end.x), abs(node.y - end.y)
        return 4 * min(dx, dy) + 10 * max(dx, dy)

    def next(self, parent):
        pos = parent.get_pos()
        if self.paths[parent][0] is None:
            return pos
        pos = round(pos[0]) // TILE_SIZE * TILE_SIZE + TILE_SIZE // 2, round(
            pos[1]) // TILE_SIZE * TILE_SIZE + TILE_SIZE // 2
        if pos in self.paths[parent][0]:
            self.paths[parent][1] = min(self.paths[parent][0].index(pos) + 1, len(self.paths[parent][0]) - 1)
        return self.paths[parent][0][self.paths[parent][1]] if self.paths[parent][0] else pos

    def get_path(self, parent):
        return self.paths[parent][0][self.paths[parent][1]:] if self.paths[parent][0] else [parent.get_pos()]


class Node:
    def __init__(self, pos, node_type):
        self.type = node_type
        self.x, self.y = pos
        self.parent = None
        self.H = 0
        self.G = 0

    def move_cost(self, other, adj1, adj2):
        return 10 if other.x == self.x or other.y == self.y else 14 if adj1.type != 1 and adj2.type != 1 else 10000

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def reset(self):
        self.H = 0
        self.G = 0
        self.parent = None
