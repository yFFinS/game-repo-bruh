import pygame

pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.mixer.init()
pygame.init()
pygame.display.set_caption('Game')
info = pygame.display.Info()
width = info.current_w
height = info.current_h
screen = pygame.display.set_mode((width, height),
                                 pygame.FULLSCREEN | pygame.HWSURFACE | pygame.RESIZABLE, 32)

from entities import *
from terrain import Terrain
from menu import Menu
from camera import *
from projectiles import *
from pathfinder import PathFinder
from particles import Particle


class Game:  # Main class
    def __init__(self):  # Init

        # FPS clock
        self.screen = screen
        self.width = width
        self.height = height
        self._music = True
        self._sounds = True
        self.clock = pygame.time.Clock()
        self.death_sounds = [load_sound('death' + str(i + 1) + '.wav') for i in range(1)]
        load_music('music.mp3')
        hurt_sound = load_sound('bruh.mp3')
        pygame.mixer.music.play(10 ** 8)

        self.sprite_groups = None

        self.conditions = None

        self.keys_pressed = None

        self.terrain = None
        self.screen2 = None
        self.player = None
        self.camera = None
        self.menu = None
        self.paths = None
        self.pathfinder = None
        self.color_mask = None
        self.reset()
        self.start_screen()

    def handle_keys(self):
        if pygame.K_F3 in self.keys_pressed:
            self.conditions[DEBUGGING] = not self.conditions[DEBUGGING]
            self.keys_pressed.remove(pygame.K_F3)
        if pygame.K_PAUSE in self.keys_pressed:
            self.conditions[PAUSED] = not self.conditions[PAUSED]
            self.keys_pressed.remove(pygame.K_PAUSE)
        if pygame.K_ESCAPE in self.keys_pressed:
            self.keys_pressed.remove(pygame.K_ESCAPE)
            self.open_menu()
        if pygame.K_F11 in self.keys_pressed:
            self.fullscreen()
            self.keys_pressed.remove(pygame.K_F11)

        if not self.conditions[PAUSED]:
            # Move calculation
            move_d = [0, 0]
            if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
                move_d[1] = -1
            if pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
                move_d[1] = 1
            if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
                move_d[0] = 1
            if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
                move_d[0] = -1
            if move_d[0] > 0:
                self.player.look_angle = 0
            elif move_d[0] < 0:
                self.player.look_angle = 180
            if move_d == [0, 0]:
                self.player.i_moving = False
            else:
                self.player.i_moving = True
            self.move(self.player, *move_d)

    def switch_music(self):
        if self._music:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.play(10 ** 8)
        self._music = not self._music

    def switch_sounds(self):
        switch_sounds()

    def reset(self, level=1):
        pygame.mixer.music.stop()
        pygame.mixer.music.play(10 ** 8)
        self.menu = Menu()
        self.menu.add_button('Continue', (self.width // 2 - 150, 200), target=self.open_menu)
        self.menu.add_button('Music', target=self.switch_music, switch=True)
        self.menu.add_button('Sounds', target=self.switch_sounds, switch=True)
        self.menu.add_button('Quit game', target=self.terminate)

        self.sprite_groups = {k: pygame.sprite.Group() for k in range(20, 30)}

        self.conditions = {k: False for k in range(40, 50)}
        self.conditions[RUNNING] = True
        self.conditions[FULLSCREEN] = True

        self.keys_pressed = []

        self.terrain = Terrain(16 * 3 * 3, 16 * 3 * 3, level)
        self.sprite_groups[CHUNKS] = pygame.sprite.Group(self.terrain.chunks)
        for chunk in self.sprite_groups[CHUNKS]:
            self.sprite_groups[ALL].add(chunk)
        self.screen2 = pygame.Surface((self.width, self.height), pygame.HWSURFACE, 32)
        self.player = Player((self.sprite_groups[ENTITIES], self.sprite_groups[ALL]),
                             (500, 500))
        self.camera = Camera(self.terrain.get_width(), self.terrain.get_height(),
                             self.player, self.width // 2, self.height // 2)

        self.pathfinder = PathFinder(self.terrain.obst_grid)
        self.paths = dict()
        self.sprite_groups[PLAYER].add(self.player)
        self.camera.update()
        
    def open_menu(self):
        self.conditions[INMENU] = not self.conditions[INMENU]
        self.conditions[PAUSED] = True if self.conditions[INMENU] else False
        if self.conditions[PAUSED]:
            pygame.mixer.pause()
            pygame.mixer.music.pause()
        else:
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()

    def resize_window(self, w, h):
        self.width, self.height = w, h
        self.screen = pygame.display.set_mode((w, h), pygame.HWSURFACE | pygame.RESIZABLE, 32)
        self.screen2 = pygame.Surface((self.width, self.height), pygame.HWSURFACE, 32)
        self.camera.centerx = self.width // 2
        self.camera.centery = self.height // 2

    def fullscreen(self):
        if self.conditions[FULLSCREEN]:
            self.resize_window(self.width, self.height)
        else:
            self.width, self.height = width, height
            self.screen = pygame.display.set_mode(
                (width, height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.RESIZABLE, 32)
            self.screen2 = pygame.Surface((width, height), pygame.HWSURFACE, 32)
            self.camera.centerx = self.width // 2
            self.camera.centery = self.height // 2
        self.conditions[FULLSCREEN] = not self.conditions[FULLSCREEN]

    def terminate(self):
        self.conditions[RUNNING] = False

    def handle_signals(self):
        for entity in self.sprite_groups[ENTITIES]:
            if entity.signals[MOVE]:
                self.move(entity, *entity.signals[MOVE])
                entity.signals[MOVE] = None

            if entity.signals[MOVETO]:
                self.move_to(entity, entity.signals[MOVETO])
                entity.signals[MOVETO] = None

            if entity.signals[LAUNCH]:
                p = PROJECTILE_IDS[entity.signals[LAUNCH][0]](
                    (self.sprite_groups[PROJECTILES], self.sprite_groups[ALL]),
                    team=entity.team, damage_amp=entity.bonus_spell_damage)

                p.launch(entity.get_pos(), entity.signals[LAUNCH][1])
                if isinstance(p, SightChecker):
                    p.parent = entity
                entity.signals[LAUNCH] = None

            if entity.signals[PUSH]:
                if entity.signals[PUSH][2] == 0:
                    entity.signals[PUSH] = None
                else:
                    self.move(entity, *entity.signals[PUSH])
                    entity.signals[PUSH] = *entity.signals[PUSH][:2], int(entity.signals[PUSH][2] * 0.95)

            if entity.signals[PARTICLE]:
                for _ in range(entity.signals[PARTICLE][-1]):
                    Particle((self.sprite_groups[PARTICLES], self.sprite_groups[ALL]), *entity.signals[PARTICLE][:-1])
                entity.signals[PARTICLE] = None

            if entity.signals[DEAD]:
                self.kill(entity)

        for projectile in self.sprite_groups[PROJECTILES]:
            if projectile.signals[MOVE]:
                self.move(projectile, *projectile.signals[MOVE])
            if projectile.signals[MOVETO]:
                self.move_to(projectile, projectile.signals[MOVETO])
            if projectile.signals[PARTICLE]:
                for _ in range(projectile.signals[PARTICLE][-1]):
                    Particle((self.sprite_groups[PARTICLES], self.sprite_groups[ALL]),
                             *projectile.signals[PARTICLE][:-1])
            if projectile.signals[DEAD]:
                projectile.die()
            projectile.reset_signals()

        if self.terrain.signals[MESSAGE]:
            msg = Message((self.sprite_groups[ALL],), (0, 100), *self.terrain.signals[MESSAGE])
            msg.rect.x = (self.width - msg.rect.x) // 2
            self.terrain.signals[MESSAGE] = None

        if self.terrain.signals[END]:
            self.next_level(self.terrain.signals[END] + 1)

        for particle in self.sprite_groups[PARTICLES]:
            if particle.signals[MOVE]:
                self.move(particle, *particle.signals[MOVE], True)
                particle.signals[MOVE] = None

    def main(self):  # Main
        while self.conditions[RUNNING]:  # Main loop
            if not self.player.alive():
                self.reset()
            self.process_events()  # Process events
            self.handle_keys()
            if not self.conditions[PAUSED]:

                self.camera.update()

                self.update_sprites()

                self.handle_signals()
                self.terrain.update([self.sprite_groups[ENTITIES], self.sprite_groups[ALL]], self.player)
            self.render_sprites()
            self.handle_messages()
            pygame.draw.rect(self.screen2, (0, 0, 200), self.terrain.end_rect)
            # Screen update
            self.screen.blit(self.screen2, (0, 0))
            if self.conditions[DEBUGGING]:
                self.debug()
            pygame.display.flip()
            # Delay
            self.clock.tick(FPS)

        pygame.quit()

    def move(self, sprite, dx, dy, velocity=0, force_move=False):
        x1, y1 = sprite.get_pos()
        if velocity == 0:
            velocity = float(sprite.velocity)
            if sprite.signals[PUSH]:
                velocity /= 2
            if type(sprite) is Player and (dx * dy == 1 or dx * dy == -1):
                velocity /= sqrt(2)
        if not force_move:
            x2 = max(sprite.rect.w // 2, min(self.terrain.get_width() - sprite.rect.w // 2,
                                                 x1 + dx * velocity / FPS))
            y2 = max(sprite.rect.h // 2, min(self.terrain.get_height() - sprite.rect.h // 2,
                                                 y1 + dy * velocity / FPS))
            sprite.rect.centerx = round(x2)
            sprite.x = x2
            if self.terrain.collide(sprite):
                sprite.rect.centerx = round(x1)
                sprite.x = x1
                x2 = x1
                if isinstance(sprite, Projectile):
                    sprite.die()
            sprite.rect.centery = round(y2)
            sprite.y = y2
            if self.terrain.collide(sprite):
                sprite.rect.centery = round(y1)
                sprite.y = y1
                y2 = y1
                if isinstance(sprite, Projectile):
                    sprite.die()
            if isinstance(sprite, SightChecker)\
                    and pygame.sprite.spritecollide(sprite, self.sprite_groups[PLAYER], False):
                sprite.parent.change_condition(FIGHTING, True)
            if isinstance(sprite, Entity):
                collided = pygame.sprite.spritecollide(sprite, self.sprite_groups[ENTITIES], False)
                if len(collided) > 1:
                    for spr in collided:
                        if spr != sprite:
                            angle = angle_between(sprite.get_pos(), spr.get_pos())
                            dx = cos(angle)
                            dy = sin(angle)
                            if isinstance(sprite, Enemy) and sprite.target == spr:
                                spr.push(dx, dy, 500)
                                spr.hurt(sprite.damage, sprite.get_pos())
                                sprite.change_condition(FIGHTING, True)
                            else:
                                spr.signals[MOVE] = (dx, dy)
                sprite.rect.centerx = round(x1)
                sprite.x = x1
                sprite.rect.centery = round(y1)
                sprite.y = y1
        else:
            x2 = x1 + dx * velocity / max(self.clock.get_fps(), 5)
            y2 = y1 + dy * velocity / max(self.clock.get_fps(), 5)
        if isinstance(sprite, Projectile) and type(sprite) is not SightChecker:
            for col in pygame.sprite.spritecollide(sprite, self.sprite_groups[PROJECTILES], False):
                if col != sprite and not isinstance(col, SightChecker):
                    col.die()
                    sprite.die()
            for spr in sprite.collision(self.sprite_groups[ENTITIES]):
                spr.hurt(sprite.damage, sprite.get_pos())
                angle = angle_between(sprite.get_pos(), spr.get_pos())
                spr.push(cos(angle), sin(angle), sprite.power)
        sprite.rect.centerx, sprite.rect.centery = round(x2), round(y2)
        sprite.x, sprite.y = x2, y2

    def move_to(self, sprite, pos, velocity=0, force_move=False):
        if velocity == 0:
            velocity = float(sprite.velocity)
        if isinstance(sprite, Entity) and not force_move:
            self.pathfinder.find(sprite, sprite.get_pos(), pos)
            new_pos = self.pathfinder.next(sprite)
            if self.paths.get(sprite, None) is None:
                self.paths[sprite] = [[], (randint(0, 255), randint(0, 255), randint(0, 255))]
            self.paths[sprite][0] = [sprite.get_pos()] + self.pathfinder.get_path(sprite)
        else:
            new_pos = pos
        angle = atan2(new_pos[1] - sprite.y, new_pos[0] - sprite.x)
        if hasattr(sprite, 'look_angle'):
            sprite.look_angle = degrees(angle)
        if abs(sprite.x - new_pos[0]) <= 0.01:
            sprite.x = new_pos[0]
            dx = 0
        else:
            dx = cos(angle)
        if abs(sprite.y - new_pos[1]) <= 0.01:
            sprite.y = new_pos[1]
            dy = 0
        else:
            dy = sin(angle)
        if isinstance(sprite, Projectile) and TRANSPARENT in sprite.mods:
            force_move = True
        self.move(sprite, dx, dy, velocity, force_move)

    def create_enemy(self, pos, **kwargs):  # Creates enemy at pos with given kwargs
        enemy_type = choice(ENEMY_IDS)
        enemy_type((self.sprite_groups[ENTITIES], self.sprite_groups[ALL]), pos, **kwargs)

    def kill(self, sprite):
        for _ in range(10):
            Particle((self.sprite_groups[PARTICLES], self.sprite_groups[ALL]), sprite.get_pos(), sprite.particle_color,
                     10, 10, 10, 10)
        sprite.kill()
        if is_sounds():
            choice(self.death_sounds).play()

    def update_sprites(self):
        while len(self.sprite_groups[PARTICLES]) > 100:
            for spr in self.sprite_groups[PARTICLES]:
                spr.kill()
                break
        for sprite in self.sprite_groups[ALL]:
            self.camera.apply_sprite(sprite)
        self.sprite_groups[ALL].update()
        for sprite in self.sprite_groups[ALL]:
            self.camera.apply_sprite(sprite, True)

    def next_level(self, level):
        screen = pygame.Surface((self.width, self.height))
        screen.fill((0, 0, 0))
        screen.set_colorkey((255, 255, 255))
        r = 1000
        pos = tuple(map(round, self.camera.apply_pos(self.player.get_pos(), True)))
        while r > 0:
            pygame.draw.circle(screen, (255, 255, 255), pos, r)
            self.render_sprites()
            self.screen.blit(self.screen2, (0, 0))
            self.screen.blit(screen, (0, 0))
            pygame.display.flip()
            pygame.draw.circle(screen, (0, 0, 0), pos, r)
            r -= 10
            self.clock.tick(FPS)
        self.reset(level)
        screen.fill((0, 0, 0))
        screen.set_colorkey((255, 255, 255))
        r = 0
        pos = tuple(map(round, self.camera.apply_pos(self.player.get_pos(), True)))
        while r < max(self.width, self.height):
            pygame.draw.circle(screen, (255, 255, 255), pos, r)
            self.render_sprites()
            self.screen.blit(self.screen2, (0, 0))
            self.screen.blit(screen, (0, 0))
            pygame.display.flip()
            pygame.draw.circle(screen, (0, 0, 0), pos, r)
            r += 20
            self.clock.tick(FPS)

    def start_screen(self):
        running = True
        font = pygame.font.Font(None, 50)
        line = font.render('Press any key to start...', True, (255, 255, 255))
        counter = 0
        x = 35
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    running = False
            counter += 1
            self.screen.fill((0, 0, 0))
            if counter < x:
                self.screen.blit(line, (self.width // 3, self.height // 3 * 2))
            elif counter > 2 * x:
                counter = 0
            pygame.display.flip()
            self.clock.tick(30)
        self.main()

    def render_sprites(self):
        for sprite in self.sprite_groups[ALL]:
            self.camera.apply_sprite(sprite)
        visible_area = pygame.sprite.Sprite()
        visible_area.rect = pygame.rect.Rect([0, 0, self.width, self.height])
        visible_sprites = pygame.sprite.Group(pygame.sprite.spritecollide(visible_area, self.sprite_groups[ALL], False))
        visible_sprites.draw(self.screen2)
        for sprite in visible_sprites:
            visible_sprites.remove(sprite)

        if self.conditions[INMENU]:
            self.menu.render(self.screen2)
        for sprite in self.sprite_groups[ALL]:
            self.camera.apply_sprite(sprite, True)

    def delete_enemy(self, pos):  # Deletes enemy at pos
        x, y = pos
        for entity in self.sprite_groups[ENTITIES]:
            if entity.collision((x, y)):
                entity.kill()
                return

    def handle_messages(self):
        self.sprite_groups[MESSAGES].draw(self.screen2)
        self.sprite_groups[MESSAGES].update()

    def change_camera_target(self, pos):
        for sprite in set(self.sprite_groups[ENTITIES]) | set(self.sprite_groups[PROJECTILES]):
            if sprite.rect.collidepoint(pos):
                self.camera.target = sprite
                return

    def debug(self):  # Shows debug info
        font = pygame.font.Font(None, 30)
        lines = list()
        lines.append(font.render('FPS: ' + str(int(self.clock.get_fps())), True, pygame.Color('red')))
        lines.append(font.render('Rect: ' + str(self.player.rect), True, pygame.Color('red')))
        lines.append(font.render('HP: ' + str(self.player.hp), True, pygame.Color('red')))
        for num, line in enumerate(lines):
            self.screen.blit(line, (10, num * 30 + 10))

        for sprite in self.paths.keys():
            if not sprite.alive():
                del self.paths[sprite]
                break
            path, color = self.paths[sprite]
            coords = [self.camera.apply_pos((int(x[0]), int(x[1])), True) for x in path]
            pygame.draw.lines(self.screen, color, False, coords, 3)

    def process_events(self):  # Process all events
        for event in pygame.event.get():
            # Check for quit
            if self.conditions[INMENU]:
                self.menu.click(pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                self.conditions[RUNNING] = False
                break

            # Check for key pressed
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.append(event.key)

            # Check for key released
            if event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    del self.keys_pressed[self.keys_pressed.index(event.key)]

            # Check for mouse button pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if self.conditions[INMENU]:
                        self.menu.click(event.pos, event.type, event.button)
                    else:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            self.create_enemy(self.camera.apply_pos(event.pos), player=self.player)
                        elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                            self.change_camera_target(self.camera.apply_pos(event.pos))
                        else:
                            self.player.start_attacking()
                if not self.conditions[PAUSED]:
                    if event.button == pygame.BUTTON_RIGHT:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            self.delete_enemy(self.camera.apply_pos(event.pos))
                        else:
                            self.player.try_range_attack(self.camera.apply_pos(event.pos))
                    elif event.button == pygame.BUTTON_LEFT:
                        self.player.try_attack(self.camera.apply_pos(event.pos))
                        rect = pygame.rect.Rect(0, 0, 70, 90)
                        rect.center = self.player.rect.center
                        if abs(self.player.look_angle) >= 90:
                            rect.x -= 40
                        else:
                            rect.x += 40
                        sprite = pygame.sprite.Sprite()
                        sprite.rect = rect
                        collided = pygame.sprite.spritecollide(sprite, self.sprite_groups[ENTITIES], False)
                        for i in collided:
                            if i != self.player:
                                i.hurt(round(self.player.damage), self.player.get_pos())
                                i.push(i.x - self.player.x, i.y - self.player.y, 15)
                        collided = pygame.sprite.spritecollide(sprite, self.sprite_groups[PROJECTILES], False)
                        for i in collided:
                            if i.team != self.player.team:
                                i.die()
                        self.terrain.collide(sprite)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    if self.conditions[INMENU]:
                        self.menu.click(event.pos, event.type, event.button)
            if event.type == pygame.VIDEORESIZE:
                if not self.conditions[FULLSCREEN]:
                    self.resize_window(event.w, event.h)


if __name__ == '__main__':
    game = Game()
