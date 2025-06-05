import os
import sys
import time
import psutil
from academy.gui import gui
from academy import arg, bpod, queues, telegram_bot, aws, time_utils
from academy.utils import utils
from academy.task_collection import task_collection
from academy.arduino import arduino
from academy.touch import touch
from academy.screen import screen
from academy.task_manager import TaskManager
from academy.softcode import softcode
from academy.camera import cam1, cam2, cam3
from user import settings
import ast


# 0 waiting
# 1 before first action
# 2 before min_time
# 3 after min_time, data not saved, animal not back
# 4 after min_time, data not saved, animal back
# 5 after max_time, data not saved, animal not back
# 6 after max_time, data saved, animal not back
# 7 setting task
# 8 running direct task
# 9 after max time, data not saved, direct task
# 10 multiple animals inside, data not saved, animal not back


def main():
    os.system("alsactl --file ~/.config/asound.state restore")
    gui.reload()
    try:
        if not cam1.connected:
            utils.log("Academy", "Cam1 not found", "ERROR")
            if not settings.TESTING:
                exit_app()

        # if not cam2.connected:
        #     utils.log('Academy', 'Cam2 not found', 'ERROR')
        #     if not settings.TESTING:
        #         exit_app()
        #
        # if not cam3.connected:
        #     utils.log('Academy', 'Cam3 not found', 'ERROR')
        #     if not settings.TESTING:
        #         exit_app()

        if not arduino.connected:
            utils.log("Academy", "Arduino not found", "ERROR")
            if not settings.TESTING:
                exit_app()

        if not touch.connected:
            utils.log("Academy", "Touch device not found", "ERROR")
            if not settings.TESTING:
                exit_app()

        if not task_collection.tasks:
            utils.log("Academy", "Tasks not found at directory tasks/", "ERROR")
            if not settings.TESTING:
                exit_app()

        utils.log("Academy", "Stablishing connection with Bpod...", "ACTION")
        if bpod.testing_connection():
            utils.log_cam("Academy", "Connection with Bpod stablished", "START")
        else:
            utils.log_cam("Academy", "Connection to Bpod failed", "ERROR")
            if not settings.TESTING:
                exit_app()

        if arg.tag:  # here we can add options to launch
            try:
                if arg.tag[0] in [0, 1, 2, 3]:
                    utils.reading_tags = arg.tag[0]
                    gui.change_reading_tags()
            except:
                pass

        arduino.turn_led_off()

        if arg.inside:
            arduino.open_door2()
            # bpod.open_inner_door()
            utils.state = 6

        gui.update_canvas()

        main_loop()

    except KeyboardInterrupt:
        exit_app()


