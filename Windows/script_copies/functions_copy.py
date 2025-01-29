from user import settings
from academy.utils import utils
from academy.camera import cam2, cam3
from academy.touch import touch
from user.psychopy_elements import window ,square, square2, square3, border1, border2, border3, image_jar_left, image_jar_right, circle_correcth
from user.sound_elements import soundStream, soundVec1, soundVec2, soundVec3
import random
import os
import re

import traceback

# when softcode n is called, function n runs once
# then loop n runs until another softcode is called

# draw a temporary white rectangle  with task.x, task.y, task.width and task.stim_duration
def function1():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.height = int(utils.task.height * settings.PIXELS_PER_MM)
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

def loop1(timing):
    if timing < utils.task.stim_duration:
        square.draw()
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()


# draw a permanent white rectangle  with task.x, task.y, task.width
def function2():
    square.pos = (int(utils.task.x * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    square.width = int(utils.task.width * settings.PIXELS_PER_MM)
    square.height = int(utils.task.height * settings.PIXELS_PER_MM)
    cont = float(utils.task.contrast) - 1
    square.fillColor = [cont, cont, cont]
    square.lineColor = [cont, cont, cont]
    print('Stimulus 2 Shown')

    # Create a red-bordered rectangle for all the three stim: self.x_positions = [65, 188, 309]
    border1.pos = (int(65 * settings.PIXELS_PER_MM), int(utils.task.y * settings.PIXELS_PER_MM))
    border1.width = int(utils.task.width * settings.PIXELS_PER_MM)
    border1.height = int(utils.task.height * settings.PIXELS_PER_MM)
    border1.lineColor = [1, 1, -1],  # Green color for the border
    border1.lineWidth = 1 * settings.PIXELS_PER_MM  # This sets the line width to 1 mm  # Green color for the border
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

    cont = float(utils.task.contrast) - 1
    #cont = 0
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


def function9():
    soundStream.stop(soundVec1)  #14Khz sound played

    cam2.put_state("Correct")
    cam3.put_state("Correct")
    print("Correct")


# camera correct and delete screen
def function11():
    soundStream.play(soundVec1)     #14Khz sound played

    cam2.put_state("Correct")
    cam3.put_state("Correct")
    print("Correct, Reward Sound played")

def loop11(timing):
    window.flip()


# camera miss with grey screen
def function12():
    cam2.put_state("Miss")
    cam3.put_state("Miss")

def loop12(timing):
    window.flip()


# camera incorrect
def function13():
    soundStream.play(soundVec2)     #4Khz sound played

    cam2.put_state("Incorrect")
    cam3.put_state("Incorrect")
    print("Incorrect, Punish Sound played")


def function14():
    soundStream.play(soundVec3)  # 4Khz sound played

    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

def loop14(timing):
    # white_screen.draw()
    window.flip()


# camera empty and delete screen
def function15():
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

    cam2.put_state("")
    cam3.put_state("")

def loop15(timing):
    border1.draw()
    border2.draw()
    border3.draw()
    window.flip()


# camera empty and delete screen
def function17():
    soundStream.stop(soundVec1)

    cam2.put_state("")
    cam3.put_state("")

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


#No mask testing functions from 21 to 25:
# start reading touchscreen:
def function21():
    width = (utils.task.width + 25) * settings.PIXELS_PER_MM      #+25 because we need 1cm more than the stim
    height = (utils.task.height + 25) * settings.PIXELS_PER_MM    #+25 because we need 1cm more than the stim

    touch.start_reading_wm_no_mask(utils.task.response_duration, utils.task.x * settings.PIXELS_PER_MM,
                        utils.task.y * settings.PIXELS_PER_MM, utils.task.correct_th * settings.PIXELS_PER_MM,
        utils.task.repoke_th * settings.PIXELS_PER_MM, utils.task.x_incorrect1 * settings.PIXELS_PER_MM, utils.task.x_incorrect2 * settings.PIXELS_PER_MM, width, height)

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win')

#Resume Reading
def function22():
    width = (utils.task.width + 25) * settings.PIXELS_PER_MM      #+25 because we need 1cm more than the stim
    height = (utils.task.height + 25) * settings.PIXELS_PER_MM    #+25 because we need 1cm more than the stim

    touch.resume_reading_wm_no_mask(utils.task.x * settings.PIXELS_PER_MM, utils.task.y * settings.PIXELS_PER_MM,
                         utils.task.correct_th * settings.PIXELS_PER_MM,
        utils.task.repoke_th * settings.PIXELS_PER_MM, utils.task.x_incorrect1 * settings.PIXELS_PER_MM, utils.task.x_incorrect2 * settings.PIXELS_PER_MM, width, height)

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


last_function_called = None     # Global variable to track the last function called
image_path = None  # Global variable to store the image path
#random_image_path_left = None
#random_image_path_right = None

# Functions for Probability Inference Tasks for different stages where the correct answer is left:
def function31():  # When the blue jar is on left
    global last_function_called, image_path
    last_function_called = 31  # Track that function31 was called

    stage = utils.task.stage
    left_images = []
    try:
        # Get all the images based on the stages
        if stage == 1:
            image_folder = '/home/ratvillage01/academy/jars/1_indication'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and 'left' in f.lower()]
        elif stage == 2:
            image_folder = '/home/ratvillage01/academy/jars/2_discrimination_1'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif stage == 3:
            image_folder = '/home/ratvillage01/academy/jars/3_discrimination_2'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left: ', random_image_path_left)

        image_path = random_image_path_left     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop31(timing):
    image_jar_left.draw()
    window.flip()


# Functions for Probability Inference Tasks for different stages where the correct answer is right:
def function32():  # When the blue jar is on right
    global last_function_called, image_path
    last_function_called = 32  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    try:
        # Get all the images based on the stages
        if stage == 1:
            image_folder = '/home/ratvillage01/academy/jars/1_indication'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and 'right' in f.lower()]
        elif stage == 2:
            image_folder = '/home/ratvillage01/academy/jars/2_discrimination_1'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif stage == 3:
            image_folder = '/home/ratvillage01/academy/jars/3_discrimination_2'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right:', random_image_path_right)

        image_path = random_image_path_right     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")


