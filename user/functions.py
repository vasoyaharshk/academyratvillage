from user import settings
from academy.utils import utils
from academy.camera import cam3
from academy.touch import touch
from user.psychopy_elements import window, square, square2, square3
from user.sound_elements import soundStream, soundVec1, soundVec2
import traceback

# when softcode n is called, function n runs once
# then loop n runs until another softcode is called


# draw a temporal white rectange  with task.x, task.y, task.width and task.stim_duration
def function1():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    # modify contrast: from 1 unchanged to 0
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
def loop1(timing):
    if timing < utils.task.stim_duration:
        square.draw()
    window.flip()

# draw a permanent white rectange  with task.x, task.y, task.width
def function2():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    # modify contrast
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
def loop2(timing):
    square.draw()
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
    #cont = float(utils.task.contrast) - 1
    cont = 0
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    square2.fillColor = [cont, cont, cont]
    square2.lineColor = [cont, cont, cont]
    square3.fillColor = [cont, cont, cont]
    square3.lineColor = [cont, cont, cont]

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
                        utils.task.repoke_th * settings.PIXELS_PER_MM)
    cam3.put_state('Resp Win')




# resume reading
def function5():
    touch.resume_reading(utils.task.x * settings.PIXELS_PER_MM, utils.task.y * settings.PIXELS_PER_MM,
                         utils.task.correct_th * settings.PIXELS_PER_MM,
                         utils.task.repoke_th * settings.PIXELS_PER_MM)
    cam3.put_state('Resp Win')




def function8():
    square.pos = (int(utils.task.positionx * settings.PIXELS_PER_MM), int(utils.task.positiony * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.fillColor = utils.task.color
    square.lineColor = utils.task.color
def loop8(timing):
    square.draw()
    window.flip()

def function9():
    pass

def loop9(timing):
    window.flip()


#Test Photogate:
def function10():
    print("Animal Crossed")
    soundStream.play(soundVec1)


# camera correct and delete screen
def function11():
    cam3.put_state('Correct')

def loop11(timing):
    window.flip()




# camera miss with grey screen
def function12():
    cam3.put_state('Miss')

def loop12(timing):
    # white_screen.draw()
    window.flip()


# camera incorrect
def function13():
    cam3.put_state('Incorrect')




# camera incorrect outside theshold with grey screen
def function14():
    cam3.put_state('Punish')

def loop14(timing):
    # white_screen.draw()
    window.flip()




# camera empty and delete screen
def function15():
    cam3.put_state('')

def loop15(timing):
    window.flip()




# communication is ok
def function16():
    #print('softcode 16 received')
    utils.control_softcodes += 1


def function17():
    #sound for correct 16KHz
    soundStream.play(soundVec1)
    print("Reward Sound played")


def function18():
    # sound for incorrect 4kHz
    soundStream.play(soundVec2)
    print("Punish Sound played")



# do nothing, used first time you create the bpod to clean old softcodes
def function19():
    pass


# close door2
def function20():
    if utils.state == 1:  # only for non direct tasks
        utils.change_to_state = 2  # first action done, before min_time