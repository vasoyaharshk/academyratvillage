from user import settings
from academy.utils import utils
from academy.camera import cam2, cam3
from academy.touch import touch
from user.psychopy_elements import *
#from user.psychopy_elements import window ,square, square2, square3, border1, border2, border3, image_jar_left, image_jar_right, circle_correcth, video_left, video_right
from user.sound_elements import soundStream, soundVec1, soundVec2, soundVec3
import random
import os
import re

import traceback

# when softcode n is called, function n runs once
# then loop n runs until another softcode is called

# Global sets for function call groups. All odd numbers are for left and even numbers for right
LEFT_FUNCTIONS = {31, 41, 43, 45, 51, 61, 81, 83, 85, 101, 103, 105, 107}
RIGHT_FUNCTIONS = {32, 42, 44, 46, 52, 62, 82, 84, 86, 102, 104, 106, 108}

last_function_called = None  # Global variable to track the last function called
image_path = None  # Global variable to store the image path


def update_image_path_size_position(correct=True):
    global image_path
    if image_path and "both" in image_path:
        print(f"Original image path: {image_path}")
        directory, filename = os.path.split(image_path)
        if correct:
            filename = re.sub(r'_[^_]+_[^_]+\.png$', '.png', filename)
        else:
            filename = re.sub(r'\d+c_', '', filename)
            filename = re.sub(r'_\d+(?=\.png)', '', filename)
        filename = filename.replace("both", "correct" if correct else "incorrect")
        image_path_replaced = os.path.join(directory, filename)
        print(f"Modified image path: {image_path_replaced}")
        return image_path_replaced
    return None


def update_image_path_position(correct=True):
    global image_path
    if image_path and "both" in image_path:
        return image_path.replace("both", "correct" if correct else "incorrect")
    return None

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
def function31():  # When the correct stimuli is on left
    global last_function_called, image_path
    last_function_called = 31  # Track that function31 was called

    image_path = utils.task.image_path_function

    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop31(timing):
    image_jar_left.draw()
    window.flip()


# Functions where the correct answer is right:
def function32():  # When the correct stimuli is on right
    global last_function_called, image_path
    last_function_called = 32  # Track that function31 was called

    image_path = utils.task.image_path_function

    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop32(timing):
    image_jar_right.draw()
    window.flip()


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
    global last_function_called

    cam2.put_state("Correct")
    cam3.put_state("Correct")

    stage = utils.task.stage
    if stage != 1:
        image_path_replaced = update_image_path_position(correct=True)
        if image_path_replaced:
            if last_function_called in LEFT_FUNCTIONS:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = settings.CENTRE_SCREEN
            elif last_function_called in RIGHT_FUNCTIONS:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = settings.CENTRE_SCREEN
            print(f"Correct image path: {image_path_replaced}")
        else:
            print("Warning: image_path is None or does not contain 'both'. No image will be updated.")


def loop35(timing):
    global last_function_called

    stage = utils.task.stage
    if stage != 1:
        if last_function_called in LEFT_FUNCTIONS:
            image_jar_left.draw()
        elif last_function_called in RIGHT_FUNCTIONS:
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


def function36():
    global last_function_called

    soundStream.play(soundVec3)
    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    stage = utils.task.stage
    if stage != 1:
        image_path_replaced = update_image_path_position(correct=False)
        if image_path_replaced:
            if last_function_called in LEFT_FUNCTIONS:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = settings.CENTRE_SCREEN
            elif last_function_called in RIGHT_FUNCTIONS:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = settings.CENTRE_SCREEN
            print(f"Incorrect image path: {image_path_replaced}")
        else:
            print("Warning: image_path is None or does not contain 'both'. No image will be updated.")


