import numpy as np
import pygame
import pygame.draw as draw

from ghost_body import get_ghost

ghost = get_ghost()
ghost_size = np.array(ghost.get_size())


class Ball:

    def __init__(self, borders, color=(255, 0, 0), r=10, score=None):
        """
        Ball(borders, color=(255, 0, 0), r=10)
        returns - None

        Initializes Ball object

        borders(np.array of shape (2,) and type float or int) - the borders of the screen.
                                                                Used to init coords within screen
        color(tuple of type (R,G,B)(int) or list of tuples (R, G, B)(int))=(255, 0, 0) -
            color of the ball. If tuple (R, G, B) is passed than it is the color of the ball.
            If list of tuples is passed, color is drawn randomly from that list.
        r(int or float or tuple/list/np.array (a, b))=10 -
            if int or float is passed r is radius of the ball
            if tuple/list/np.array (a, b) is passed radius is drawn randomly
            from interval a to b
        score(int or float)=None - the bounty for ball. If None is passed score is calculated
                                   from r by formula score=round(30/r)
        """
        self.coords = np.random.randint(0, borders, size=2).astype(float)
        self.velocity = np.random.randint(-30, 30, size=2).astype(float)
        self.borders = borders

        if type(color[0]) == int:
            self.color = color
        else:
            self.color = color[np.random.randint(0, len(color))]

        if type(r) in (tuple, list, np.array):
            a, b = r
            self.r = np.random.random() * (b - a) + a
        else:
            self.r = r

        if score is None:
            self.score = max(1, int(np.round(30 / self.r)))
        else:
            self.score = score

        self.is_alive = True

    def move(self, dt=1):
        """
        Ball.move(dt=1)
        returns - None

        Updates balls coordinates by time dt

        dt(int or float) - value of variable of evolution
        """
        self.coords += self.velocity * dt

    def collision(self):
        """
        Ball.collision(borders)
        returns - None

        Calculates the collision of the ball with borders

        borders(np.array of shape (2,) and type float or int) - the borders of the screen.
        """
        for i in (0, 1):
            if np.abs(self.coords[i] - self.borders[i] / 2) >= self.borders[i] / 2 - self.r:
                self.coords[i] = self.r if self.coords[i] <= self.r else self.borders[i] - self.r
                self.velocity[i] *= -1

    def click(self, mouse_coords):
        """
        Ball.click(mouse_coords)
        returns - int

        Checks if ball is clicked

        mouse_coords(np.array of shape (2,) and type float or int) - x, y coordinates of mouse

        returns the amount of score received for the click (determined by Ball.score variable)
        """
        if self.is_alive and np.linalg.norm(self.coords - mouse_coords) <= self.r:
            self.is_alive = False
            return self.score

        return -1

    def render(self, surface):
        """
        Ball.render(surface)
        returns - None

        Renders ball on the surface.

        surface(pygame.Surface) - surface to be rendered on
        """
        if self.is_alive:
            draw.circle(surface, self.color, self.coords, self.r)


class Ghost:

    def __init__(self, borders, size, score=None):
        self.coords = np.random.randint(0, borders - size, size=2).astype(float)
        self.velocity = np.random.randint(-30, 30, size=2).astype(float)
        self.borders = borders
        self.size = size
        self.ghost = pygame.transform.smoothscale(ghost, (size, size))

        if score is None:
            self.score = max(1, int(np.round(100 / self.size)))
        else:
            self.score = score

        self.is_alive = True

    def move(self, dt=1):
        self.coords += self.velocity * dt
        self.velocity += np.random.random(2) * 5 * dt

    def collision(self):
        if not (0 <= self.coords[1] <= self.borders[1] - self.size):
            self.coords[1] = 0 if 0 > self.coords[1] else self.borders[1] - self.size
            self.velocity[1] *= -1.5 if np.abs(self.velocity[1]) <= 50 else -1

        if self.coords[0] < 0:
            self.coords[0] = self.borders[0] + self.coords[0]
        elif self.coords[0] > self.borders[0]:
            self.coords[0] = self.coords[0] - self.borders[0]

    def click(self, mouse_coords):
        x0, y0 = self.coords
        if self.is_alive:
            if 0 <= self.coords[0] <= self.borders[0] - self.size:
                if pygame.Rect(x0, y0, self.size, self.size).collidepoint(mouse_coords):
                    self.is_alive = False
                    return self.score
            else:
                if (pygame.Rect(x0, y0, self.borders[0] - x0, self.size).collidepoint(mouse_coords) or
                    pygame.Rect(0, y0, self.size - self.borders[0] + x0, self.size).collidepoint(mouse_coords)):
                    self.is_alive = False
                    return self.score

        return -1

    def render(self, surface):
        if self.is_alive:
            if 0 <= self.coords[0] <= self.borders[0] - self.size:
                surface.blit(self.ghost, self.coords)
            else:
                surface.blit(self.ghost, self.coords)
                surface.blit(self.ghost, self.coords - np.array([self.borders[0], 0]))
