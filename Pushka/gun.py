import math
from random import randrange as rnd, choice
from time import time
import json

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

small_font = pygame.font.SysFont('Comic Sans MS', 20)
big_font = pygame.font.SysFont('Comic Sans MS', 60)

WIDTH = 800
HEIGHT = 600


def exit_program():
    """
    exit_program()
    returns - None

    exits the program
    """
    pygame.quit()
    exit(0)


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

        if not -self.r < self.x < 800 + self.r:
            self.x = (1 - self.r) if (self.x >= 800 + self.r) else (799 + self.r)


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

        if not -self.r < self.y < 600 + self.r:
            self.y = (1 - self.r) if (self.y >= 600 + self.r) else (599 + self.r)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
targets = [TargetHorizontal() for _ in range(3)] +\
          [TargetVertical() for _ in range(3)]
score = 0

finished = False
start_time = time()

while targets:
    screen.fill(WHITE)

    gun.draw()

    for target in targets:
        target.move()
        target.draw()

    for b in balls:
        b.draw()

    score_text = small_font.render(f'Score {score}', True, BLACK)
    screen.blit(score_text, (20, 20))
    bullet_text = small_font.render(f'Bullets {bullet}', True, BLACK)
    screen.blit(bullet_text, (20, 40))
    time_text = small_font.render(f'Time {time() - start_time:.1f}', True, BLACK)
    screen.blit(time_text, (20, 60))

    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    c = 0
    for b in balls:
        b.move()
        for i, target in enumerate(targets):
            if b.hittest(target) and target.live:
                target.live = 0
                score += target.hit()
                targets.pop(i)
                balls.pop(c)
                break
        else:
            if not b.is_moving:
                balls.pop(c)
            else:
                c += 1

    gun.power_up()

final_time = round(time() - start_time, 1)
final_score = int(10000 * score / (final_time * bullet))

player_name = ""
name_entered = False

while not name_entered:
    screen.fill(WHITE)

    row = []
    row += [big_font.render(f'Final score is {final_score}', True, BLACK)]
    row += [big_font.render(f'Enter your name', True, BLACK)]
    row += [big_font.render(player_name, True, BLACK)]

    y_offset = 150
    for i in range(3):
        width, height = row[i].get_size()
        x_offset = (WIDTH - width) / 2
        screen.blit(row[i], (x_offset, y_offset))

        y_offset += height

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                name_entered = True
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                player_name += event.unicode

    pygame.display.update()
    clock.tick(FPS)

try:
    with open('leaderboard.json', 'r') as f:
        leaderboard = json.load(f)
    leaderboard['scores'].append({'name': player_name, 'score': final_score})
    leaderboard['scores'] = sorted(leaderboard['scores'], key=lambda x: x.get('score'), reverse=True)
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)
except:
    leaderboard = {'scores': [{'name': player_name, 'score': final_score}]}
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)

leaderboard_surface = pygame.Surface((800, 600))
leaderboard_surface.fill(WHITE)
title_text = big_font.render('Leaderboard', True, BLACK)

width, height = title_text.get_size()

x_offset = (WIDTH - width) / 2
y_offset = 50

leaderboard_surface.blit(title_text, (x_offset, y_offset))
y_offset += 100
rows = [None for _ in range(10)]
leaderboard_length = 10 if len(leaderboard['scores']) > 10 else len(leaderboard['scores'])
for i in range(leaderboard_length):
    name, score = leaderboard['scores'][i]['name'], leaderboard['scores'][i]['score']
    row = pygame.Surface((300, 30))
    row.fill(WHITE)
    name_surface = small_font.render(f'{name}', True, BLACK)
    score_surface = small_font.render(f'{score}', True, BLACK)
    row.blit(name_surface, (0, 0))
    row.blit(score_surface, (200, 0))

    rows[i] = row

for row in rows:
    if row is not None:
        width, height = row.get_size()
        x_offset = (WIDTH - width) / 2
        leaderboard_surface.blit(row, (x_offset, y_offset))
        y_offset += height
    else:
        break

while True:
    screen.blit(leaderboard_surface, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()

    pygame.display.update()
    clock.tick(FPS)