def loop36(timing):
    global last_function_called

    stage = utils.task.stage
    if stage != 1:
        if last_function_called in LEFT_FUNCTIONS:
            image_jar_left.draw()
        elif last_function_called in RIGHT_FUNCTIONS:
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
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law/{current_condition}'
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
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law/{current_condition}'
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
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law/{current_condition}'
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
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law/{current_condition}'
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
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law/{current_condition}'
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
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law/{current_condition}'
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
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_1_indication'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and 'left' in f.lower()]
        elif substage == 2:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_2_discrimination_1'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 3:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_3_discrimination_2'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 4:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_4_discrimination_3'
            left_images = [f for f in os.listdir(image_folder) if
                           os.path.isfile(os.path.join(image_folder, f)) and
                           ('left' in f.lower() and 'both' in f.lower())]
        elif substage == 5:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_5_discrimination_4'
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
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_1_indication'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and 'right' in f.lower()]
        elif substage == 2:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_2_discrimination_1'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 3:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_3_discrimination_2'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 4:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_4_discrimination_3'
            right_images = [f for f in os.listdir(image_folder) if
                            os.path.isfile(os.path.join(image_folder, f)) and
                           ('right' in f.lower() and 'both' in f.lower())]
        elif substage == 5:
            image_folder = '/home/harsh/academy/stimuli/urn_training/0_extra_training/1_5_discrimination_4'
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
    global last_function_called

    cam2.put_state("Correct")
    cam3.put_state("Correct")

    substage = utils.task.substage
    if substage != 1:
        image_path_replaced = update_image_path_position(correct=True)
        if image_path_replaced:
            if last_function_called in LEFT_FUNCTIONS:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = settings.CENTRE_SCREEN
            elif last_function_called in RIGHT_FUNCTIONS:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = settings.CENTRE_SCREEN
            print(f"Correct image path: {image_path_replaced}")
        else:
            print("Warning: image_path is None or does not contain 'both'. No image will be updated.")


def loop55(timing):
    global last_function_called

    substage = utils.task.substage
    if substage != 1:
        if last_function_called in LEFT_FUNCTIONS:
            image_jar_left.draw()
        elif last_function_called in RIGHT_FUNCTIONS:
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


def function56():
    global last_function_called

    soundStream.play(soundVec3)
    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    substage = utils.task.substage
    if substage != 1:
        image_path_replaced = update_image_path_position(correct=False)
        if image_path_replaced:
            if last_function_called in LEFT_FUNCTIONS:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = settings.CENTRE_SCREEN
            elif last_function_called in RIGHT_FUNCTIONS:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = settings.CENTRE_SCREEN
            print(f"Incorrect image path: {image_path_replaced}")
        else:
            print("Warning: image_path is None or does not contain 'both'. No image will be updated.")


def loop56(timing):
    global last_function_called

    substage = utils.task.substage
    if substage != 1:
        if last_function_called in LEFT_FUNCTIONS:
            image_jar_left.draw()
        elif last_function_called in RIGHT_FUNCTIONS:
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


## FUNCTIONS FROM 60 TO 70 ARE FOR WEBER'S LAW TRAINING.
def function61():  # When the correct answer is on left
    global last_function_called, image_path
    last_function_called = 61

    image_path = utils.task.image_path_function

    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop61(timing):
    image_jar_left.draw()
    window.flip()


## FUNCTIONS FROM 60 TO 70 ARE FOR WEBER'S LAW TRAINING.
def function62():  # When the correct answer is on left
    global last_function_called, image_path
    last_function_called = 62

    image_path = utils.task.image_path_function

    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop62(timing):
    image_jar_right.draw()
    window.flip()


#Display camera correct, play correct sound and display correct stimuli FOR WEBER'S LAW TRAINING.
def function63():
    global last_function_called

    cam2.put_state("Correct")
    cam3.put_state("Correct")

    stage = utils.task.stage
    if stage != 1:
        image_path_replaced = update_image_path_size_position(correct=True)
        if image_path_replaced:
            if last_function_called in LEFT_FUNCTIONS:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = settings.CENTRE_SCREEN
            elif last_function_called in RIGHT_FUNCTIONS:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = settings.CENTRE_SCREEN
            print(f"Correct image path: {image_path_replaced}")
        else:
            print("Warning: image_path is None or could not be processed. No image will be updated.")