def loop32(timing):
    image_jar_right.draw()
    window.flip()

#
# # Start reading touchscreen for Probabilistic inference tasks with all touches processed:
# def function33():
#     width = utils.task.width * settings.PIXELS_PER_MM
#     height = utils.task.height * settings.PIXELS_PER_MM
#     x_correct = utils.task.x_correcth * settings.PIXELS_PER_MM
#     x_incorrect = utils.task.x_incorrecth
#     y = utils.task.y_correcth * settings.PIXELS_PER_MM
#
#     if x_incorrect is None:
#         touch.start_reading_probability(utils.task.response_duration, x_correct, None, y, width, height)
#     else:
#         x_incorrect = utils.task.x_incorrecth * settings.PIXELS_PER_MM
#         touch.start_reading_probability(utils.task.response_duration, x_correct, x_incorrect, y, width, height)
#
#     cam2.put_state("Resp Win")
#     cam3.put_state("Resp Win")
#     print('Resp Win 1')
#     #print('x_correct in functions: ', x_correct)
#     #print('x_incorrect in functions: ', x_incorrect)


# Start reading touchscreen for Probabilistic inference tasks with only one touch processing:
def function34():
    width = utils.task.width * settings.PIXELS_PER_MM
    height = utils.task.height * settings.PIXELS_PER_MM
    x_correct = utils.task.x_correcth * settings.PIXELS_PER_MM
    x_incorrect = utils.task.x_incorrecth
    y = utils.task.y_correcth * settings.PIXELS_PER_MM

    if x_incorrect is None:
        touch.start_reading_probability_first_touch(utils.task.response_duration, x_correct, None, y, width, height)
    else:
        x_incorrect = utils.task.x_incorrecth * settings.PIXELS_PER_MM
        touch.start_reading_probability_first_touch(utils.task.response_duration, x_correct, x_incorrect, y, width, height)

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win 1')
    #print('x_correct in functions: ', x_correct)
    #print('x_incorrect in functions: ', x_incorrect)


#Display camera correct, play correct sound and display correct stimuli FOR PROBABILISTIC INFERENCE TASK AND WEBER'S LAW.
def function35():
    #soundStream.play(soundVec1)

    cam2.put_state("Correct")
    cam3.put_state("Correct")
    #print("Correct, Reward Sound played")

    stage = utils.task.stage
    if stage != 1:
        # Replace "both" with "correct" in the image path
        if image_path and "both" in image_path:
            image_path_replaced = image_path.replace("both", "correct")
            # Update the image path for drawing
            if last_function_called in [31, 41, 43, 45, 51, 61]:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            elif last_function_called in [32, 42, 44, 46, 52, 62]:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
        print(f"Correct image path: {image_path_replaced}")

