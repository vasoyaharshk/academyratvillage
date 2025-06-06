import os
import sys
from psychopy import visual, logging
from psychopy.visual import Circle
from user import settings
from psychopy import prefs
prefs.hardware['audioLib'] = ['no sound']

# to avoid the recurrent psychopy monitor warning
logging.console.setLevel(logging.CRITICAL)


# #To avoid the video logs debugging prints. Comment this part if there is a need to debug:
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"  # Ensure FFmpeg path is set
# os.environ["IMAGEIO_FFMPEG_LOGLEVEL"] = "error"  # Suppress FFmpeg logs
# os.environ["FFREPORT"] = "quiet"  # Fully disable FFmpeg reports
# os.environ["IMAGEIO_NO_INTERNET"] = "1"  # Prevent external FFmpeg updates
#
# # Redirect standard error to suppress FFmpeg prints
# sys.stderr = open(os.devnull, "w")

# create the window
window = visual.Window(size=settings.WIN_RESOLUTION, screen=settings.SCREEN_NUMBER, color=settings.WIN_COLOR, units='pix', fullscr=False, viewPos=settings.VIEW_POSITION)

#window = visual.Window(size=settings.WIN_RESOLUTION, screen=settings.SCREEN_NUMBER, color=settings.WIN_COLOR, units='pix', fullscr=False)

os.system('wmctrl -r "PsychoPy" -b add,above')

# create all the stimuli you will use in all tasks
square = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

square2 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

square3 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

square4 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

border1 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

border2 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

border3 = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
                     units='pix',
                     lineColor= [0.2, 0.2, 0.2],
                     fillColor= [0.2, 0.2, 0.2],
                     pos=(int(settings.WIN_RESOLUTION[0] / 2), int(settings.WIN_RESOLUTION[1] / 2)))

correct_border = visual.Rect(win=window,
                     height=settings.WIN_RESOLUTION[1],
                     width=int(settings.STIM_WIDTH * settings.PIXELS_PER_MM_X),
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


image_jar_left = visual.ImageStim(win=window, image=None)  # Image will be set dynamically

image_jar_right = visual.ImageStim(win=window, image=None)  # Image will be set dynamically

circle_correcth = Circle(win=window, radius=1, edges=128, lineColor=[1, 1, -1], fillColor=None)  # Green border, no fill

# Use a placeholder video to avoid NoneType error. This is a dummy video
video_placeholder = "/home/ratvillage01/academy/stimuli/bastos_taylor/placeholder_black_video.mp4"  # Ensure this file exists

# Video Stimuli, sound disabled and filename given to placeholder but is taken from functions.py which takes it from the task.
video_left = visual.MovieStim(win=window, filename=video_placeholder, loop=False, size=(1280, 720), units='pix')
video_right = visual.MovieStim(win=window, filename=video_placeholder, loop=False, size=(1280, 720), units='pix')


image_jar_left_sized = visual.ImageStim(
    win=window,
    image=None,
    size=(1280, 720),
    units='pix'
)

image_jar_right_sized = visual.ImageStim(
    win=window,
    image=None,
    size=(1280, 720),
    units='pix'
)