def loop63(timing):
    global last_function_called

    stage = utils.task.stage
    if stage != 1:
        if last_function_called in LEFT_FUNCTIONS:
            image_jar_left.draw()
        elif last_function_called in RIGHT_FUNCTIONS:
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


def function64():
    global last_function_called

    soundStream.play(soundVec3)
    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    stage = utils.task.stage
    if stage != 1:
        image_path_replaced = update_image_path_size_position(correct=False)
        if image_path_replaced:
            if last_function_called in LEFT_FUNCTIONS:
                image_jar_left.image = image_path_replaced
                image_jar_left.pos = settings.CENTRE_SCREEN
            elif last_function_called in RIGHT_FUNCTIONS:
                image_jar_right.image = image_path_replaced
                image_jar_right.pos = settings.CENTRE_SCREEN
            print(f"Incorrect image path: {image_path_replaced}")
        else:
            print("Warning: image_path is None or could not be processed. No image will be updated.")


def loop64(timing):
    global last_function_called

    stage = utils.task.stage
    if stage != 1:
        if last_function_called in LEFT_FUNCTIONS:
            image_jar_left.draw()
        elif last_function_called in RIGHT_FUNCTIONS:
            image_jar_right.draw()
        window.flip()
    else:
        window.flip()


## FUNCTIONS FROM 70 TO 80 ARE FOR TURTLE STYLE EXPERIMENT:
# def function71():  # When the correct stimuli is on left
#     global last_function_called, image_path
#     last_function_called = 71  # Track that function31 was called
#
#     substage = utils.task.substage
#     left_images = []
#     try:
#         # Get all the images based on the stages
#         if substage == 0:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/0_pre_training'
#             left_images = [f for f in os.listdir(image_folder) if
#                            os.path.isfile(os.path.join(image_folder, f)) and
#                            ('left' in f.lower() and 'both' in f.lower())]
#         elif substage == 1:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/1_training'
#             left_images = [f for f in os.listdir(image_folder) if
#                            os.path.isfile(os.path.join(image_folder, f)) and
#                            ('left' in f.lower() and 'both' in f.lower())]
#         elif substage == 2:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/2_training'
#             left_images = [f for f in os.listdir(image_folder) if
#                            os.path.isfile(os.path.join(image_folder, f)) and
#                            ('left' in f.lower() and 'both' in f.lower())]
#         elif substage == 3:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/3_training'
#             left_images = [f for f in os.listdir(image_folder) if
#                            os.path.isfile(os.path.join(image_folder, f)) and
#                            ('left' in f.lower() and 'both' in f.lower())]
#
#         if not left_images:
#             raise ValueError(f"No images found in {image_folder} for stage {stage}.")
#
#         # Choose a random image from the left_images list
#         random_image_path_left = os.path.join(image_folder, random.choice(left_images))
#
#         image_jar_left.image = random_image_path_left
#         image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
#
#         print('Stage: ', utils.task.stage)
#         print('Correct answer on left: ', random_image_path_left)
#
#         image_path = random_image_path_left     #Used in Function 35 or function 36 afterwards.
#
#     except Exception as e:
#         print(f"Error occurred: {e}")
#
# def loop71(timing):
#     image_jar_left.draw()
#     window.flip()
#
#
# # Functions for Probability Inference Tasks for different stages where the correct answer is right:
# def function72():  # When the correct stimuli is on right
#     global last_function_called, image_path
#     last_function_called = 72  # Track that function31 was called
#
#     substage = utils.task.substage
#     right_images = []
#     try:
#         # Get all the images based on the stages
#         if substage == 0:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/0_pre_training'
#             right_images = [f for f in os.listdir(image_folder) if
#                             os.path.isfile(os.path.join(image_folder, f)) and
#                            ('right' in f.lower() and 'both' in f.lower())]
#         elif substage == 1:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/1_training'
#             right_images = [f for f in os.listdir(image_folder) if
#                             os.path.isfile(os.path.join(image_folder, f)) and
#                            ('right' in f.lower() and 'both' in f.lower())]
#         elif substage == 2:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/2_training'
#             right_images = [f for f in os.listdir(image_folder) if
#                             os.path.isfile(os.path.join(image_folder, f)) and
#                            ('right' in f.lower() and 'both' in f.lower())]
#         elif substage == 3:
#             image_folder = '/home/harsh/academy/stimuli/turtle_style/6_turtle_style/3_training'
#             right_images = [f for f in os.listdir(image_folder) if
#                             os.path.isfile(os.path.join(image_folder, f)) and
#                            ('right' in f.lower() and 'both' in f.lower())]
#
#         if not right_images:
#             raise ValueError(f"No images found in {image_folder} for stage {stage}.")
#
#         # Choose a random image from the right_images list
#         random_image_path_right = os.path.join(image_folder, random.choice(right_images))
#
#         image_jar_right.image = random_image_path_right
#         image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
#
#         print('Stage:', utils.task.stage)
#         print('Correct answer on right:', random_image_path_right)
#
#         image_path = random_image_path_right     #Used in Function 35 or function 36 afterwards.
#
#     except Exception as e:
#         print(f"Error occurred: {e}")
#
#
# def loop72(timing):
#     image_jar_right.draw()
#     window.flip()


