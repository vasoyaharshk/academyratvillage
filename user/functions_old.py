from user import settings
from academy.utils import utils
from academy.camera import cam2, cam3
from academy.touch import touch
from user.psychopy_elements import window, square, square2, square3, jar1, jar2, jar3, border1, border2, border3
from user.sound_elements import soundStream, soundVec1, soundVec2, soundVec3, soundVec4
import traceback

# when softcode n is called, function n runs once
# then loop n runs until another softcode is called


# draw a temporal white rectange  with task.x, task.y, task.width and task.stim_duration
def function1():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.height = int(utils.task.height * settings.PIXELS_PER_MM)
    # modify contrast: from 1 unchanged to 0
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    print('Stimulus 1 Shown')

    # Create a green-bordered rectangle for all the three stim: self.x_positions = [65, 188, 309]
    border1.pos = (int(65 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border1.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border1.lineColor = [1, 1, -1],  # Green color for the border
    border1.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border1.fillColor = None  # No fill color

    border2.pos = (int(188 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border2.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border2.lineColor = [1, 1, -1],  # Green color for the border
    border2.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border2.fillColor = None  # No fill color

    border3.pos = (int(309 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border3.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border3.lineColor = [1, 1, -1],  # Green color for the border
    border3.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border3.fillColor = None  # No fill color

def loop1(timing):
    if timing < utils.task.stim_duration:
        square.draw()
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()


# draw a permanent white rectange  with task.x, task.y, task.width
def function2():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.height = int(utils.task.height * settings.PIXELS_PER_MM)
    # modify contrast
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    print('Stimulus 2 Shown')

    # Create a red-bordered rectangle for all the three stim: self.x_positions = [65, 188, 309]
    border1.pos = (int(65 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border1.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border1.lineColor = [1, 1, -1],  # Green color for the border
    border1.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border1.fillColor = None  # No fill color

    border2.pos = (int(188 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border2.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border2.lineColor = [1, 1, -1],  # Green color for the border
    border2.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border2.fillColor = None  # No fill color

    border3.pos = (int(309 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border3.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border3.lineColor = [1, 1, -1],  # Green color for the border
    border3.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border3.fillColor = None  # No fill color

def loop2(timing):
    square.draw()
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()



# draw a 3 temporal white rectangles (fot touchteaching)  with task.x, task.y, task.width and task.stim_duration
def function3():
    square.pos = (int(utils.task.x[0] * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square2.pos = (int(utils.task.x[1] * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square3.pos = (int(utils.task.x[2] * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    # modify contrast
    cont = float(utils.task.contrast) - 1
    cont = 0
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    square2.fillColor = [cont, cont, cont]
    square2.lineColor = [cont, cont, cont]
    square3.fillColor = [cont, cont, cont]
    square3.lineColor = [cont, cont, cont]
    print('Stimulus Shown')

def loop3(timing):
    square.draw()
    square2.draw()
    square3.draw()
    window.flip()


# start reading touchscreen
def function4():

    try:
        x = utils.task.x[1]
    except:
        x = utils.task.x

    touch.start_reading(utils.task.response_duration, x * settings.PIXELS_PER_MM,
                        utils.task.y * settings.PIXELS_PER_MM, utils.task.correct_th * settings.PIXELS_PER_MM,
        utils.task.repoke_th * settings.PIXELS_PER_MM,
    )
    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win')
    print('Stim Correct: ', utils.task.correct_th * settings.PIXELS_PER_MM)

# resume reading
def function5():
    touch.resume_reading(utils.task.x * settings.PIXELS_PER_MM, utils.task.y * settings.PIXELS_PER_MM,
                         utils.task.correct_th * settings.PIXELS_PER_MM,
        utils.task.repoke_th * settings.PIXELS_PER_MM,
    )
    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win')


#Balma script:
def function6():  #For Stage 1 where the probabilities are 100% blue vs nothing:
    jar1.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    jar1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    print('Stimulus Shown')

def loop6(timing):
    jar1.draw()
    window.flip()

def function7(): #For Stage 2 where the probabilities are 100% blue vs 100% yellow:
    jar1.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    jar1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    jar2.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    jar2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    print('Stimulus Shown')
def loop7(timing):
    jar1.draw()
    jar2.draw()
    window.flip()
def function8():
    cam3.put_state("Correct")
    soundStream.stop(soundVec1)
    print("Correct")

def function9(): #For Stage 3 where the probabilities are 100% yellow vs 50% blue and 50% yellow:
    jar2.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    jar2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    jar3.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    jar3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    print('Stimulus Shown')
def loop9(timing):
    jar2.draw()
    jar3.draw()
    window.flip()

def function10():
    cam2.put_state("Miss")
    cam3.put_state("Miss")
    soundStream.play(soundVec3)
    print("No response Sound played")

def loop10(timing):
    window.flip()

# camera correct and delete screen
def function11():
    try:
        utils.task.pulse_pal.stop_pulse()
    except:
        pass
    cam2.put_state("Correct")
    cam3.put_state("Correct")
    soundStream.play(soundVec1)
    print("Correct, Reward Sound played")

def loop11(timing):
    window.flip()


# camera miss with grey screen
def function12():
    cam2.put_state("Miss")
    cam3.put_state("Miss")


def loop12(timing):
    # white_screen.draw()
    window.flip()


#Balma script:
# camera incorrect
def function13():
    try:
        utils.task.pulse_pal.stop_pulse()
    except:
        pass
    cam2.put_state("Incorrect")
    cam3.put_state("Incorrect")
    # sound for incorrect 4kHz
    soundStream.play(soundVec2)
    print("Incorrect, Punish Sound played")


# camera incorrect outside theshold with grey screen
def function14():
    try:
        utils.task.pulse_pal.stop_pulse()
    except:
        pass
    cam2.put_state("Punish")
    cam3.put_state("Punish")
    soundStream.play(soundVec3)
    print("Punish, Punish Sound played")

def loop14(timing):
    # white_screen.draw()
    window.flip()


# camera empty and delete screen
def function15():
    cam2.put_state("")
    cam3.put_state("")

    # Create a red-bordered rectangle for all the three stim: self.x_positions = [65, 188, 309]
    border1.pos = (int(65 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border1.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border1.lineColor = [1, 1, -1],  # Green color for the border
    border1.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border1.fillColor = None  # No fill color

    border2.pos = (int(188 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border2.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border2.lineColor = [1, 1, -1],  # Green color for the border
    border2.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border2.fillColor = None  # No fill color

    border3.pos = (int(309 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border3.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border3.lineColor = [1, 1, -1],  # Green color for the border
    border3.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border3.fillColor = None  # No fill color


def loop15(timing):
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()


# communication is ok
def function16():
    #print('softcode 16 received')
    utils.control_softcodes += 1


# camera empty and delete screen
def function17():
    cam2.put_state("")
    cam3.put_state("")
    soundStream.stop(soundVec1)

def loop17(timing):
    window.flip()

def function18():
    soundStream.stop(soundVec3)
    print("Punish Sound Stopped")


# do nothing, used first time you create the bpod to clean old softcodes
def function19():
    pass


# close door2
def function20():
    if utils.state == 1:  # only for non direct tasks
        utils.change_to_state = 2  # first action done, before min_time


#Gal-without mask testing functions from 21 to 25:

# start reading touchscreen:
def function21():
    try:
        x = utils.task.x[1]
    except:
        x = utils.task.x

    touch.start_reading(utils.task.response_duration, x * settings.PIXELS_PER_MM,
                        utils.task.y * settings.PIXELS_PER_MM, utils.task.correct_th * settings.PIXELS_PER_MM, utils.task.repoke_th * settings.PIXELS_PER_MM,
                        )

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win')


def function22():
    try:
        x = utils.task.x[1]
    except:
        x = utils.task.x

    touch.start_reading(utils.task.response_duration, x * settings.PIXELS_PER_MM,
                        utils.task.y * settings.PIXELS_PER_MM, utils.task.correct_th * settings.PIXELS_PER_MM, utils.task.repoke_th * settings.PIXELS_PER_MM,
                        )

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win')


def function23():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.height = int(utils.task.height * settings.PIXELS_PER_MM)
    # modify contrast: from 1 unchanged to 0
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    print('Stimulus 1 Shown')

    # Create a red-bordered rectangle for all the three stim: self.x_positions = [65, 188, 309]
    border1.pos = (int(65 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border1.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border1.lineColor = [1, 1, -1],  # Green color for the border
    border1.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border1.fillColor = None  # No fill color

    border2.pos = (int(188 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border2.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border2.lineColor = [1, 1, -1],  # Green color for the border
    border2.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border2.fillColor = None  # No fill color

    border3.pos = (int(309 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border3.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border3.lineColor = [1, 1, -1],  # Green color for the border
    border3.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border3.fillColor = None  # No fill color

def loop23(timing):
    if timing < utils.task.stim_duration:
        square.draw()
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()


# draw a permanent white rectange  with task.x, task.y, task.width
def function24():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.height = int(utils.task.height * settings.PIXELS_PER_MM)
    # modify contrast
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    print('Stimulus 2 Shown')

    # Create a red-bordered rectangle for all the three stim: self.x_positions = [65, 188, 309]
    border1.pos = (int(65 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border1.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border1.lineColor = [1, 1, -1],  # Green color for the border
    border1.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border1.fillColor = None  # No fill color

    border2.pos = (int(188 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border2.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border2.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border2.lineColor = [1, 1, -1],  # Green color for the border
    border2.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border2.fillColor = None  # No fill color

    border3.pos = (int(309 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border3.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border3.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border3.lineColor = [1, 1, -1],  # Green color for the border
    border3.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm
    border3.fillColor = None  # No fill color

def loop24(timing):
    square.draw()
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()

