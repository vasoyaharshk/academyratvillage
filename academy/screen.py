import os
from user import functions
from user import settings
from academy import time_utils


os.system(settings.XINPUT)


class Screen:
    def __init__(self):
        if hasattr(functions, 'window'):
            self.win = functions.window
        else:
            self.win = FakeWindow()

        self.tag = None
        self.first = True
        self.chrono = time_utils.Chrono()
        self.my_loop = lambda *args, **kwargs: None

    def play(self):
        if self.first:
            self.first = False

            # Dynamically build the function and loop names based on self.tag
            func_name = f'function{self.tag}'
            loop_name = f'loop{self.tag}'

            # Use getattr to get the function and loop dynamically
            if hasattr(functions, func_name):
                getattr(functions, func_name)()
            if hasattr(functions, loop_name):
                self.chrono.reset()
                self.my_loop = getattr(functions, loop_name)

        self.my_loop(self.chrono.get_seconds())


class FakeWindow:
    def __init__(self):
        self.name = 'fake'

    def flip(self):
        pass


screen = Screen()