def function71():  # When the correct stimuli is on left
    global last_function_called, image_path
    last_function_called = 71  # Track that function31 was called

    image_path = utils.task.image_path_function

    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop71(timing):
    image_jar_left.draw()
    window.flip()


# Functions where the correct answer is right:
def function72():  # When the correct stimuli is on right
    global last_function_called, image_path
    last_function_called = 72  # Track that function31 was called

    image_path = utils.task.image_path_function

    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

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
        touch.start_reading_probability_correction(utils.task.response_duration, x_correct, None, y, width, height)
    else:
        x_incorrect = utils.task.x_incorrecth * settings.PIXELS_PER_MM
        touch.start_reading_probability_correction(utils.task.response_duration, x_correct, x_incorrect, y, width, height)

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
        touch.start_reading_probability_correction(utils.task.response_duration, x_correct, None, y, width, height)
    else:
        x_incorrect = utils.task.x_incorrecth * settings.PIXELS_PER_MM
        touch.start_reading_probability_correction(utils.task.response_duration, x_correct, x_incorrect, y, width, height)

    cam2.put_state("Resp Win")
    cam3.put_state("Resp Win")
    print('Resp Win 2')
    #print('x_correct in functions: ', x_correct)
    #print('x_incorrect in functions: ', x_incorrect)



## FUNCTIONS FROM 81 TO 86 ARE FOR WEBER'S LAW POST.
# Functions for Probability Inference Tasks for different stages where the correct answer is left:
def function81():  # When the correct answer is on left
    global last_function_called, image_path
    last_function_called = 81  # Track that function41 was called

    stage = utils.task.stage
    current_condition = utils.task.current_condition
    left_images = []
    try:
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law_post/{current_condition}'
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

def loop81(timing):
    image_jar_left.draw()
    window.flip()


# Functions for Probability Inference Tasks for different stages where the correct answer is right:
# Weber's law Post:
def function82():  # When the correct answer is on right
    global last_function_called, image_path
    last_function_called = 82  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    current_condition = utils.task.current_condition

    try:
        # Get all the images based on the stages
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law_post/{current_condition}'
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


def loop82(timing):
    image_jar_right.draw()
    window.flip()


#Function 83 to 86 are for conditions 1 and 2 for ror 1 in weber's law post 83 is for Left-Small, 84 for for Right-Small, 85 is for Left-Big, 86 for for Right-Big:
def function83():
    global last_function_called, image_path
    last_function_called = 83  # Track that function41 was called

    stage = utils.task.stage
    current_condition = utils.task.current_condition
    left_images = []
    try:
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law_post/{current_condition}'
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