def main_loop():
    weight = []
    last_time_tag = 0
    last_tags = []
    last_time_tags = []
    last_time_scale = 0
    new_time_scale = 0
    enter_flag = False

    while True:

        if utils.force_relaunch:
            utils.force_relaunch = False

            if utils.state in [0, 1, 2, 3, 4, 5, 6]:
                utils.relaunch = True
                utils.state_after_relaunch = utils.state
                if utils.state in [1, 2, 3, 4, 5]:
                    try:
                        stop_and_save_task()
                    except:
                        pass
                utils.change_to_state = 0

        if utils.change_to_state != utils.state:
            utils.change_gui = True
            if utils.state == 7 or utils.change_to_state == 7:
                utils.change_gui7 = True
            utils.old_state = utils.state
            go_to_state(utils.change_to_state)
            utils.state = utils.change_to_state

        gui.reload()

        # if utils.chrono.get_seconds() >= settings.MAXIMUM_TIME + utils.alarm_mouse_time:
        #     telegram_bot.alarm_session_time(settings.MAXIMUM_TIME + utils.alarm_mouse_time)
        #     utils.alarm_mouse_time += 3600

        try:
            status, tag = queues.tags.get_nowait()
        except:
            status, tag = None, None

        if status == "a":
            button_actions(tag)

        if status == "t":
            temperature = tag
            utils.log("Academy", "Temperature: " + str(temperature), "ACTION")
            try:
                if temperature > settings.MAXIMUM_TEMPERATURE:
                    utils.telegram.alarm_temperature(temperature)
            except:
                pass

        elif status == "p":
            new_time_scale = time_utils.now_seconds()
            weight.append((new_time_scale, float(tag)))
            weight = [value for value in weight if value[0] + 3 >= new_time_scale]
            utils.log("Academy", "weight: " + tag, "ACTION")

        # day/night light
        begin_time = time_utils.hour_minute_to_time(
            settings.HOUR_DAY, settings.MINUTE_DAY
        )
        end_time = time_utils.hour_minute_to_time(
            settings.HOUR_NIGHT, settings.MINUTE_NIGHT
        )
        now = time_utils.now_time()
        if begin_time < end_time:
            day = begin_time <= now <= end_time
        else:  # crosses midnight
            day = now >= begin_time or now <= end_time

        if day and not utils.day:
            arduino.turn_led_off()
            utils.day = True
        elif not day and utils.day:
            arduino.turn_led_on()
            utils.day = False

        if utils.state == 0:  # waiting
            if utils.relaunch:
                relaunch()

            if status == "s":
                try:
                    utils.super_subject = task_collection.subjects_dict[tag]
                    utils.subject = utils.super_subject.subject
                    last_time_tag = time_utils.now_seconds()

                    last_tags += [tag]
                    last_time_tags += [last_time_tag]
                    enter_flag = False  #

                    indices = []
                    for index, t in enumerate(last_time_tags):
                        if last_time_tag < t + settings.DURATION_TAGS:
                            indices += [index]

                    last_tags = [last_tags[i] for i in indices]
                    last_time_tags = [last_time_tags[i] for i in indices]

                    enter_flag = subject_action(first_time=True, last_tags=last_tags)
                except:
                    utils.log_cam(
                        "Academy", "Subject not found for tag: " + tag, "ERROR"
                    )

            elif status is None:
                if (
                    enter_flag
                    and time_utils.now_seconds() < last_time_tag + settings.DURATION_TAG
                ):
                    enter_flag = subject_action(first_time=False, last_tags=last_tags)
                elif enter_flag:
                    enter_flag = False
                    real_subject_action()

        elif utils.state == 1:  # 1 before first action
            if status == "s":
                utils.log_cam(
                    utils.subject.name,
                    "Not allowed to exit, task has not started yet",
                    "ACTION",
                )

            screen_loop()

        elif utils.state == 2:  # 2 before min_time

            doors1 = cam1.area_doors1.value
            total = cam1.area_total.value

            if utils.subject_trapped:
                if total < min(settings.NOMICECAGE, settings.NOMICEDOOR1):
                    arduino.close_door1()
                    utils.subject_trapped = False

            elif (
                time_utils.now_seconds() > utils.alarm_trapped_time + 10
                and doors1 > settings.NOMICEDOOR1
            ):
                utils.alarm_trapped_repetition += 1
                utils.alarm_trapped_time = time.time()
                if utils.alarm_trapped_repetition > 3:
                    utils.alarm_trapped_repetition = 0
                    utils.alarm_trapped_time = time.time() + 600
                    telegram_bot.alarm_subject_trapped()
                    utils.subject_trapped = True
                    arduino.open_door1()

            screen_loop()

        elif utils.state == 3:  # 3 after min_time, data not saved, animal not back
            if settings.ENABLE_EXIT_WEIGHING and status == "w":
                try:
                    new_time = time_utils.now_seconds()
                    weight.append((new_time, float(tag)))
                    weight = [value for value in weight if value[0] + 3 >= new_time]
                    list_weights = ",".join([str(item[1]) for item in weight])
                    if (len(weight) == 5
                            and cam1.area_doors2.value < settings.NOMICEDOOR2
                            and cam1.area_doors1.value > settings.NOMICEDOOR2):
                        good_weight = weight[2][1]
                        utils.task.subject_weight = good_weight
                        utils.log(utils.subject.name, "weight: " + str(good_weight), "ACTION")
                        utils.log(utils.subject.name, "list_of_weights: " + list_weights, "ACTION",)
                        weight = []
                        utils.change_to_state = (4)
                except:  # because an animal can be stuck and then we have measures of weight and rfid at the same time
                    pass
            else:
                utils.task.subject_weight = 0
                if (cam1.area_doors2.value < settings.NOMICEDOOR2
                        and cam1.area_doors1.value > settings.NOMICEDOOR2):
                    utils.change_to_state = (4)

            screen_loop()

        elif utils.state == 4:  # 4 after min_time, data not saved, animal back
            stop_and_save_task()
            utils.change_to_state = 0

        elif utils.state == 5:  # 5 after max_time, data not saved, animal not back
            stop_and_save_task()
            utils.change_to_state = 6

        elif utils.state == 6:  # 6 after max_time, data saved, animal not back

            if (
                utils.chrono.get_seconds()
                >= utils.task_real_duration + utils.alarm_mouse_time
            ):
                bpod.play_buzzer1()
                bpod.play_buzzer2()
                arduino.noise_door2()
                bpod.play_buzzer1()
                bpod.play_buzzer2()
                arduino.noise_door2()
                utils.alarm_mouse_time += 900

            if (
                utils.chrono.get_seconds()
                >= utils.task_real_duration + utils.alarm_mouse_time2
            ):
                try:
                    telegram_bot.alarm_session_time(
                        utils.task_real_duration + utils.alarm_mouse_time2,
                        utils.subject.name,
                    )
                except:
                    telegram_bot.alarm_session_time(
                        utils.task_real_duration + utils.alarm_mouse_time2, ""
                    )
                utils.alarm_mouse_time2 += 3600

            if (
                time_utils.now_seconds() > last_time_scale + 600
                and cam1.area_doors1.value < settings.NOMICEDOOR1
                and cam1.area_total.value < settings.NOMICEDOOR1
            ):
                last_time_scale = time_utils.now_seconds()
                arduino.tare_scale()

            if settings.ENABLE_EXIT_WEIGHING and status == "w":
                new_time = time_utils.now_seconds()
                weight.append((new_time, float(tag)))
                weight = [value for value in weight if value[0] + 3 >= new_time]
                list_weights = ",".join([str(item[1]) for item in weight])
                if (len(weight) == 5 and cam1.area_doors2.value < settings.NOMICEDOOR2
                        and cam1.area_doors1.value > settings.NOMICEDOOR2):
                    try:
                        good_weight = weight[2][1]
                        utils.task.subject_weight = good_weight
                        utils.log(utils.subject.name, "weight: " + str(good_weight), "ACTION")
                        utils.log(utils.subject.name,"list_of_weights: " + list_weights,"ACTION")
                        weight = []
                        utils.log_cam(utils.subject.name, "Returning home", "ACTION")
                    except:
                        utils.log("Academy", "returning home after relaunch", "ACTION")
                    arduino.move_doors_to_go_home()
                    utils.change_to_state = 0  # waiting
            else:
                utils.task.subject_weight = 0
                if (cam1.area_doors2.value < settings.NOMICEDOOR2
                        and cam1.area_doors1.value > settings.NOMICEDOOR2):
                    try:
                        utils.log_cam(utils.subject.name, "Returning home", "ACTION")
                    except:
                        utils.log("Academy", "returning home after relaunch", "ACTION")
                    arduino.move_doors_to_go_home()
                    utils.change_to_state = 0  # waiting

        elif utils.state == 7:  # 7 setting task
            pass

        elif utils.state == 8:  # 8 running direct task
            screen_loop()

        elif utils.state == 9:  # after max time, data not saved, direct task
            stop_and_save_task()
            utils.change_to_state = 7

        elif (
            utils.state == 10
        ):  # multiple animals inside, data not saved, animal not back
            stop_and_save_task()
            utils.reading_tags = 0
            gui.change_reading_tags()
            # bpod.open_inner_door()
            utils.change_to_state = 0


