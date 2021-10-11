import numpy as np
import pygame
import pygame.draw as draw

import ball
import styles

LEADERBOARD = 'leaderboard.txt'
def update_leaderboard(score):
    print(f'Finished. Final score {score}.')
    name = input('Enter your name to save in leaderboard: ')
    with open(LEADERBOARD, 'a') as file:
        file.write(f"{name:<20}: {score}\n")

pygame.init()

FPS = 30
BORDERS = np.array([600, 600])

screen = pygame.display.set_mode(BORDERS)


pygame.display.update()
clock = pygame.time.Clock()
finished = False

POOL_SIZE = 5
pool = [ball.Ball(BORDERS, styles.COLORS, r=(5, 31))
        for _ in range(POOL_SIZE)]


score = 0
penalty = 3
balls_left = POOL_SIZE

dt = 3 / FPS

while not finished:
    clock.tick(FPS)
    for el in pool:
        el.render(screen)
        el.move(dt)
        el.collision(BORDERS)



    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos 
            for i, el in enumerate(pool):
                d_score = el.click(np.array([x, y]))
                if d_score > 0:
                    score += d_score
                    el.render(screen)
                    pygame.display.update()

                    balls_left -= 1
                    print(f'Hit!  score - {score}')
                    pool.pop(i)
                    break
            else:
                score -= penalty
                print(f'Miss! score - {score}')


    if event.type == pygame.QUIT:
        finished = True
    pygame.display.update()
    screen.fill(styles.BLACK)

    if balls_left == 0:
        pygame.quit()
        finished = True
        update_leaderboard(score)
pygame.quit()