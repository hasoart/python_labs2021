import pygame

from targets import Ball, Ghost
import styles


def exit_program():
    """
    exit_program()
    returns - None

    exits the program
    """
    pygame.quit()
    exit(0)


class Game:
    def __init__(self, size, dt=0.1, score_penalty=1, pool_size=(10, 2), bg_color=styles.BLACK,
                 ball_colors=styles.COLORS, ball_radius=10, ball_score=None, ball_max_velocity=50,
                 ghost_size=50, ghost_score=None, ghost_max_velocity=100):
        """
        Initializes Game object. Game object is used to simplify handling of multiple targets on one surface. Note that
        clicks should be handled using GameHandler object.

        returns - None

        arguments:
        size(np.array of shape (2,) of type int) - the size of the game surface.
        dt(int or float)=0.1 - the time evolution variable. Can be used to control the overall speed of the game.
        score_penalty(int or float)=1 - the amount of score to be punished for miss clicks.
        pool_size(tuple (Balls, Ghosts) of non-negative ints) - the amount of Balls and Ghosts in the pool.
        bg_color(color tuple (R,G,B))=styles.BLACK - the background of play field.

        ball_colors(tuple of type (R,G,B)(int) or list of tuples (R, G, B)(int))=styles.COLORS - see
                  Ball.__init__ argument 'color' for more info.

        ball_radius(int or float or tuple/list/np.array (a, b)) - see Ball.__init__ argument 'r' for more info.
        ball_score(int or float or None)=None - see Ball.__init__ argument 'score' for more info.
        ball_max_velocity(int or float)=50 - see Ball.__init__ argument 'max_velocity' for more info.

        ghost_size(int or float)=50 - see Ghost.__init__ argument 'size' for more info.
        ghost_score(int or float or None)=None - see Ghost.__init__ argument 'score' for more info.
        ghost_max_velocity(int or float)=100 - see Ghost.__init__ argument 'max_velocity' for more info.
        """
        self.surface = pygame.Surface(size)
        self.size = size

        self.pool = [Ball(size, ball_colors, ball_radius, ball_max_velocity, ball_score)
                     for _ in range(pool_size[0])] + \
                    [Ghost(size, ghost_size, ghost_max_velocity, ghost_score) for _ in range(pool_size[1])]
        self.balls_left = pool_size[0] + pool_size[1]
        self.bg_color = bg_color

        self.score = 0
        self.score_penalty = score_penalty

        self.dt = dt

        self.is_finished = False

    def evolve(self):
        """
        Game.evolve() - handles the evolution of the game
        returns - None
        """
        self.surface.fill(self.bg_color)
        for ball in reversed(self.pool):  # here we iterate through reversed pool so
            ball.move(self.dt)  # that the first object renders on top
            ball.collision()
            ball.render(self.surface)

    def clicked(self, coords):
        """
        Game.clicked(coords) - transmits the click to targets of the pool
        returns - 1 if hit, 0 if miss, -1 if hit and the game finished

        coords(list, tuple or np.array of mouse coordinates of type int or float) - x and y coordinates of click
        """
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

    def set_dt(self, dt):
        """
        sets Game.dt variable to dt(int or float)
        returns - None
        """
        self.dt = dt

    def get_is_finished(self):
        """
        returns Game.is_finished(bool) variable, which is used to check if Game has finished or not
        """
        return self.is_finished

    def get_surface(self):
        """
        returns Game.surface(pygame.Surface) on which the game is rendered on
        """
        return self.surface

    def get_score(self):
        """
        returns the score(int or float) of the game
        """
        return self.score

    def get_size(self):
        """
        returns the size of the game surface(tuple of ints (width, height))
        """
        return self.size