def stop_and_save_task():
    softcode.kill()
    screen.win.flip()
    screen.tag = None
    screen.first = False
    screen.my_loop = lambda *args, **kwargs: None

    utils.task.p.join()
    try:
        utils.task.my_bpod.close()
    except AttributeError:
        pass
    utils.task.my_bpod = None

    if utils.task_manager is not None:
        try:
            utils.task_manager.save_csvs(weight=utils.task.subject_weight)
        except Exception as e:
            print(f"No data to save, session stopped. Error: {e}")

    if utils.subject is None:
        name = "None"
    else:
        name = utils.subject.name

    name_task = (
        utils.task.task
        + "-"
        + str(int(float(utils.task.stage)))
        + "-"
        + str(int(float(utils.task.substage)))
    )
    utils.log_cam(name, name_task, "END")
    #aws.send_timing2()


def button_actions(tag):
    if tag == "EXIT_ACADEMY":
        if utils.state == 0:
            exit_app()
        else:
            utils.log_cam(
                "Academy",
                "There is a subject inside the box, wait until it leaves to exit academy",
                "ERROR",
            )

    elif tag == "EXIT_TASK":
        stop_and_save_task()
        utils.change_to_state = 0


def screen_loop():
    try:
        trials_performed = queues.trials.get_nowait()
        if len(utils.list_of_trial_timings) < trials_performed:
            utils.list_of_trial_timings.append(utils.chrono.get_seconds())
    except:
        trials_performed = 0

    if (
        trials_performed >= utils.task.trials_max
        or utils.chrono.get_seconds() >= utils.task.duration_max
    ):
        if utils.state == 8:
            utils.change_to_state = 9  # after max time, data not saved, direct task
        else:
            utils.change_to_state = 5  # after max_time, data not saved, animal not back

    if utils.state == 2 or utils.state == 1:

        seconds = utils.chrono.get_seconds()
        last_trials = [
            item for item in utils.list_of_trial_timings if item > seconds - 600
        ]

        if (
            seconds > utils.task.duration_tired
            and len(last_trials) < utils.task.trials_tired
        ) or utils.task.tired:
            utils.change_to_state = (
                3  # 3 after min_time, data not saved, animal not back
            )
        if (
            seconds > utils.task.duration_min
            and trials_performed >= utils.task.trials_min
        ):
            utils.change_to_state = (
                3  # 3 after min_time, data not saved, animal not back
            )

    if cam2.tracking_inside:
        if (
            time_utils.now_seconds() > utils.alarm_mice_time + 10
            and cam2.area_total.value > settings.SEVERALMICE
            and utils.state != 8
        ):
            utils.alarm_mice_repetition += 1
            utils.alarm_mice_time = time.time()
            if utils.alarm_mice_repetition > 3:
                utils.alarm_mice_repetition = 0
                utils.alarm_mice_time = time.time() + 3600
                # utils.change_to_state = 10
                telegram_bot.alarm_mice(cam2.area_total.value)

    if cam3.tracking_inside:
        if (
            time_utils.now_seconds() > utils.alarm_mice_time + 10
            and cam3.area_total.value > settings.SEVERALMICE
            and utils.state != 8
        ):
            utils.alarm_mice_repetition += 1
            utils.alarm_mice_time = time.time()
            if utils.alarm_mice_repetition > 3:
                utils.alarm_mice_repetition = 0
                utils.alarm_mice_time = time.time() + 3600
                # utils.change_to_state = 10
                telegram_bot.alarm_mice(cam3.area_total.value)

        if settings.CAM3_FLOOR_ON:
            if (
                time_utils.now_seconds() > utils.alarm_mice_time + 10
                and cam3.area_total_floor.value > settings.FLOORMOUSE
                and utils.state != 8
            ):
                utils.alarm_mice_repetition += 1
                utils.alarm_mice_time = time.time()
                if utils.alarm_mice_repetition > 3:
                    utils.alarm_mice_repetition = 0
                    utils.alarm_mice_time = time.time() + 600
                    try:
                        telegram_bot.alarm_mice_floor(utils.subject.name)
                    except:
                        telegram_bot.alarm_mice_floor("")
    try:
        screen.tag = queues.softcodes.get_nowait()
        screen.first = True
    except:
        pass

    screen.play()


