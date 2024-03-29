import os
from psychopy import visual, logging
from user import settings


# to avoid the recurrent psychopy monitor warning
logging.console.setLevel(logging.CRITICAL)



# create the window
window = visual.Window(size=settings.WIN_RESOLUTION, screen=settings.SCREEN_NUMBER, color=settings.WIN_COLOR,
                       units='pix', fullscr=False, viewPos=settings.VIEW_POSITION)
os.system('wmctrl -r "PsychoPy" -b add,above')





# create all the stimuli you will use in all tasks
square = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

square2 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

square3 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))


# squares = []
# x_positions=[30, 200, 360]
# y_positions=125
# for i in range(3):
#     squares.append(visual.Rect(win=window,
#                                 height=settings.WIN_RESOLUTION[1],
#                                 width=30,
#                                 units='pix',
#                                 lineColor= [0.2, 0.2, 0.2],
#                                 fillColor= [0.2, 0.2, 0.2],
#                                 pos=(x_positions[i], y_positions)))


white_screen = visual.Rect(win=window,
                           width=settings.WIN_RESOLUTION[0],
                           height=settings.WIN_RESOLUTION[1],
                           units='pix',
                           fillColor=[1, 1, 1],
                           pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))