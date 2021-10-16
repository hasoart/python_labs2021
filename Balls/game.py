import pygame

from ball import Ball
import styles


def exit_program():
    pygame.quit()
    exit(0)


class Game:

    def __init__(self, size, dt=0.1, score_penalty=1, ball_count=10, ball_colors=styles.COLORS,
                 bg_color=styles.BLACK, ball_radius=10, ball_score=None):

        self.surface = pygame.Surface(size)
        self.size = size

        self.pool = [Ball(size, ball_colors, ball_radius, ball_score)
                     for _ in range(ball_count)]
        self.balls_left = ball_count
        self.bg_color = bg_color

        self.score = 0
        self.score_penalty = score_penalty

        self.dt = dt

        self.is_finished = False

    def evolve(self):
        self.surface.fill(self.bg_color)
        for ball in reversed(self.pool):  # here we iterate through reversed pool so
            ball.move(self.dt)  # that the first object renders on top
            ball.collision()
            ball.render(self.surface)

    def clicked(self, coords):
        for i, ball in enumerate(self.pool):
            score_inc = ball.click(coords)
            if score_inc >= 0:
                self.pool.pop(i)
                self.score += score_inc
                self.balls_left -= 1

                if self.balls_left > 0:
                    return 1
                else:
                    self.is_finished = True
                    return -1
        else:
            self.score -= self.score_penalty
            return 0

    # returns 1 for hit, 0 for miss and -1 if no balls left

    def set_dt(self, dt):
        self.dt = dt

    def get_is_finished(self):
        return self.is_finished

    def get_surface(self):
        return self.surface

    def get_score(self):
        return self.score

    def get_size(self):
        return self.size


class GameEventHandler:

    def __init__(self, game, game_coords=(0, 0)):
        self.game = game
        self.game_coords = game_coords

        self.is_finished = False

    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_program()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.is_finished:
                x, y = event.pos
                x_game, y_game = self.game_coords
                x_rel, y_rel = x - x_game, y - y_game

                width_game, height_game = self.game.get_size()

                if (0 <= x_rel <= width_game and
                        0 <= y_rel <= height_game):
                    finish_code = self.game.clicked((x_rel, y_rel))

                    if finish_code == -1:
                        self.is_finished = True

                    return finish_code


class ScoreSurface:
    def __init__(self, size, font=styles.score_font, bg_color=styles.BLACK,
                 colors=styles.HIT_MISS_NEUTRAL):

        self.size = size
        self.surface = pygame.Surface(size)
        self.font = font
        self.bg_color = bg_color
        self.hit, self.miss, self.neutral = colors

    def get_surface(self, score, hit):
        if hit == 1 or hit == -1:
            color = self.hit
        elif hit == 0:
            color = self.miss
        else:
            color = self.neutral
        text = self.font.render(f'Score {score}', True, color)
        self.surface.fill(self.bg_color)
        self.surface.blit(text, (0, 0))

        return self.surface


class FinalScreenHandler:
    def __init__(self, final_screen, leaderboard):
        self.text = ""
        self.final_screen = final_screen
        self.leaderboard = leaderboard

    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_program()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.leaderboard.write(self.text, self.final_screen.get_score())
                    exit_program()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                self.final_screen.set_name(self.text)


class FinalScreen:
    def __init__(self, size, score=0, font=styles.final_screen_font,
                 font_color=styles.WHITE, bg_color=styles.BLACK):
        self.size = size
        self.surface = pygame.Surface(size)
        self.font = font
        self.font_color = font_color
        self.bg_color = bg_color

        self.score = score
        self.name = ""

    def get_surface(self):
        row = []
        row += [self.font.render(f'Final score is {self.score}', True, self.font_color)]
        row += [self.font.render(f'Enter your name', True, self.font_color)]
        row += [self.font.render(self.name, True, self.font_color)]

        self.surface.fill(self.bg_color)

        y_offset = 0
        for i in range(3):
            width, height = row[i].get_size()
            x_offset = (self.size[0] - width) / 2
            self.surface.blit(row[i], (x_offset, y_offset))

            y_offset += height

        return self.surface

    def set_name(self, name):
        self.name = name

    def set_score(self, score):
        self.score = score

    def get_name(self):
        return self.name

    def get_score(self):
        return self.score


class Leaderboard:
    def __init__(self, leaderboard_path='leaderboard.txt'):
        self.path = leaderboard_path

    def write(self, name, score):
        with open(self.path, 'a') as file:
            file.write(f"{name:<20}: {score}\n")