def subject_action(first_time, last_tags):
    #print('Subject threshold countdown')
    cage = (cam1.area_cage1.value + cam1.area_cage2.value)
    doors1 = cam1.area_doors1.value
    total = cam1.area_total.value
    enter_flag = False

    if cage > settings.NOMICECAGE:
        if first_time:
            utils.log_cam(
                utils.subject.name, "Movement in the cage area " + str(cage), "ACTION"
            )
    elif doors1 > settings.NOMICEDOOR1:
        if first_time:
            utils.log_cam(
                utils.subject.name,
                "Movement in the doors1 area " + str(doors1),
                "ACTION",
            )
    elif total > settings.ONEMOUSE:
        if first_time:
            utils.log_cam(
                utils.subject.name, "Movement in the door2 area " + str(total), "ACTION"
            )
    elif len(set(last_tags)) > 1:
        if first_time:
            utils.log_cam(
                utils.subject.name,
                "Other subjects detected in the last seconds",
                "ACTION",
            )
    else:
        if (
            time_utils.now_datetime() > utils.super_subject.min_time
            or utils.super_subject.all_in
        ):
            if utils.super_subject.task is None:
                utils.log_cam(
                    "Academy",
                    "task: "
                    + utils.subject.task
                    + "not found for subject: "
                    + utils.subject.name,
                    "ERROR",
                )
            else:
                enter_flag = True
        else:
            if first_time:
                utils.log_cam(
                    utils.subject.name,
                    "Not allowed to enter until: "
                    + time_utils.datetime_to_string(utils.super_subject.min_time),
                    "ACTION",
                )
    return enter_flag


