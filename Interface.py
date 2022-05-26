from pathlib import Path
from typing import Callable, Iterable

import pygame as pg


class Button:
    def __init__(self, x: float, y: float, width: float, height: float, image_path: Path,
                 on_click: Callable, on_click_args: Iterable):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._image = pg.transform.scale(pg.image.load(image_path), (width, height))
        self._on_click = on_click
        self._on_click_args = on_click_args

    def is_clicked(self) -> bool:
        for _ in pg.event.get(eventtype=pg.MOUSEBUTTONDOWN):
            mouse_position = pg.mouse.get_pos()
            return self._x <= mouse_position[0] <= self._x + self._width \
                   and self._y <= mouse_position[1] <= self._y + self._height

    def on_click(self) -> None:
        self._on_click(*self._on_click_args)

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self._image, (self._x, self._y))