def loop35(timing):
    # Check which function (31 or 32) was last called and display the corresponding image:
    stage = utils.task.stage
    if stage != 1:
        if last_function_called in [31, 41, 43, 45, 51, 61]:
            #print("Last function called: ", last_function_called)
            image_jar_left.draw()
        elif last_function_called in [32, 42, 44, 46, 52, 62]:
            #print("Last function called: ", last_function_called)
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


# Display camera Punish, play punish sound and display incorrect stimuli FOR PROBABILISTIC INFERENCE TASK AND WEBER'S LAW AND WEBER'S LAW TRAINING.
def function36():
    soundStream.play(soundVec3)

    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    stage = utils.task.stage
    if stage != 1:
        # Replace "both" with "correct" in the image path
        if image_path and "both" in image_path:
            image_path_replaced = image_path.replace("both", "incorrect")
            # Update the image path for drawing
            if last_function_called in [31, 41, 43, 45, 51, 61]:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            elif last_function_called in [32, 42, 44, 46, 52, 62]:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
        print(f"Incorrect image path: {image_path_replaced}")
    else:
        pass

def loop36(timing):
    # Check which function (31 or 32) was last called and display the corresponding image:
    stage = utils.task.stage
    if stage != 1:
        if last_function_called in [31, 41, 43, 45, 51, 61]:
            #print("Last function called: ", last_function_called)
            image_jar_left.draw()
        elif last_function_called in [32, 42, 44, 46, 52, 62]:
            #print("Last function called: ", last_function_called)
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


#Miss:
def function37():
    #soundStream.play(soundVec3)  #4Khz sound played

    cam2.put_state("Miss")
    cam3.put_state("Miss")
    print("No response, miss")

def loop37(timing):
    window.flip()


#Correct without image display:
def function38():
    soundStream.play(soundVec1)

    cam2.put_state("Correct")
    cam3.put_state("Correct")
    print("Correct, Reward Sound played")


#Punish without image display:
def function39():
    #soundStream.play(soundVec3)

    cam2.put_state("Punish")
    cam3.put_state("Punish")
    #print("Punish, Punish Sound played")


#Miss:
def function40():
    pass

def loop40(timing):
    window.flip()

