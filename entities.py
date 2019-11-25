
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 300

    def get_pos(self):
        return self.x, self.y

    def get_velocity(self):
        return self.velocity

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def move(self, x, y):
        self.x = x
        self.y = y
