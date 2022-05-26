import os
from math import sin, cos, radians
from pathlib import Path

import pygame as pg

from GameSettings import *


class GameObject(pg.sprite.Sprite):
    def __init__(self, *groups: pg.sprite.AbstractGroup,
                 x: float = DEFAULT_X, y: float = DEFAULT_Y,
                 direction: float = DEFAULT_DIRECTION,
                 image_path: Path,
                 width: float = DEFAULT_WIDTH, height: float = DEFAULT_HEIGHT):
        super().__init__(*groups)
        self._x = x
        self._y = y
        self._direction = direction
        self._original_image = pg.transform.rotate(pg.transform.scale(pg.image.load(image_path), (width, height)),
                                                   direction)
        self._image = self._original_image.copy()
        self._rect = self._image.get_rect(center=(self._x, self._y))
        self._width = width
        self._height = height

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def direction_radians(self):
        return radians(self._direction)

    @property
    def direction_degrees(self):
        return self._direction

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        return self._rect

    def update(self) -> None:
        super().update()

    def move(self, dx: float, dy: float) -> None:
        self._x += dx
        self._y += dy
        if not self.in_horizontal_bounds():
            self._x = WIDTH - self._x
        if not self.in_vertical_bounds():
            self._y = HEIGHT - self._y
        self._rect.center = self._x, self._y

    def rotate(self, angle: float = 0) -> None:
        self._image = pg.transform.rotate(self._original_image, self._direction + angle)
        self._rect = self._image.get_rect(center=self._original_image.get_rect(center=(self._x, self._y)).center)
        self._direction += angle
        self._direction %= 360

    def in_horizontal_bounds(self):
        return -BOUND < self._x < WIDTH + BOUND

    def in_vertical_bounds(self):
        return -BOUND < self._y < HEIGHT + BOUND

    def in_bounds(self):
        return self.in_horizontal_bounds() and self.in_vertical_bounds()


class Player(GameObject):
    _spaceship_image_path = Path('./img/spaceship.png')
    _spaceship_accelerating_image_path = Path('./img/spaceship_accelerating.png')
    _laser_image_path = Path('./img/laser.png')

    def __init__(self, *args, **kwargs):
        self._lasers = pg.sprite.Group()
        self._lives = DEFAULT_LIVES_NUMBER
        self._score = 0
        self._space_pressed = False
        self._k_up_pressed = False
        self._x_velocity = 0
        self._y_velocity = 0
        super().__init__(*args, image_path=self._spaceship_image_path, **kwargs)
        self._spaceship_image = pg.transform.scale(pg.image.load(self._spaceship_image_path),
                                                   (self._width, self._height))
        self._spaceship_accelerating_image = pg.transform.scale(pg.image.load(self._spaceship_accelerating_image_path),
                                                                (self._width, self._height))

    @property
    def lasers(self):
        return self._lasers

    @property
    def lives(self):
        return self._lives

    @property
    def score(self):
        return self._score

    @property
    def velocity_squared(self):
        return self._x_velocity ** 2 + self._y_velocity ** 2

    def increase_score(self) -> None:
        self._score += 1

    def respawn(self) -> None:
        self._x = CENTER_X
        self._y = CENTER_Y
        self._direction = 0
        self._x_velocity = 0
        self._y_velocity = 0
        self._lives -= 1
        self.rotate(angle=-self._direction)

    def move(self, dx: float, dy: float) -> None:
        super().move(dx, dy)

    def movement(self) -> None:
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self._k_up_pressed = True
            if self.velocity_squared < MAX_SPACESHIP_SPEED_SQUARED:
                self._x_velocity += SPACESHIP_ACCELERATION * sin(self.direction_radians)
                self._y_velocity += SPACESHIP_ACCELERATION * cos(self.direction_radians)
            self.set_image(self._spaceship_accelerating_image)
        else:
            if self._x_velocity != 0:
                self._x_velocity -= self._x_velocity / abs(self._x_velocity) * abs(self._x_velocity) * 0.1
            if self._y_velocity != 0:
                self._y_velocity -= self._y_velocity / abs(self._y_velocity) * abs(self._y_velocity) * 0.1
        if keys[pg.K_LEFT]:
            self.rotate(angle=SPACESHIP_ROTATION_SPEED)
        if keys[pg.K_RIGHT]:
            self.rotate(angle=-SPACESHIP_ROTATION_SPEED)
        if keys[pg.K_SPACE]:
            self._space_pressed = True
        elif self._space_pressed:
            self._space_pressed = False
            self._lasers.add(Laser(x=self._x, y=self._y,
                                   direction=self._direction,
                                   image_path=self._laser_image_path,
                                   width=DEFAULT_LASER_WIDTH, height=DEFAULT_LASER_HEIGHT))

    def update(self) -> None:
        self.movement()
        self.move(dx=-self._x_velocity,
                  dy=-self._y_velocity)

    def set_image(self, image: pg.Surface):
        self._image = pg.transform.rotate(image, self._direction)