def loop83(timing):
    image_jar_left.draw()
    window.flip()


def function84():
    global last_function_called, image_path
    last_function_called = 84  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    current_condition = utils.task.current_condition

    try:
        # Get all the images based on the stages
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law_post/{current_condition}'
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

def loop84(timing):
    image_jar_right.draw()
    window.flip()


def function85():
    global last_function_called, image_path
    last_function_called = 85  # Track that function41 was called

    stage = utils.task.stage
    current_condition = utils.task.current_condition
    left_images = []
    try:
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law_post/{current_condition}'
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

def loop85(timing):
    image_jar_left.draw()
    window.flip()


def function86():
    global last_function_called, image_path
    last_function_called = 86  # Track that function31 was called

    stage = utils.task.stage
    right_images = []
    current_condition = utils.task.current_condition

    try:
        # Get all the images based on the stages
        image_folder = f'/home/harsh/academy/stimuli/webers_law/4_webers_law_post/{current_condition}'
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

def loop86(timing):
    image_jar_right.draw()
    window.flip()



# Functions for Probability Inference Tasks for different stages where the correct answer is left, for new discrimination
#101 to 104 without spacers:
def function101():  # When the correct stimuli is on left and small
    global last_function_called, image_path
    last_function_called = 101  # Track that function101 was called
    image_path = utils.task.image_path_function
    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop101(timing):
    image_jar_left.draw()
    window.flip()

def function102():  # When the correct stimuli is on right and small
    global last_function_called, image_path
    last_function_called = 102  # Track that function102 was called
    image_path = utils.task.image_path_function
    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop102(timing):
    image_jar_right.draw()
    window.flip()

def function103():  # When the correct stimuli is on left and big
    global last_function_called, image_path
    last_function_called = 103  # Track that function103 was called
    image_path = utils.task.image_path_function
    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop103(timing):
    image_jar_left.draw()
    window.flip()

def function104():  # When the correct stimuli is on right and big
    global last_function_called, image_path
    last_function_called = 104  # Track that function104 was called
    image_path = utils.task.image_path_function
    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop104(timing):
    image_jar_right.draw()
    window.flip()

#105 to 108 are for
def function105():  # When the correct stimuli is on left, small, with spacer
    global last_function_called, image_path
    last_function_called = 105
    image_path = utils.task.image_path_function
    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop105(timing):
    image_jar_left.draw()
    window.flip()

def function106():  # When the correct stimuli is on right, small, with spacer
    global last_function_called, image_path
    last_function_called = 106
    image_path = utils.task.image_path_function
    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop106(timing):
    image_jar_right.draw()
    window.flip()

def function107():  # When the correct stimuli is on left, big, with spacer
    global last_function_called, image_path
    last_function_called = 107
    image_path = utils.task.image_path_function
    image_jar_left.image = image_path
    image_jar_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop107(timing):
    image_jar_left.draw()
    window.flip()

def function108():  # When the correct stimuli is on right, big, with spacer
    global last_function_called, image_path
    last_function_called = 108
    image_path = utils.task.image_path_function
    image_jar_right.image = image_path
    image_jar_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])

def loop108(timing):
    image_jar_right.draw()
    window.flip()


#Functions from 110 onwards are for Bastos and Taylor:
# Function 111: Correct answer on left:
# Function 111: Display the first frame of Left Video (without playing)
def function111():
    global last_function_called
    last_function_called = 111

    video_left.setMovie(utils.task.video_path_function)
    video_left.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
    video_left.seek(0)  # Show the first frame only
    print(f"Assigned left video: {utils.task.video_path_function}")

def loop111(timing):
    video_left.draw()  # Show the first frame
    window.flip()