def real_subject_action():
    print('Subject allowed to enter')
    total = cam1.area_total.value
    if total < settings.ONEMOUSE:
        utils.log_cam(utils.subject.name, "Area is correct " + str(total), "ACTION")
        utils.change_to_state = 1  # before first action


def go_to_state(num):

    if num == 0:  # waiting
        utils.subject_trapped = False
        utils.alarm_mouse_time = 1000000000
        utils.alarm_mouse_time2 = 1000000000
        utils.alarm_mice_repetition = 0
        utils.alarm_trapped_repetition = 0
        utils.list_of_trial_timings = []
        task_collection.subjects_dict = task_collection.create_subjects_dict()
        cam2.put_state('inactive')
        cam3.put_state("inactive")
        cam2.put_state('black')
        cam3.put_state("black")
        if utils.reading_tags > 0:
            arduino.turn_led_on()
        utils.log("Academy", "Go to state 0", "ACTION")
        screen.tag = None
        screen.first = False
        screen.my_loop = lambda *args, **kwargs: None

    elif num == 1:  # before first action
        utils.alarm_mouse_time = 60
        utils.alarm_mouse_time2 = 3600
        utils.task_real_duration = 0
        arduino.close_door1()
        arduino.open_door2()
        arduino.turn_led_off()
        # bpod.close_inner_door()
        utils.task = utils.super_subject.task
        utils.task.init_variables()

        utils.subject.stage = float(utils.subject.stage)
        utils.subject.substage = float(utils.subject.substage)
        utils.subject.substage_bias = float(utils.subject.substage_bias)
        utils.subject.stim_dur_ds = float(utils.subject.stim_dur_ds)
        utils.subject.stim_dur_dm = float(utils.subject.stim_dur_dm)
        utils.subject.stim_dur_dl = float(utils.subject.stim_dur_dl)
        #PI variables:
        utils.subject.moved_back_counter = float(utils.subject.moved_back_counter)
        utils.subject.block = int(utils.subject.block)  # Cast to int

        if isinstance(utils.subject.conditions, str):
            utils.subject.conditions = ast.literal_eval(utils.subject.conditions)
        utils.subject.conditions = list(map(int, utils.subject.conditions))

        if isinstance(utils.subject.completed_conditions, str):
            utils.subject.completed_conditions = ast.literal_eval(utils.subject.completed_conditions)
        utils.subject.completed_conditions = list(map(int, utils.subject.completed_conditions))

        utils.subject.current_condition = int(utils.subject.current_condition)  # Cast to int
        utils.subject.repetition = int(utils.subject.repetition)  # Cast to int
        utils.subject.current_repetition = int(utils.subject.current_repetition)  # Cast to int
        utils.subject.trial_counter = int(utils.subject.trial_counter)  # Cast to int
        utils.subject.stim_trial = int(utils.subject.stim_trial)  # Cast to int.

        if isinstance(utils.subject.stim_trials, str):
            utils.subject.stim_trials = ast.literal_eval(utils.subject.stim_trials)
        utils.subject.stim_trials = list(map(int, utils.subject.stim_trials))

        utils.subject.stim_trial_counter = int(utils.subject.stim_trial_counter)  # Cast to int

        if isinstance(utils.subject.ror, str):
            utils.subject.ror = ast.literal_eval(utils.subject.ror)
        utils.subject.ror = list(map(float, utils.subject.ror))

        if isinstance(utils.subject.completed_ror, str):
            utils.subject.completed_ror = ast.literal_eval(utils.subject.completed_ror)
        utils.subject.completed_ror = list(map(float, utils.subject.completed_ror))

        utils.subject.current_ror = float(utils.subject.current_ror)  # Cast to float
        utils.subject.trial_counter_ror = int(utils.subject.trial_counter_ror)  # Cast to int
        utils.subject.block_size = int(utils.subject.block_size)  # Cast to int
        utils.subject.block_trial_counter = int(utils.subject.block_trial_counter)  # Cast to int
        utils.subject.block_accuracy = float(utils.subject.block_accuracy)  # Cast to float
        utils.subject.block_number = int(utils.subject.block_number)  # Cast to int
        utils.subject.ror_change = int(utils.subject.ror_change)  #Cast to Boolean
        utils.subject.block_change = int(utils.subject.block_change)  #Cast to Boolean
        utils.subject.last_stim_trial = int(utils.subject.last_stim_trial)  #Cast to int
        utils.subject.last_condition_trial = int(utils.subject.last_condition_trial)  #Cast to int
        utils.subject.total_trials = int(utils.subject.total_trials)  #Cast to int
        utils.subject.block_correct_count = int(utils.subject.block_correct_count)  #Cast to int
        utils.subject.block_valid_count = int(utils.subject.block_valid_count)  #Cast to int
        utils.subject.condition_trial_counter = int(utils.subject.condition_trial_counter)  #Cast to int
        utils.subject.stage_forward_change = int(utils.subject.stage_forward_change)  #Cast to int
        utils.subject.stage_backward_change = int(utils.subject.stage_backward_change)  #Cast to int
        utils.subject.task_number = int(utils.subject.task_number)  #Cast to int
        utils.subject.last_forward_stage = int(utils.subject.last_forward_stage)  #Cast to int
        utils.subject.last_backward_stage = int(utils.subject.last_backward_stage)  #Cast to int
        utils.subject.reward_frequency = float(utils.subject.reward_frequency)  #Cast to float
        utils.subject.reward_db = float(utils.subject.reward_db)  #Cast to float
        utils.subject.reward_duration = float(utils.subject.reward_duration)  #Cast to float



        #From subject to task:
        utils.task.stage = utils.subject.stage
        utils.task.substage = utils.subject.substage
        utils.task.substage_bias = utils.subject.substage_bias
        utils.task.stim_dur_ds = utils.subject.stim_dur_ds
        utils.task.stim_dur_dm = utils.subject.stim_dur_dm
        utils.task.stim_dur_dl = utils.subject.stim_dur_dl
        utils.task.choice = utils.subject.choice
        #PI variables:
        utils.task.moved_back_counter = utils.subject.moved_back_counter
        utils.task.block = utils.subject.block
        utils.task.conditions = utils.subject.conditions
        utils.task.completed_conditions = utils.subject.completed_conditions
        utils.task.current_condition = utils.subject.current_condition
        utils.task.repetition = utils.subject.repetition
        utils.task.current_repetition = utils.subject.current_repetition
        utils.task.trial_counter = utils.subject.trial_counter
        utils.task.stim_trial = utils.subject.stim_trial
        utils.task.stim_trials = utils.subject.stim_trials
        utils.task.stim_trial_counter = utils.subject.stim_trial_counter
        utils.task.ror = utils.subject.ror
        utils.task.completed_ror = utils.subject.completed_ror
        utils.task.current_ror = utils.subject.current_ror
        utils.task.trial_counter_ror = utils.subject.trial_counter_ror
        utils.task.block_size = utils.subject.block_size
        utils.task.block_trial_counter = utils.subject.block_trial_counter
        utils.task.block_accuracy = utils.subject.block_accuracy
        utils.task.block_number = utils.subject.block_number
        utils.task.ror_change = utils.subject.ror_change
        utils.task.block_change = utils.subject.block_change
        utils.task.last_stim_trial = utils.subject.last_stim_trial
        utils.task.last_condition_trial = utils.subject.last_condition_trial
        utils.task.total_trials = utils.subject.total_trials
        utils.task.block_correct_count = utils.subject.block_correct_count
        utils.task.block_valid_count = utils.subject.block_valid_count
        utils.task.condition_trial_counter = utils.subject.condition_trial_counter
        utils.task.stage_forward_change = utils.subject.stage_forward_change
        utils.task.stage_backward_change = utils.subject.stage_backward_change
        utils.task.task_number = utils.subject.task_number
        utils.task.last_forward_stage = utils.subject.last_forward_stage
        utils.task.last_backward_stage = utils.subject.last_backward_stage
        utils.task.reward_frequency = utils.subject.reward_frequency
        utils.task.reward_db = utils.subject.reward_db
        utils.task.reward_duration = utils.subject.reward_duration

        utils.task_manager = TaskManager(utils.subject)
        utils.gui_name = utils.subject.name + " - " + utils.task.task
        utils.log("Academy", "Go to state 1", "ACTION")
        name_task = (
            utils.task.task
            + "-"
            + str(int(float(utils.task.stage)))
            + "-"
            + str(int(float(utils.task.substage)))
        )
        utils.log_cam(utils.subject.name, name_task, "START")
        utils.task.set_and_run(
            utils.subject, utils.subject.name, utils.subject.weight, utils.task_manager
        )

    elif num == 2:  # before min_time
        utils.subject_trapped = False
        arduino.close_door2()
        utils.log_cam(
            utils.subject.name, "First action in box, closing door 2", "ACTION"
        )
        utils.log("Academy", "Go to state 2", "ACTION")

    elif num == 3:  # after min_time, data not saved, animal not back
        arduino.temp_and_scale()
        time.sleep(1)
        if utils.subject_trapped:
            # this should never happen
            telegram_bot.alarm_subject_trapped()
            utils.subject_trapped = False
            arduino.close_door1()
        arduino.open_door2()
        utils.log_cam(utils.subject.name, "Opening door2, subject can leave", "ACTION")
        utils.log("Academy", "Go to state 3", "ACTION")

    elif num == 4:  # after min_time, data not saved, animal back
        arduino.move_doors_to_go_home()
        utils.log_cam(utils.subject.name, "Returning home", "ACTION")
        utils.log("Academy", "Go to state 4", "ACTION")

    elif num == 5:  # after max_time, data not saved, animal not back
        arduino.open_door2()
        utils.log("Academy", "Go to state 5", "ACTION")

    elif num == 6:  # after max_time, data saved, animal not back
        # bpod.open_inner_door()
        # bpod.play_buzzer2()
        utils.task_real_duration = utils.chrono.get_seconds()
        utils.log("Academy", "Go to state 6", "ACTION")

    elif num == 7:  # setting task
        cam2.put_state('inactive')
        cam3.put_state("inactive")
        cam2.put_state('black')
        cam3.put_state("black")
        arduino.turn_led_off()
        utils.log("Academy", "Go to state 7", "ACTION")
        screen.tag = None
        screen.first = False
        screen.my_loop = lambda *args, **kwargs: None

    elif num == 8:  # running direct task

        if gui.subject is None:
            subject_name = "None"
            utils.task_manager = None
        else:
            subject_name = gui.subject.name
            gui.subject.task = utils.task.task
            gui.subject.stage = utils.task.stage
            gui.subject.substage = utils.task.substage
            utils.task_manager = TaskManager(gui.subject)

        utils.log_cam(subject_name, utils.task.task, "START")
        gui.name = subject_name + " - " + utils.task.task
        utils.task.set_and_run(
            gui.subject, subject_name, utils.task.subject_weight, utils.task_manager
        )

    elif num == 10:  # multiple animals inside
        # bpod.open_inner_door()
        utils.log("Academy", "Go to state 10", "ACTION")


def exit_app():
    utils.log("Academy", "EXIT", "END")
    time.sleep(1)
    arduino.turn_led_off()
    cam1.put_state("inactive")
    cam2.put_state("inactive")
    cam3.put_state("inactive")
    for i in range(500):
        gui.reload()
    cam1.stop()
    cam2.stop()
    cam3.stop()
    f = open(os.devnull, "w")
    sys.stdout = f
    sys.stderr = f
    sys.tracebacklimit = 0
    try:
        for attrib in dir(globals):
            delattr(globals, attrib)
    except AttributeError:
        pass
    sys.exit(0)


def relaunch():

    num = str(utils.reading_tags)

    time.sleep(1)
    cam1.put_state("inactive")
    cam2.put_state("inactive")
    cam3.put_state("inactive")
    for i in range(500):
        gui.reload()
    cam1.stop()
    cam2.stop()
    cam3.stop()

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except:
        pass

    python = sys.executable

    if utils.state_after_relaunch in [1, 2, 3, 4, 5, 6]:
        os.execl(python, python, sys.argv[0], "-i", num)
    else:
        os.execl(python, python, sys.argv[0], num)


if __name__ == "__main__":
    main()
