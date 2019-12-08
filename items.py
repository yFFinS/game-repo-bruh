import pygame


class Item:
    def __init__(self, name):
        self.name = name


class Weapon(Item):
    def __init__(self, name, damage=0, attack_speed=0, base_attack_time=0, attack_range=0, attack_width=0, durability=0,
                 special_effect=None):
        super().__init__(name)
        self.damage = damage
        self.attack_speed = attack_speed
        self.base_attack_time = base_attack_time
        self.durability = durability
        self.special_effect = special_effect
        self.attack_range = attack_range
        self.attack_width = attack_width
        self.image = pygame.image.load('images/weapon.png')