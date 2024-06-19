from user import settings
from academy.utils import utils
from academy.camera import cam2, cam3
from academy.touch import touch
from user.psychopy_elements import window, square, square2, square3

# when softcode n is called, function n runs once
# then loop n runs until another softcode is called


# draw a temporal white rectange  with task.x, task.y, task.width and task.stim_duration
def function1():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    # modify contrast
    # cont = float(utils.task.contrast) - 1
    # square.fillColor = [cont, cont, cont]
    # square.lineColor = [cont, cont, cont]
def loop1(timing):
    if timing < utils.task.stim_duration:
        square.draw()
    window.flip()

# draw a permanent white rectange  with task.x, task.y, task.width
def function2():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    # modify contrast
    # cont = float(utils.task.contrast) - 1
    # square.fillColor = [cont, cont, cont]
    # square.lineColor = [cont, cont, cont]
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
    cam2.put_state('Resp Win')
    cam3.put_state('Resp Win')




# resume reading
def function5():
    touch.resume_reading(utils.task.x * settings.PIXELS_PER_MM, utils.task.y * settings.PIXELS_PER_MM,
                         utils.task.correct_th * settings.PIXELS_PER_MM,
                         utils.task.repoke_th * settings.PIXELS_PER_MM)
    cam2.put_state('Resp Win')
    cam3.put_state('Resp Win')




# camera correct and delete screen
def function11():
    cam2.put_state('Correct')
    cam3.put_state('Correct')

def loop11(timing):
    window.flip()




# camera miss with grey screen
def function12():
    cam2.put_state('Miss')
    cam3.put_state('Miss')

def loop12(timing):
    # white_screen.draw()
    window.flip()


# camera incorrect
def function13():
    cam2.put_state('Incorrect')
    cam3.put_state('Incorrect')




# camera incorrect outside theshold with grey screen
def function14():
    cam2.put_state('Punish')
    cam3.put_state('Punish')

def loop14(timing):
    # white_screen.draw()
    window.flip()




# camera empty and delete screen
def function15():
    cam2.put_state('')
    cam3.put_state('')

def loop15(timing):
    window.flip()




# communication is ok
def function16():
    #print('softcode 16 received')
    utils.control_softcodes += 1


# do nothing, used first time you create the bpod to clean old softcodes
def function19():
    pass


# close door2
def function20():
    if utils.state == 1:  # only for non direct tasks
        utils.change_to_state = 2  # first action done, before min_time
