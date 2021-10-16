import numpy as np
import pygame.draw as draw


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

        returns the amount of score recieved for the click (determinend by Ball.score variable)
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
