from GameObjects import *
from Interface import *


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption(TITLE)
        self._screen = pg.display.set_mode(RESOLUTION)
        self._clock = pg.time.Clock()
        self._font = pg.font.SysFont('Roboto', 50)
        self._background = pg.transform.scale(pg.image.load(BACKGROUND_IMAGE_PATH), RESOLUTION)
        self._background_asteroids = pg.transform.scale(pg.image.load(BACKGROUND_ASTEROIDS_IMAGE_PATH), RESOLUTION)
        self._all_game_objects = pg.sprite.Group()
        self._asteroids = pg.sprite.Group()
        self._player = Player()
        self._asteroids.add([Asteroid() for _ in range(10)])
        self._all_game_objects.add(self._asteroids, self._player)
        self._start_button = Button(x=CENTER_X - START_BUTTON_WIDTH / 2,
                                    y=CENTER_Y - START_BUTTON_HEIGHT / 2,
                                    width=START_BUTTON_WIDTH,
                                    height=START_BUTTON_HEIGHT,
                                    image_path=Path('./img/start_button.png'),
                                    on_click=self.game_loop,
                                    on_click_args=())

    def start(self) -> None:
        self.main_menu()

    def main_menu(self) -> None:
        while True:
            self.quit_check()
            self.background()
            self._start_button.draw(screen=self._screen)
            if self._start_button.is_clicked():
                self._start_button.on_click()
            pg.display.update()
            self._clock.tick(FPS)

    def game_loop(self) -> None:
        while True:
            self.quit_check()
            self.background()
            self.objects()
            score = self._font.render(f'Score: {self._player.score}', True, (255, 255, 255))
            lives = self._font.render(f'Lives: {self._player.lives}', True, (255, 255, 255))
            self._screen.blit(score, score.get_rect(center=(CENTER_X, 25)))
            self._screen.blit(lives, lives.get_rect(center=(70, 25)))
            pg.display.update()
            self._clock.tick(FPS)

    def background(self):
        offset = pg.time.get_ticks() // 100 % WIDTH
        self._screen.blit(self._background, (0, 0))
        self._screen.blit(self._background_asteroids, (offset, 0))
        self._screen.blit(self._background_asteroids, (offset - WIDTH, 0))

    def collision(self) -> None:
        for sprite in pg.sprite.spritecollide(self._player, self._asteroids, True, pg.sprite.collide_mask):
            if isinstance(sprite, Asteroid):
                self._all_game_objects.add(Explosion(x=sprite.x, y=sprite.y, direction=sprite.direction_degrees,
                                                     image_path=Path('./img/asteroid_1.png')))
            sprite.kill()
            self.spawn_asteroid()
            self._player.respawn()

        for sprite in pg.sprite.groupcollide(self._asteroids, self._player.lasers, True, pg.sprite.collide_mask):
            if isinstance(sprite, Asteroid):
                self._all_game_objects.add(Explosion(x=sprite.x, y=sprite.y, direction=sprite.direction_degrees,
                                                     image_path=Path('./img/asteroid_1.png')))
            sprite.kill()
            self.spawn_asteroid()
            self._player.increase_score()

    def objects(self) -> None:
        self.collision()
        self._all_game_objects.add(self._player.lasers)
        self._all_game_objects.update()
        self._all_game_objects.draw(self._screen)

    def spawn_asteroid(self) -> None:
        asteroid = Asteroid()
        self._asteroids.add(asteroid)
        self._all_game_objects.add(asteroid)

    def quit_check(self) -> None:
        if self._player.lives == 0:
            self.quit(message=f'Game over\nScore: {self._player.score}')
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    @staticmethod
    def quit(message: int | str = 0) -> None:
        pg.quit()
        exit(message)
