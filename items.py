import pygame

from functions import load_image


class Item(pygame.sprite.Sprite):
    def __init__(self, group, name, texture, size):
        super().__init__(group)
        self.name = name
        self.size = size
        self.image = load_image(texture)
        self.animation_frames = self.image.get_width() // self.size[0]


class Weapon(Item):
    def __init__(self, group, name, texture, size=None, damage=0, attack_speed=0, base_attack_time=0,
                 attack_range=None,
                 durability=0, special_effect=None):
        super().__init__(group, name, texture, size)
        self.damage = damage
        self.attack_speed = attack_speed
        self.base_attack_time = base_attack_time
        self.durability = durability
        self.special_effect = special_effect
        if attack_range is None:
            self.attack_range = max(size)
        else:
            self.attack_range = attack_range

    def get_current_sprite(self, cur_frame, frames):
        ratio = cur_frame / frames
        animation_frame = 0
        for i in range(self.image.get_width() // self.size[0], -1, -1):
            if ratio * self.animation_frames >= i:
                animation_frame = i
                break
        return int(self.size[0] / self.animation_frames / 2) * animation_frame, (
            animation_frame * self.size[0], 0, *self.size)
