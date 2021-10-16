import numpy as np
import time

from game import *

pygame.init()

FPS = 30
dt = 3 / FPS
score_timeout = 0.5

screen_size = np.array([602, 678])
game_size = np.array([600, 600])
score_size = np.array([600, 75])
final_screen_size = np.array([600, 676])
game_coords = np.array([1, 1])
score_coords = np.array([1, 602])
final_screen_coords = np.array([1, 1])

screen = pygame.display.set_mode(screen_size)
screen.fill(styles.WHITE)
pygame.display.update()
clock = pygame.time.Clock()

penalty = 3
ball_count = 30

game = Game(game_size, dt, penalty, ball_count, ball_radius=(10, 30))
score = ScoreSurface(score_size)
handler = GameEventHandler(game, game_coords)
leaderboard = Leaderboard('leaderboard.txt')

game_finished = False

score_surf = score.get_surface(0, -1)

last_score_time = time.time()
while not game_finished:
    game.evolve()

    game_surf = game.get_surface()
    screen.blit(game_surf, game_coords)

    hit = handler.handle()

    if hit is not None:
        score_surf = score.get_surface(game.get_score(), hit)
        last_score_time = time.time()
    elif time.time() - last_score_time >= score_timeout:
        score_surf = score.get_surface(game.get_score(), None)

    screen.blit(score_surf, score_coords)

    game_finished = game.get_is_finished()
    pygame.display.update()

    clock.tick(FPS)

final_screen = FinalScreen(size=final_screen_size, score=game.get_score())
handler = FinalScreenHandler(final_screen, leaderboard)

while True:
    handler.handle()
    final_screen_surf = final_screen.get_surface()
    screen.blit(final_screen_surf, final_screen_coords)
    pygame.display.update()
