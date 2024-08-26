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

            if self.tag == 1:
                if hasattr(functions, 'function1'):
                    functions.function1()
                if hasattr(functions, 'loop1'):
                    self.chrono.reset()
                    self.my_loop = functions.loop1
            if self.tag == 2:
                if hasattr(functions, 'function2'):
                    functions.function2()
                if hasattr(functions, 'loop2'):
                    self.chrono.reset()
                    self.my_loop = functions.loop2
            if self.tag == 3:
                if hasattr(functions, 'function3'):
                    functions.function3()
                if hasattr(functions, 'loop3'):
                    self.chrono.reset()
                    self.my_loop = functions.loop3
            if self.tag == 4:
                if hasattr(functions, 'function4'):
                    functions.function4()
                if hasattr(functions, 'loop4'):
                    self.chrono.reset()
                    self.my_loop = functions.loop4
            if self.tag == 5:
                if hasattr(functions, 'function5'):
                    functions.function5()
                if hasattr(functions, 'loop5'):
                    self.chrono.reset()
                    self.my_loop = functions.loop5
            if self.tag == 6:
                if hasattr(functions, 'function6'):
                    functions.function6()
                if hasattr(functions, 'loop6'):
                    self.chrono.reset()
                    self.my_loop = functions.loop6
            if self.tag == 7:
                if hasattr(functions, 'function7'):
                    functions.function7()
                if hasattr(functions, 'loop7'):
                    self.chrono.reset()
                    self.my_loop = functions.loop7
            if self.tag == 8:
                if hasattr(functions, 'function8'):
                    functions.function8()
                if hasattr(functions, 'loop8'):
                    self.chrono.reset()
                    self.my_loop = functions.loop8
            if self.tag == 9:
                if hasattr(functions, 'function9'):
                    functions.function9()
                if hasattr(functions, 'loop9'):
                    self.chrono.reset()
                    self.my_loop = functions.loop9
            if self.tag == 10:
                if hasattr(functions, 'function10'):
                    functions.function10()
                if hasattr(functions, 'loop10'):
                    self.chrono.reset()
                    self.my_loop = functions.loop10
            if self.tag == 11:
                if hasattr(functions, 'function11'):
                    functions.function11()
                if hasattr(functions, 'loop11'):
                    self.chrono.reset()
                    self.my_loop = functions.loop11
            if self.tag == 12:
                if hasattr(functions, 'function12'):
                    functions.function12()
                if hasattr(functions, 'loop12'):
                    self.chrono.reset()
                    self.my_loop = functions.loop12
            if self.tag == 13:
                if hasattr(functions, 'function13'):
                    functions.function13()
                if hasattr(functions, 'loop13'):
                    self.chrono.reset()
                    self.my_loop = functions.loop13
            if self.tag == 14:
                if hasattr(functions, 'function14'):
                    functions.function14()
                if hasattr(functions, 'loop14'):
                    self.chrono.reset()
                    self.my_loop = functions.loop14
            if self.tag == 15:
                if hasattr(functions, 'function15'):
                    functions.function15()
                if hasattr(functions, 'loop15'):
                    self.chrono.reset()
                    self.my_loop = functions.loop15
            if self.tag == 16:
                if hasattr(functions, 'function16'):
                    functions.function16()
                if hasattr(functions, 'loop16'):
                    self.chrono.reset()
                    self.my_loop = functions.loop16
            if self.tag == 17:
                if hasattr(functions, 'function17'):
                    functions.function17()
                if hasattr(functions, 'loop17'):
                    self.chrono.reset()
                    self.my_loop = functions.loop17
            if self.tag == 18:
                if hasattr(functions, 'function18'):
                    functions.function18()
                if hasattr(functions, 'loop18'):
                    self.chrono.reset()
                    self.my_loop = functions.loop18
            if self.tag == 19:
                if hasattr(functions, 'function19'):
                    functions.function19()
                if hasattr(functions, 'loop19'):
                    self.chrono.reset()
                    self.my_loop = functions.loop19
            if self.tag == 20:
                if hasattr(functions, 'function20'):
                    functions.function20()
                if hasattr(functions, 'loop20'):
                    self.chrono.reset()
                    self.my_loop = functions.loop20
            if self.tag == 21:
                if hasattr(functions, 'function21'):
                    functions.function21()
                if hasattr(functions, 'loop21'):
                    self.chrono.reset()
                    self.my_loop = functions.loop21
            if self.tag == 22:
                if hasattr(functions, 'function22'):
                    functions.function22()
                if hasattr(functions, 'loop22'):
                    self.chrono.reset()
                    self.my_loop = functions.loop22
            if self.tag == 23:
                if hasattr(functions, 'function23'):
                    functions.function23()
                if hasattr(functions, 'loop23'):
                    self.chrono.reset()
                    self.my_loop = functions.loop23
            if self.tag == 24:
                if hasattr(functions, 'function24'):
                    functions.function24()
                if hasattr(functions, 'loop24'):
                    self.chrono.reset()
                    self.my_loop = functions.loop24
            if self.tag == 25:
                if hasattr(functions, 'function25'):
                    functions.function25()
                if hasattr(functions, 'loop25'):
                    self.chrono.reset()
                    self.my_loop = functions.loop25

        self.my_loop(self.chrono.get_seconds())


class FakeWindow:
    def __init__(self):
        self.name = 'fake'

    def flip(self):
        pass


screen = Screen()
