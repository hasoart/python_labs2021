import math
from random import randrange as rnd, choice

import pygame


FPS = 60

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
ORANGE = 0xFF7200
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

pygame.font.init()
score_font = pygame.font.SysFont('Comic Sans MS', 20)

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen

        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.is_moving = True

    def move(self, dt=1):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        if self.y <= 550:
            self.vy -= 1.2 * dt
            self.y -= self.vy * dt
            self.x += self.vx * dt
            self.vx *= 0.99
        else:
            if self.vx ** 2 + self.vy ** 2 > 10:
                self.vy = -self.vy / 2
                self.vx = self.vx / 2
                self.y = 549
            else:
                self.is_moving = False

        if self.x > 780:
            self.vx = -self.vx / 2
            self.x = 779

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        pygame.draw.circle(
            self.screen,
            BLACK,
            (self.x, self.y),
            self.r,
            1
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        # FIXED

        delta_x = obj.x - self.x
        delta_y = obj.y - self.y
        min_dist = (obj.r + self.r) ** 2

        dist = delta_x*delta_x + delta_y*delta_y
        if dist > min_dist:
            return False
        else:
            return True


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan2(event.pos[1]-450, event.pos[0]-20)
        if self.f2_on:
            self.color = ORANGE
        else:
            self.color = GREY

    def draw(self):
        gun_w = 7
        gun_l = self.f2_power
        x_gun = 20
        y_gun = 450
        sin_an = math.sin(self.an)
        cos_an = math.cos(self.an)
        coords = [(x_gun + gun_w * 0.5 * sin_an, y_gun - gun_w * 0.5 * cos_an),
                  (x_gun + gun_w * 0.5 * sin_an + gun_l * cos_an, y_gun - gun_w * 0.5 * cos_an + gun_l * sin_an),
                  (x_gun - gun_w * 0.5 * sin_an + gun_l * cos_an, y_gun + gun_w * 0.5 * cos_an + gun_l * sin_an),
                  (x_gun - gun_w * 0.5 * sin_an, y_gun + gun_w * 0.5 * cos_an)]

        pygame.draw.polygon(screen, self.color, coords)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = ORANGE
        else:
            self.color = GREY


class Target:
    def __init__(self):
        self.live = 1
        self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        self.x = rnd(600, 780)
        self.y = rnd(350, 550)
        self.r = rnd(2, 10)
        self.points = int(round(10 / self.r))
        self.color = RED
        self.live = 1

    def move(self, dt=1):
        pass

    def hit(self):
        """Попадание шарика в цель."""
        return self.points

    def draw(self):
        if self.live > 0:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.r, width=1)


class TargetHorizontal(Target):
    def __init__(self):
        super(TargetHorizontal, self).__init__()
        self.v = (-1) ** rnd(1, 3) * self.r ** 0.5

    def new_target(self):
        self.x = rnd(0, 800)
        self.y = rnd(50, 200)
        self.r = rnd(5, 20)
        self.points = int(round(10 / self.r))
        self.color = GREEN
        self.live = 1

    def move(self, dt=1):
        self.x += self.v * dt

        if not -100 < self.x < 880:
            self.x = -99 if self.x >= 880 else 879


class TargetVertical(Target):
    def __init__(self):
        super(TargetVertical, self).__init__()
        self.v = (-1) ** rnd(1, 3) * self.r ** 0.5

    def new_target(self):
        self.x = rnd(680, 780)
        self.y = rnd(0, 600)
        self.r = rnd(5, 20)
        self.points = int(math.ceil(10 / self.r))
        self.color = BLUE
        self.live = 1

    def move(self, dt=1):
        self.y += self.v * dt

        if not -100 < self.y < 700:
            self.y = -99 if self.x >= 700 else 699


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
targets = [TargetHorizontal() for _ in range(10)] +\
          [TargetVertical() for _ in range(10)]
score = 0

finished = False

while not finished:
    screen.fill(WHITE)
    gun.draw()

    text = score_font.render(f'Score {score}', True, BLACK)
    screen.blit(text, (20, 20))

    for target in targets:
        target.move()
        target.draw()

    for b in balls:
        b.draw()

    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    c = 0
    for b in balls:
        b.move()
        for target in targets:
            if b.hittest(target) and target.live:
                target.live = 0
                score += target.hit()
                balls.pop(c)
                break
        else:
            if not b.is_moving:
                balls.pop(c)
            else:
                c += 1

    gun.power_up()


pygame.quit()