# Function 112: Display the first frame of Right Video (without playing)
def function112():
    global last_function_called
    last_function_called = 112

    video_right.setMovie(utils.task.video_path_function)
    video_right.pos = (settings.CENTRE_SCREEN[0], settings.CENTRE_SCREEN[1])
    video_right.seek(0)  # Show the first frame only
    print(f"Assigned right video: {utils.task.video_path_function}")

def loop112(timing):
    video_right.draw()  # Show the first frame
    window.flip()

#Correct:
def function113():
    global last_function_called

    cam2.put_state("Correct")
    cam3.put_state("Correct")

    stage = utils.task.stage
    # if stage != 1:
    #     image_path_replaced = update_image_path_size_position(correct=True)
    #     if image_path_replaced:
    #         if last_function_called in LEFT_FUNCTIONS:
    #             image_jar_left.image = image_path_replaced
    #             image_jar_left.pos = settings.CENTRE_SCREEN
    #         elif last_function_called in RIGHT_FUNCTIONS:
    #             image_jar_right.image = image_path_replaced
    #             image_jar_right.pos = settings.CENTRE_SCREEN
    #         print(f"Correct image path: {image_path_replaced}")
    #     else:
    #         print("Warning: image_path is None or could not be processed. No image will be updated.")


def loop113(timing):
    global last_function_called

    stage = utils.task.stage
    # if stage != 1:
    #     if last_function_called in LEFT_FUNCTIONS:
    #         image_jar_left.draw()
    #     elif last_function_called in RIGHT_FUNCTIONS:
    #         image_jar_right.draw()
    #     window.flip()
    # else:
    #     window.flip()

#Punish:
def function114():
    global last_function_called

    soundStream.play(soundVec3)
    cam2.put_state("Punish")
    cam3.put_state("Punish")
    print("Punish, Punish Sound played")

    stage = utils.task.stage
    # if stage != 1:
    #     image_path_replaced = update_image_path_size_position(correct=False)
    #     if image_path_replaced:
    #         if last_function_called in LEFT_FUNCTIONS:
    #             image_jar_left.image = image_path_replaced
    #             image_jar_left.pos = settings.CENTRE_SCREEN
    #         elif last_function_called in RIGHT_FUNCTIONS:
    #             image_jar_right.image = image_path_replaced
    #             image_jar_right.pos = settings.CENTRE_SCREEN
    #         print(f"Incorrect image path: {image_path_replaced}")
    #     else:
    #         print("Warning: image_path is None or could not be processed. No image will be updated.")


def loop114(timing):
    global last_function_called

    stage = utils.task.stage
    # if stage != 1:
    #     if last_function_called in LEFT_FUNCTIONS:
    #         image_jar_left.draw()
    #     elif last_function_called in RIGHT_FUNCTIONS:
    #         image_jar_right.draw()
    #     window.flip()
    # else:
    #     window.flip()


# Function 115: Play the Left Video from 5 Seconds
def function115():
    global last_function_called
    last_function_called = 115

    video_left.setMovie(utils.task.video_path_function)
    start_time = 0.0  # Start video from 0 seconds
    video_left.seek(start_time)  # Seek to the specific time before playing
    print(f"Playing left video from {start_time:.2f} seconds...")

    while video_left.status != visual.FINISHED:
        video_left.draw()
        window.flip()


def loop115(timing):
    if video_left.status != visual.FINISHED:
        video_left.draw()
    window.flip()


# Function 116: Play the Right Video from 6.5 Seconds
def function116():
    global last_function_called
    last_function_called = 116

    start_time = 0.0  # Start video from 0 seconds
    video_right.setMovie(utils.task.video_path_function)
    video_right.seek(start_time)  # Seek to the specific time before playing
    print(f"Playing right video from {start_time:.2f} seconds...")

    while video_right.status != visual.FINISHED:
        video_right.draw()
        window.flip()


def loop116(timing):
    if video_right.status != visual.FINISHED:
        video_right.draw()
    window.flip()
