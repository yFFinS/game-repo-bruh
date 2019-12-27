from main import WIDTH, HEIGHT


class Camera:
    def __init__(self, width, height, target):
        self.target = target
        self.x = target.x
        self.y = target.y
        self.w = width
        self.h = height
    
    def update(self):
        if self.w - WIDTH // 2 > self.target.x > WIDTH // 2:
            self.x = self.target.x
        else:
            if self.target.x <= WIDTH // 2:
                self.x = WIDTH // 2
            else:
                self.x = self.w - WIDTH // 2
        if self.h - HEIGHT // 2 > self.target.y > HEIGHT // 2:
            self.y = self.target.y
        else:
            if self.target.y <= HEIGHT // 2:
                self.y = HEIGHT // 2
            else:
                self.y = self.h - HEIGHT // 2

    def blit_pos(self):
        return -(self.x - WIDTH // 2), -(self.y - HEIGHT // 2)