class GameEventHandler:
    def __init__(self, game, game_coords=(0, 0), logger=None):
        """
        Initializes GameEventHandler object. This object is used to handle click events and program closing events.
        returns - None

        arguments:
        game(Game) - the game for which the clicks are handled
        game_coords(list, tuple or np.array of ints)=(0, 0) - coordinates of the upper-left corner of the game.
               Used to calculate relative click coordinates for game.

        logger(Logger)=None - if None is passed no logging is done. Otherwise logging is done by the logger.
        """
        self.game = game
        self.game_coords = game_coords

        self.is_finished = False

        if logger is None:
            self.logging = False
        else:
            self.logging = True
            self.logger = logger

            self.obj_id = hash(game.get_surface())
            self.obj_name = "GameEventHandler"
            self.obj_properties = {'position': [*map(int, [*game_coords])]}

            self.logger.init(self)

    def handle(self):
        """
        Handles envents pygame.QUIT and pygame.MOUSEBUTTONDOWN.
        returns - True if game finished, 0 if miss, 1 if hit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.logging:
                    self.logger.log(self, 'Quit application')
                    self.logger.dump()
                exit_program()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.is_finished:
                x, y = event.pos

                x_game, y_game = self.game_coords
                x_rel, y_rel = x - x_game, y - y_game

                if self.logging:
                    self.logger.log(self, f'Click registered at x:{x}, y:{y}')

                width_game, height_game = self.game.get_size()

                if (0 <= x_rel <= width_game and
                        0 <= y_rel <= height_game):
                    finish_code = self.game.clicked((x_rel, y_rel))

                    if finish_code == -1:
                        self.is_finished = True

                    return finish_code

    def get_obj_id(self):
        """
        returns id generated from the hash of game surface. Used for logging.
        """
        return self.obj_id

    def get_obj_name(self):
        """
        returns name of the object. Used for logging.
        """
        return self.obj_name

    def get_obj_properties(self):
        """
        returns object properties. Used for logging.
        """
        return self.obj_properties


class ScoreSurface:
    def __init__(self, size, font=styles.score_font, bg_color=styles.BLACK,
                 colors=styles.HIT_MISS_NEUTRAL):
        """
        ScoreSurface object is used to get surfaces with text showing the score on it.

        arguments:

        size(np.array of shape (2,) of type int) - the size of the surface.
        font(pygame Font object)=styles.score_font - font used to render text
        bg_color(color tuple (R,G,B))=styles.BLACK - background color of the surface
        colors(list of 3 color tuples (R,G,B))=styles.HIT_MISS_NEUTRAL - colors used for rendering the text depending
            whether click was hit, miss or no click has been done in a while(neutral). In the list first color stands
            for hit, second for miss and third for neutral
        """
        self.size = size
        self.surface = pygame.Surface(size)
        self.font = font
        self.bg_color = bg_color
        self.hit, self.miss, self.neutral = colors

    def get_surface(self, score, hit):
        """
        returns the surface(pygame.Surface) with text on it

        arguments:
        score(int or float) - score to be displayed
        hit(int or None) - which color to use.
                           1 or -1 for hit
                           0 for miss
                           None for neutral

        """
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
    def __init__(self, final_screen, leaderboard, logger=None):
        """
        FinalScreenHandler is used to handle events on final screen.

        argumentsL
        final_screen(FinalScreen) - FinalScreen which is going to be handled
        leaderboard(Leaderboard) - Leaderboard where scores are going to be saved to
        logger(Logger or None)=None - if None is passed no logging is done, otherwise logger is used to do it.
        """
        self.text = ""
        self.final_screen = final_screen
        self.leaderboard = leaderboard

        if logger is None:
            self.logging = False
        else:
            self.logging = True
            self.logger = logger

            self.obj_id = hash(final_screen.get_surface())
            self.obj_name = "FinalScreenHandler"
            self.obj_properties = {'leaderboard': self.leaderboard.get_name()}

            self.logger.init(self)

    def handle(self):
        """
        Handles the events.
        returns - None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.logging:
                    self.logger.log(self, 'Quit application')
                    self.logger.dump()
                exit_program()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.logging:
                        self.logger.log(self, 'Sending write request to leaderboard')

                    self.leaderboard.write(self.text, self.final_screen.get_score())

                    if self.logging:
                        self.logger.log(self, 'Quit application')
                        self.logger.dump()
                    exit_program()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                self.final_screen.set_name(self.text)

    def get_obj_id(self):
        """
        returns id generated from the hash of final_screen surface. Used for logging.
        """
        return self.obj_id

    def get_obj_name(self):
        """
        returns name of the object. Used for logging.
        """
        return self.obj_name

    def get_obj_properties(self):
        """
        returns object properties. Used for logging.
        """
        return self.obj_properties


class FinalScreen:
    def __init__(self, size, score=0, font=styles.final_screen_font,
                 font_color=styles.WHITE, bg_color=styles.BLACK):
        """
        FinalScreen object is used to create and render final screen where the score is shown and the user is prompted
        to write their name to save in leaderboard.

        arguments:
        size(np.array of shape (2,) of type int) - the size of the surface.
        score(int or float)=0 - the score to be shown.
        font(pygame Font object)=styles.score_font - font used to render text.
        font_color(color tuple (R,G,B)) - color of the text.
        bg_color(color tuple (R,G,B))=styles.BLACK - background color of the final screen.
        """
        self.size = size
        self.surface = pygame.Surface(size)
        self.font = font
        self.font_color = font_color
        self.bg_color = bg_color

        self.score = score
        self.name = ""

    def get_surface(self):
        """
        returns the surface of final screen.
        """
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
        """
        set_name(name(str))
        returns - None

        Sets the name of the player.
        """
        self.name = name

    def set_score(self, score):
        """
        set_score(score(int or float))
        returns - None

        Sets the score of the player.
        """
        self.score = score

    def get_name(self):
        """
        get_name()
        returns the name of the player(str)
        """
        return self.name

    def get_score(self):
        """
        get_score()
        returns the score of the player(str)
        """
        return self.score


class Leaderboard:
    def __init__(self, leaderboard_path='leaderboard.csv', logger=None):
        """
        Leaderboard used to save player scores in csv file.

        arguments:
        leaderboard_path(str)='leaderboard.csv' - path to the leaderboard file
        logger(Logger or None)=None - if None is passed no logging is done, otherwise logger is used to do it.
        """
        self.path = leaderboard_path

        if logger is None:
            self.logging = False
        else:
            self.logging = True
            self.logger = logger

            self.obj_id = hash(leaderboard_path)
            self.obj_name = "Leaderboard"
            self.obj_properties = {'path': self.path}

            self.logger.init(self)

    def write(self, name, score):
        """
        write(name(str), score(int or float))
        adds new score to the leaderboard
        """
        with open(self.path, 'a') as file:
            file.write(f"{name},{score}\n")
            if self.logging:
                self.logger.log(self, f"Score saved. {name=}, {score=}")

    def get_obj_id(self):
        """
        returns id generated from the hash of final_screen surface. Used for logging.
        """
        return self.obj_id

    def get_obj_name(self):
        """
        returns name of the object. Used for logging.
        """
        return self.obj_name

    def get_obj_properties(self):
        """
        returns object properties. Used for logging.
        """
        return self.obj_properties

    def get_name(self):
        """
        returns the path to the leaderboard. Used  for logging purposes.
        """
        return self.path
