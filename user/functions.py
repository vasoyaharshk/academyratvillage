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
                        utils.task.repoke_th * settings.PIXELS_PER_MM)
    cam3.put_state('Resp Win')




# resume reading
def function5():
    touch.resume_reading(utils.task.x * settings.PIXELS_PER_MM, utils.task.y * settings.PIXELS_PER_MM,
                         utils.task.correct_th * settings.PIXELS_PER_MM,
                         utils.task.repoke_th * settings.PIXELS_PER_MM)
    cam3.put_state('Resp Win')


#Balma script:
def function6():
    try:
        utils.task.pulse_pal.trigger_pulse(1)
        cam3.put_state('On')
    except:
        print(traceback.format_exc())

#Balma script:
def function7():
    try:
        utils.task.pulse_pal.trigger_pulse(2)
        cam3.put_state('On')
    except:
        print(traceback.format_exc())

def function8():
    cam3.put_state('Correct')
    soundStream.stop(soundVec1)
    print("Correct")



# camera correct and delete screen
def function11():
    try:
        utils.task.pulse_pal.stop_pulse()
    except:
        pass
    cam3.put_state('Correct')
    soundStream.play(soundVec1)
    print("Correct, Reward Sound played")

def loop11(timing):
    window.flip()


# camera miss with grey screen
def function12():
    cam3.put_state('Miss')

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
    cam3.put_state('Incorrect')
    # sound for incorrect 4kHz
    soundStream.play(soundVec2)
    print("Incorrect, Punish Sound played")


# camera incorrect outside theshold with grey screen
def function14():
    try:
        utils.task.pulse_pal.stop_pulse()
    except:
        pass
    cam3.put_state('Punish')
    soundStream.play(soundVec2)
    print("Punish, Punish Sound played")

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


# camera empty and delete screen
def function17():
    cam3.put_state('')
    soundStream.stop(soundVec1)

def loop17(timing):
    window.flip()


# do nothing, used first time you create the bpod to clean old softcodes
def function19():
    pass


# close door2
def function20():
    if utils.state == 1:  # only for non direct tasks
        utils.change_to_state = 2  # first action done, before min_time