## FUNCTIONS FROM 41 TO 46 ARE FOR WEBER'S LAW.
# Functions for Probability Inference Tasks for different stages where the correct answer is left:
def function41():  # When the correct answer is on left
    global last_function_called, image_path
    last_function_called = 41  # Track that function41 was called

    stage = utils.task.stage
    current_condition = utils.task.current_condition
    left_images = []
    try:
        image_folder = f'/home/ratvillage01/academy/jars/4_webers_law/{current_condition}'
        left_images = [f for f in os.listdir(image_folder) if
                       os.path.isfile(os.path.join(image_folder, f)) and
                       ('left' in f.lower() and 'both' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left: ', random_image_path_left)

        image_path = random_image_path_left     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop41(timing):
    image_jar_left.draw()
    window.flip()


# Functions for Probability Inference Tasks for different stages where the correct answer is right:
def function42():  # When the correct answer is on right
    global last_function_called, image_path
    last_function_called = 42  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    current_condition = utils.task.current_condition

    try:
        # Get all the images based on the stages
        image_folder = f'/home/ratvillage01/academy/jars/4_webers_law/{current_condition}'
        right_images = [f for f in os.listdir(image_folder) if
                        os.path.isfile(os.path.join(image_folder, f)) and
                        ('right' in f.lower() and 'both' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right:', random_image_path_right)

        image_path = random_image_path_right     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")


def loop42(timing):
    image_jar_right.draw()
    window.flip()


#Function 43 to 46 are for conditions 1 and 2 for ror 1 in weber's law 43 is for Left-Small, 44 for for Right-Small, 45 is for Left-Big, 46 for for Right-Big:
def function43():
    global last_function_called, image_path
    last_function_called = 43  # Track that function41 was called

    stage = utils.task.stage
    current_condition = utils.task.current_condition
    left_images = []
    try:
        image_folder = f'/home/ratvillage01/academy/jars/4_webers_law/{current_condition}'
        left_images = [f for f in os.listdir(image_folder) if
                       os.path.isfile(os.path.join(image_folder, f)) and
                       ('left' in f.lower() and 'both' in f.lower() and 'small' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left, small jar: ', random_image_path_left)

        image_path = random_image_path_left  # Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop43(timing):
    image_jar_left.draw()
    window.flip()


def function44():
    global last_function_called, image_path
    last_function_called = 44  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    current_condition = utils.task.current_condition

    try:
        # Get all the images based on the stages
        image_folder = f'/home/ratvillage01/academy/jars/4_webers_law/{current_condition}'
        right_images = [f for f in os.listdir(image_folder) if
                        os.path.isfile(os.path.join(image_folder, f)) and
                        ('right' in f.lower() and 'both' in f.lower() and 'small' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right, small jar:', random_image_path_right)

        image_path = random_image_path_right  # Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop44(timing):
    image_jar_right.draw()
    window.flip()


def function45():
    global last_function_called, image_path
    last_function_called = 45  # Track that function41 was called

    stage = utils.task.stage
    current_condition = utils.task.current_condition
    left_images = []
    try:
        image_folder = f'/home/ratvillage01/academy/jars/4_webers_law/{current_condition}'
        left_images = [f for f in os.listdir(image_folder) if
                       os.path.isfile(os.path.join(image_folder, f)) and
                       ('left' in f.lower() and 'both' in f.lower() and 'big' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left, big jar: ', random_image_path_left)

        image_path = random_image_path_left  # Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop45(timing):
    image_jar_left.draw()
    window.flip()


def function46():
    global last_function_called, image_path
    last_function_called = 46  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    current_condition = utils.task.current_condition

    try:
        # Get all the images based on the stages
        image_folder = f'/home/ratvillage01/academy/jars/4_webers_law/{current_condition}'
        right_images = [f for f in os.listdir(image_folder) if
                        os.path.isfile(os.path.join(image_folder, f)) and
                        ('right' in f.lower() and 'both' in f.lower() and 'big' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right, big jar:', random_image_path_right)

        image_path = random_image_path_right  # Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop46(timing):
    image_jar_right.draw()
    window.flip()


## FUNCTIONS FROM 50 TO 56 ARE FOR EASY TRAINING.
# Functions for Probability Inference Tasks for different stages where the correct answer is left:
def function51():  # When the blue jar is on left
    global last_function_called, image_path
    last_function_called = 51  # Track that function31 was called

    substage = utils.task.substage
    left_images = []
    try:
        # Get all the images based on the stages
        if substage == 1:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_1_indication'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and 'left' in f.lower()]
        elif substage == 2:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_2_discrimination_1'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 3:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_3_discrimination_2'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 4:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_4_discrimination_3'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 5:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_5_discrimination_4'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left: ', random_image_path_left)

        image_path = random_image_path_left     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop51(timing):
    image_jar_left.draw()
    window.flip()


# Functions for Probability Inference Tasks for different stages where the correct answer is right:
def function52():  # When the blue jar is on right
    global last_function_called, image_path
    last_function_called = 52  # Track that function31 was called

    substage = utils.task.substage
    right_images = []
    try:
        # Get all the images based on the stages
        if substage == 1:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_1_indication'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and 'right' in f.lower()]
        elif substage == 2:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_2_discrimination_1'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 3:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_3_discrimination_2'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 4:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_4_discrimination_3'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 5:
            image_folder = '/home/ratvillage01/academy/jars/0_extra_training/1_5_discrimination_4'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right:', random_image_path_right)

        image_path = random_image_path_right     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")


def loop52(timing):
    image_jar_right.draw()
    window.flip()


#Display camera correct, play correct sound and display correct stimuli for EASY TRAINING:.
def function55():
    #soundStream.play(soundVec1)

    cam2.put_state("Correct")
    cam3.put_state("Correct")
    #print("Correct, Reward Sound played")

    substage = utils.task.substage
    if substage != 1:
        # Replace "both" with "correct" in the image path
        if image_path and "both" in image_path:
            image_path_replaced = image_path.replace("both", "correct")
            # Update the image path for drawing
            if last_function_called in [31, 41, 51]:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            elif last_function_called in [32, 42, 52]:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
        print(f"Correct image path: {image_path_replaced}")

def loop55(timing):
    # Check which function (31 or 32) was last called and display the corresponding image:
    substage = utils.task.substage
    if substage != 1:
        if last_function_called in [31, 41, 51]:
            #print("Last function called: ", last_function_called)
            image_jar_left.draw()
        elif last_function_called in [32, 42, 52]:
            #print("Last function called: ", last_function_called)
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


# Display camera correct, play punish sound and display incorrect stimuli.
def function56():
    soundStream.play(soundVec3)

    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    substage = utils.task.substage
    if substage != 1:
        # Replace "both" with "correct" in the image path
        if image_path and "both" in image_path:
            image_path_replaced = image_path.replace("both", "incorrect")
            # Update the image path for drawing
            if last_function_called in [31, 41, 51]:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            elif last_function_called in [32, 42, 52]:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
        print(f"Incorrect image path: {image_path_replaced}")
    else:
        pass

def loop56(timing):
    # Check which function (31 or 32) was last called and display the corresponding image:
    substage = utils.task.substage
    if substage != 1:
        if last_function_called in [31, 41, 51]:
            #print("Last function called: ", last_function_called)
            image_jar_left.draw()
        elif last_function_called in [32, 42, 52]:
            #print("Last function called: ", last_function_called)
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()

## FUNCTIONS FROM 60 TO 70 ARE FOR WEBER'S LAW TRAINING.
def function61():  # When the correct answer is on left
    global last_function_called, image_path
    last_function_called = 61  # Track that function41 was called

    stage = utils.task.stage
    trial_condition = utils.task.trial_condition
    left_images = []

    print('Trial Condition: ', trial_condition)

    try:
        image_folder = f'/home/ratvillage01/academy/jars/5_webers_law_training/{trial_condition}'
        left_images = [f for f in os.listdir(image_folder) if
                       os.path.isfile(os.path.join(image_folder, f)) and
                       ('left' in f.lower() and 'both' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left: ', random_image_path_left)

        image_path = random_image_path_left     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop61(timing):
    image_jar_left.draw()
    window.flip()


def function62():  # When the correct answer is on right
    global last_function_called, image_path
    last_function_called = 62  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    trial_condition = utils.task.trial_condition

    print('Trial Condition: ', trial_condition)

    try:
        # Get all the images based on the stages
        image_folder = f'/home/ratvillage01/academy/jars/5_webers_law_training/{trial_condition}'
        right_images = [f for f in os.listdir(image_folder) if
                        os.path.isfile(os.path.join(image_folder, f)) and
                        ('right' in f.lower() and 'both' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right:', random_image_path_right)

        image_path = random_image_path_right     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")


def loop62(timing):
    image_jar_right.draw()
    window.flip()


#Display camera correct, play correct sound and display correct stimuli FOR WEBER'S LAW TRAINING.
def function63():
    #soundStream.play(soundVec1)

    cam2.put_state("Correct")
    cam3.put_state("Correct")
    #print("Correct, Reward Sound played")

    stage = utils.task.stage
    if stage != 1:
        # Replace "both" with "correct" in the image path
        if image_path and "both" in image_path:
            print(f"Original image path: {image_path}")
            # Split into directory and filename
            directory, filename = os.path.split(image_path)
            # Remove everything after the last underscore
            filename = re.sub(r'_[^_]+_[^_]+\.png$', '.png', filename)
            # Replace "both" with "correct"
            filename = filename.replace("both", "correct")
            # Recombine the directory and modified filename
            image_path_replaced = os.path.join(directory, filename)
            print(f"Modified image path is {image_path_replaced}")
            # Update the image path for drawing
            if last_function_called in [61]:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            elif last_function_called in [62]:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop63(timing):
    # Check which function (31 or 32) was last called and display the corresponding image:
    stage = utils.task.stage
    if stage != 1:
        if last_function_called in [61]:
            #print("Last function called: ", last_function_called)
            image_jar_left.draw()
        elif last_function_called in [62]:
            #print("Last function called: ", last_function_called)
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


# Display camera Punish, play punish sound and display incorrect stimuli FOR WEBER'S LAW TRAINING.
def function64():
    soundStream.play(soundVec3)

    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    stage = utils.task.stage
    if stage != 1:
        # Replace "both" with "correct" in the image path
        if image_path and "both" in image_path:
            print(f"Original image path: {image_path}")
            # Split into directory and filename
            directory, filename = os.path.split(image_path)
            # Remove all "[digit]c_" patterns
            filename = re.sub(r'\d+c_', '', filename)
            # Replace "both" with "incorrect"
            filename = filename.replace("both", "incorrect")
            # Remove the final "_digits" before ".png"
            filename = re.sub(r'_\d+(?=\.png)', '', filename)
            # Recombine the directory and modified filename
            image_path_replaced = os.path.join(directory, filename)
            print(f"Modified image path is {image_path_replaced}")
            # Update the image path for drawing
            if last_function_called in [61]:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            elif last_function_called in [62]:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
            print(f"Incorrect image path: {image_path_replaced}")


def loop64(timing):
    # Check which function (31 or 32) was last called and display the corresponding image:
    stage = utils.task.stage
    if stage != 1:
        if last_function_called in [61]:
            #print("Last function called: ", last_function_called)
            image_jar_left.draw()
        elif last_function_called in [62]:
            #print("Last function called: ", last_function_called)
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


## FUNCTIONS FROM 70 TO 80 ARE FOR TURTLE STYLE EXPERIMENT:
def function71():  # When the correct stimuli is on left
    global last_function_called, image_path
    last_function_called = 71  # Track that function31 was called

    substage = utils.task.substage
    left_images = []
    try:
        # Get all the images based on the stages
        if substage == 0:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/0_pre_training'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 1:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/1_training'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 2:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/2_training'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 3:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/3_training'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]

        if not left_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the left_images list
        random_image_path_left = os.path.join(image_folder, random.choice(left_images))

        image_jar_left.image = random_image_path_left
        image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage: ', utils.task.stage)
        print('Correct answer on left: ', random_image_path_left)

        image_path = random_image_path_left     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")

def loop71(timing):
    image_jar_left.draw()
    window.flip()


# Functions for Probability Inference Tasks for different stages where the correct answer is right:
def function72():  # When the correct stimuli is on right
    global last_function_called, image_path
    last_function_called = 72  # Track that function31 was called

    substage = utils.task.substage
    right_images = []
    try:
        # Get all the images based on the stages
        if substage == 0:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/0_pre_training'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 1:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/1_training'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 2:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/2_training'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 3:
            image_folder = '/home/harsh/academy/jars/6_turtle_style/3_training'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]

        if not right_images:
            raise ValueError(f"No images found in {image_folder} for stage {stage}.")

        # Choose a random image from the right_images list
        random_image_path_right = os.path.join(image_folder, random.choice(right_images))

        image_jar_right.image = random_image_path_right
        image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

        print('Stage:', utils.task.stage)
        print('Correct answer on right:', random_image_path_right)

        image_path = random_image_path_right     #Used in Function 35 or function 36 afterwards.

    except Exception as e:
        print(f"Error occurred: {e}")


def loop72(timing):
    image_jar_right.draw()
    window.flip()


# start reading touchscreen:
def function73():
    width = utils.task.width * settings.PIXELS_PER_MM
    height = utils.task.height * settings.PIXELS_PER_MM
    x_correct = utils.task.x_correcth * settings.PIXELS_PER_MM
    x_incorrect = utils.task.x_incorrecth
    y = utils.task.y_correcth * settings.PIXELS_PER_MM

    if x_incorrect is None:
        touch.start_reading_probability_turtle(utils.task.response_duration, x_correct, None, y, width, height)
    else:
        x_incorrect = utils.task.x_incorrecth * settings.PIXELS_PER_MM
        touch.start_reading_probability_turtle(utils.task.response_duration, x_correct, x_incorrect, y, width, height)

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win 1')
    #print('x_correct in functions: ', x_correct)
    #print('x_incorrect in functions: ', x_incorrect)

#Resume Reading
def function74():
    width = utils.task.width * settings.PIXELS_PER_MM
    height = utils.task.height * settings.PIXELS_PER_MM
    x_correct = utils.task.x_correcth * settings.PIXELS_PER_MM
    x_incorrect = utils.task.x_incorrecth
    y = utils.task.y_correcth * settings.PIXELS_PER_MM

    if x_incorrect is None:
        touch.start_reading_probability_turtle(utils.task.response_duration, x_correct, None, y, width, height)
    else:
        x_incorrect = utils.task.x_incorrecth * settings.PIXELS_PER_MM
        touch.start_reading_probability_turtle(utils.task.response_duration, x_correct, x_incorrect, y, width, height)

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win 1')
    #print('x_correct in functions: ', x_correct)
    #print('x_incorrect in functions: ', x_incorrect)