class Asteroid(GameObject):
    from random import choice, randrange, randint

    _asteroid_image_paths = [Path('./img/asteroid_1.png'),
                             Path('./img/asteroid_2.png'),
                             Path('./img/asteroid_3.png')]

    _position_boundaries = [{'x': (-BOUND, WIDTH + BOUND), 'y': (-BOUND, -BOUND + 1)},
                            {'x': (-BOUND, WIDTH + BOUND), 'y': (HEIGHT + BOUND, HEIGHT + BOUND + 1)},
                            {'x': (-BOUND, -BOUND + 1), 'y': (-BOUND, HEIGHT + BOUND)},
                            {'x': (WIDTH + BOUND, WIDTH + BOUND + 1), 'y': (-BOUND, HEIGHT + BOUND)}]

    def __init__(self, *args, **kwargs):
        self._image_path = None
        self._dx, self._dy = None, None
        self.set_random_parameters()
        super().__init__(*args, x=self._x, y=self._y, direction=0, image_path=self.choice(self._asteroid_image_paths),
                         **kwargs)
        self._rotation_speed = self.randrange(-MAX_ASTEROID_ROTATION_SPEED, MAX_ASTEROID_ROTATION_SPEED)

    def set_random_parameters(self) -> None:
        boundaries = self.choice(self._position_boundaries)
        self._x = self.randrange(*boundaries['x'])
        if not self._x:
            self._x = 0.1
        self._y = self.randrange(*boundaries['y'])
        if not self._y:
            self._y = 0.1
        self._dx = (self.randrange(CENTER_X - CENTER_AREA_RADIUS,
                                   CENTER_X + CENTER_AREA_RADIUS) - self._x) / 2000 * self.randint(1, 3)
        self._dy = (self.randrange(CENTER_Y - CENTER_AREA_RADIUS,
                                   CENTER_Y + CENTER_AREA_RADIUS) - self._y) / 2000 * self.randint(1, 3)
        self._image_path = self.choice(self._asteroid_image_paths)

    def update(self) -> None:
        if not self.in_bounds():
            self.set_random_parameters()
        self.move(dx=self._dx, dy=self._dy)
        self.rotate(angle=self._rotation_speed)
        super().update()


class Laser(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self) -> None:
        if not self.in_bounds():
            self.kill()
        self.move(dx=-LASER_SPEED * sin(self.direction_radians),
                  dy=-LASER_SPEED * cos(self.direction_radians))
        super().update()


class Explosion(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._images = self.get_images()
        self._start_tick = pg.time.get_ticks()
        self._frame_length = EXPLOSION_LENGTH_IN_MILLIS // len(self._images)

    def get_images(self) -> list[pg.Surface]:
        images = []
        for root, _, files in os.walk(EXPLOSION_ANIMATION_IMAGES_PATH):
            for file in files:
                images.append(pg.transform.rotate(pg.transform.scale(pg.image.load(Path('.', root, file)),
                                                                     (self._width, self._height)), self._direction))
        return images

    @property
    def index(self) -> int:
        return (pg.time.get_ticks() - self._start_tick) // self._frame_length

    def update(self) -> None:
        index = self.index
        if index >= len(self._images):
            self.kill()
        else:
            self._image = self._images[index]
            super().update()
