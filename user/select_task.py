import numpy as np
from wx.lib.pubsub.py2and3 import print_
from academy import telegram_bot
from user import settings
import random
import json
import pandas as pd
from types import SimpleNamespace


# Examples of functions to calculate new task and stage
# If the function fails to return, new task and stage will be previous task and previous stage
# df is the session dataframe for the subject


def select_task(df, subject):
    task = subject.task
    wait_seconds = 3600 * settings.TIME_TO_ENTER
    last_row = df.iloc[-1]  # Get the last row of the DataFrame
    my_subject = df.subject.iloc[0]

    # def get_val_from_df_or_default(column_name, default_val):
    #     if column_name in df.columns:
    #         val = last_row[column_name]
    #         if pd.isna(val):
    #             return default_val
    #         return val
    #     return default_val
    #
    #
    # stage = get_val_from_df_or_default('stage', 0)
    # substage = get_val_from_df_or_default('substage', 0)
    # substage_bias = get_val_from_df_or_default('substage_bias', 0)
    # choice = get_val_from_df_or_default('choice', 0)

    # stim_dur_ds = get_val_from_df_or_default('stim_dur_ds', 0)
    # stim_dur_dm = get_val_from_df_or_default('stim_dur_dm', 0)
    # stim_dur_dl = get_val_from_df_or_default('stim_dur_dl', 0)
    # block = get_val_from_df_or_default('block', 0)
    # conditions = get_val_from_df_or_default('conditions', [])
    # completed_conditions = get_val_from_df_or_default('completed_conditions', [])
    # current_condition = get_val_from_df_or_default('current_condition', 0)
    # repetition = get_val_from_df_or_default('repetition', 0)
    # current_repetition = get_val_from_df_or_default('current_repetition', 0)
    # trial_counter = get_val_from_df_or_default('trial_counter', 0)
    # stim_trial = get_val_from_df_or_default('stim_trial', 0)
    # stim_trials = get_val_from_df_or_default('stim_trials', [])
    # stim_trial_counter = get_val_from_df_or_default('stim_trial_counter', 0)
    #
    # ror = get_val_from_df_or_default('ror', [])
    # completed_ror = get_val_from_df_or_default('completed_ror', [])
    # current_ror = get_val_from_df_or_default('current_ror', 0.0)
    # trial_counter_ror = get_val_from_df_or_default('trial_counter_ror', 0)
    #
    # block_size = get_val_from_df_or_default('block_size', 0)
    # block_trial_counter = get_val_from_df_or_default('block_trial_counter', 0)
    # block_accuracy = get_val_from_df_or_default('block_accuracy', 0.0)
    # block_number = get_val_from_df_or_default('block_number', 0)
    # ror_change = get_val_from_df_or_default('ror_change', 0)
    # block_change = get_val_from_df_or_default('block_change', 0)
    # last_stim_trial = get_val_from_df_or_default('last_stim_trial', 0)
    # last_condition_trial = get_val_from_df_or_default('last_condition_trial', 0)
    # total_trials = get_val_from_df_or_default('total_trials', 0)
    # block_correct_count = get_val_from_df_or_default('block_correct_count', 0)
    # block_valid_count = get_val_from_df_or_default('block_valid_count', 0)
    # condition_trial_counter = get_val_from_df_or_default('condition_trial_counter', 0)
    # low_trial_count = get_val_from_df_or_default('low_trial_count', 0)
    # low_accuracy_count = get_val_from_df_or_default('low_accuracy_count', 0)
    # stage_forward_change = get_val_from_df_or_default('stage_forward_change', 0)
    # stage_backward_change = get_val_from_df_or_default('stage_backward_change', 0)

    variable_defaults = {
        'stage': 0,
        'substage': 0,
        'substage_bias': 0,
        'choice': 0,
        'stim_dur_ds': 0,
        'stim_dur_dm': 0,
        'stim_dur_dl': 0,
        'block': 0,
        'conditions': [],
        'completed_conditions': [],
        'current_condition': 0,
        'repetition': 0,
        'current_repetition': 0,
        'trial_counter': 0,
        'stim_trial': 0,
        'stim_trials': [],
        'stim_trial_counter': 0,
        'ror': [],
        'completed_ror': [],
        'current_ror': 0.0,
        'trial_counter_ror': 0,
        'block_size': 0,
        'block_trial_counter': 0,
        'block_accuracy': 0.0,
        'block_number': 0,
        'ror_change': 0,
        'block_change': 0,
        'last_stim_trial': 0,
        'last_condition_trial': 0,
        'total_trials': 0,
        'block_correct_count': 0,
        'block_valid_count': 0,
        'condition_trial_counter': 0,
        'low_trial_count': 0,
        'low_accuracy_count': 0,
        'stage_forward_change': 0,
        'stage_backward_change': 0,
    }

    def get_val(column_name, default_val):
        if column_name in df.columns:
            val = last_row[column_name]
            return val if pd.notna(val) else default_val
        return default_val

    # Create a namespace and assign variables
    vars_ns = SimpleNamespace()
    for var_name, default in variable_defaults.items():
        setattr(vars_ns, var_name, get_val(var_name, default))


    # Check if task does not contain the word 'Probability'
    if 'Probability' not in task:  #Excludes all the task without the word Probability
        pass  #Working Memmory section removed

    elif 'Probability' in task:     #Includes all the task without the word Probability
        if 'Probability_Training_BB_Size' in task:
            if task_number == 3:
                message = 'PI: Advance from stage 3 to Webers Law Pre Test'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass
                stage = 4
                task = 'Probability_WebersLaw_Pre'
                block = 12  # This is the number of trials one conditions will remain for
                conditions = []  # Takes the conditions from select task file.
                completed_conditions = []  # To store completed conditions
                current_condition = 0  # To track the current condition in progress
                repetition = 2  # To store how many times the conditions needs to repeat.
                current_repetition = 0  # To store how many times the condition has repeated.
                trial_counter = 0  # Track the number of trials for the current condition
                # Image output stims:
                stim_trial = 0
                stim_trials = []
                stim_trial_counter = 0

        elif 'Probability_WebersLaw' in task:
            # Assign each value from the last row to the variables:
            stage = last_row['stage']
            block = last_row['block']
            conditions = last_row['conditions']
            completed_conditions = last_row['completed_conditions']
            current_condition = last_row['current_condition']
            repetition = last_row['repetition']
            current_repetition = last_row['current_repetition']
            trial_counter = last_row['trial_counter']
            # Image output stims:
            stim_trial = last_row['stim_trial']
            stim_trials = last_row['stim_trials']
            stim_trial_counter = last_row['stim_trial_counter']

            if stage == 5:
                block = 0
                conditions = []  # Takes the conditions from task file after first session.
                completed_conditions = []  # To store completed conditions
                current_condition = 0  # To track the current condition in progress
                repetition = 0
                current_repetition = 0  # To store how many times the condition has repeated.
                trial_counter = 0  # Track the number of trials for the current condition.
                # Image output stims:
                stim_trial = 0
                stim_trials = []
                stim_trial_counter = 0

                if task == "Probability_WebersLaw_Pre":
                    task = 'Probability_WL_Training_Acc'
                    stage = 5

                    ror = [16.0, 12.0, 8.0, 6.0, 4.0, 2.0, 1.5]
                    completed_ror = []
                    current_ror = 16.0
                    trial_counter_ror = 0
                    substage = 0
                    trial_counter = 0
                    block_size = 40  # Every 40 blocks the criteria will be tested.
                    block_trial_counter = 0  # Counter for accuracy.
                    block_accuracy = 0.0  # Accuracy for that 40 trial block
                    block_number = 1
                    ror_change = 0
                    block_change = 0
                    last_stim_trial = 0
                    last_condition_trial = 0
                    total_trials = 0
                    block_correct_count = 0  # Tracks the number of corrects in the block
                    block_valid_count = 0  ##Tracks the number of valid trials in the block

                    message = 'PI: Probability_WebersLaw_Pre Test complete, Moving to Webers law Training on next session.'
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass
                if task == "Probability_WebersLaw_Post":
                    #task = 'Probability_Bastos_Taylor'
                    # Weber's Law:
                    stage = 1
                    ror = []
                    completed_ror = []
                    current_ror = 0.0
                    trial_counter_ror = 0

                    block_size = 0  # Every 40 blocks the criteria will be tested.
                    block_trial_counter = 0  # Counter for accuracy.
                    block_accuracy = 0.0  # Accuracy for that 40 trial block
                    block_number = 0
                    ror_change = 0
                    block_change = 0
                    last_stim_trial = 0
                    last_condition_trial = 0
                    total_trials = 0
                    block_correct_count = 0  # Tracks the number of corrects in the block
                    block_valid_count = 0  ##Tracks the number of valid trials in the block

                    message = 'PI: Probability_WebersLaw_Post Test complete, Moving to Handtracking'
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

        elif 'Probability_WL_Training' in task:
            # Assign each value from the last row to the variables:
            stage = last_row['stage']
            ror = last_row['ror']
            completed_ror = last_row['completed_ror']
            current_ror = last_row['current_ror']
            trial_counter_ror = last_row['trial_counter_ror']
            block_size = last_row['block_size']
            block_trial_counter = last_row['block_trial_counter']  # Counter for accuracy.
            block_accuracy = last_row['block_accuracy']  # Accuracy for that 40 trial block
            block_number = last_row['block_number']  # Accuracy for that 40 trial block
            ror_change = last_row['ror_change']
            block_change = last_row['block_change']
            last_stim_trial = last_row['last_stim_trial']
            last_condition_trial = last_row['last_condition_trial']
            total_trials = last_row['total_trials']
            block_correct_count = last_row['block_correct_count']
            block_valid_count = last_row['block_valid_count']
            trial_end_criteria = last_row['trial_end_criteria']

            stim_trial = last_row['stim_trial']
            stim_trials = last_row['stim_trials']
            stim_trial_counter = last_row['stim_trial_counter']

            condition_trial_counter = last_row['condition_trial_counter']
            conditions = last_row['conditions']

            message = f"PI: ROR {current_ror} and Block {block_number} for subject {my_subject}. Total Trials in ROR are {trial_counter_ror}"
            print(f'{message}')
            try:
                telegram_bot.alarm_finish_session(message, my_subject)
            except:
                print('Telegram message not sent')
                pass

            if trial_counter_ror >= 216:
                message = f"URGENT PI: ROR {current_ror} and Block {block_number} for subject {my_subject}. Total Trials are {trial_counter_ror}"
                print(f'{message}')
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass


            # Telgram warning messages:
            # Load dictionary from file
            if task == 'Probability_WL_Training_Acc':
                file_path = "/home/ratvillage01/academy/user/trial_criteria_training.json"
            if task == 'Probability_WL_Training_Runthrough_Acc':
                file_path = "/home/ratvillage01/academy/user/trial_criteria_runthrough.json"
            try:
                with open(file_path, "r") as file:
                    trial_message_criteria = json.load(file)
                print("✅ JSON file loaded successfully!")
            except FileNotFoundError:
                print(f"❌ Error: JSON file not found at {file_path}")
            except json.JSONDecodeError:
                print("❌ Error: JSON file is not properly formatted.")

            # Convert JSON keys to float (since JSON loads numbers as strings)
            trial_message_criteria = {
                subject: {float(ror): values for ror, values in ror_dict.items()}
                for subject, ror_dict in trial_message_criteria.items()
            }
            # Ensure `current_ror` is treated as a float
            current_ror = float(current_ror)
            # Debugging Information
            if my_subject in trial_message_criteria:
                print(f"✅ {my_subject} found in trial_message_criteria")
            else:
                print(f"❌ {my_subject} NOT found in trial_message_criteria")
            if current_ror in trial_message_criteria.get(my_subject, {}):
                print(f"✅ ROR {current_ror} found for subject {my_subject}")
            else:
                print(f"❌ ROR {current_ror} NOT found for subject {my_subject}")
            if trial_message_criteria.get(my_subject, {}).get(current_ror):
                print(f"✅ Threshold list exists for {my_subject} in ROR {current_ror}")
            else:
                print(f"❌ No thresholds found for {my_subject} in ROR {current_ror}")
            # Handle threshold check and updating logic
            if (
                    my_subject in trial_message_criteria
                    and current_ror in trial_message_criteria[my_subject]
                    and trial_message_criteria[my_subject][current_ror]
            ):
                print(f"Current Subject: {my_subject}, Current ROR: {current_ror}")
                print(f"Thresholds before pop: {trial_message_criteria[my_subject][current_ror]}")
                next_threshold = trial_message_criteria[my_subject][current_ror][0]
                if block_trial_counter >= next_threshold:
                    message = f"URGENT: {block_trial_counter} TRIALS COMPLETED IN ROR {current_ror} FOR {my_subject}. CHECK DATA."
                    print(message)
                    try:
                        for _ in range(3):
                            telegram_bot.alarm_finish_session(message, my_subject)
                        print(
                            f"Before pop for ROR {current_ror}: {trial_message_criteria[my_subject][current_ror]}")
                        if trial_message_criteria[my_subject][current_ror]:
                            trial_message_criteria[my_subject][current_ror].pop(0)
                        print(f"After pop for ROR {current_ror}: {trial_message_criteria[my_subject][current_ror]}")
                        print("Full trial_message_criteria after pop:",
                              json.dumps(trial_message_criteria, indent=4))
                        print(f"Dictionary ID before and after pop: {id(trial_message_criteria)}")
                        # Save updated dictionary back to file
                        with open(file_path, "w") as file:
                            json.dump(trial_message_criteria, file, indent=4)
                        print("✅ JSON file updated successfully!")
                    except Exception as e:
                        print(f"Telegram message not sent for {my_subject}. Error: {e}")

            if task == "Probability_WL_Training_Acc":
                if stage == 4: # when Probability_WL_Training_Acc is complete, it changes stage to 4
                    task = 'Probability_WL_Training_Runthrough_Acc'
                    stage = 5
                    # if isinstance(completed_ror, str):
                    #     completed_ror = str_to_list(completed_ror)
                    # ror = completed_ror
                    ror = [16.0, 12.0, 8.0, 6.0, 4.0, 2.0, 1.5]
                    completed_ror = []
                    current_ror = 16.0
                    trial_counter_ror = 0
                    substage = 0
                    trial_counter = 0
                    block_size = 40  # Every 40 blocks the criteria will be tested.
                    block_trial_counter = 0  # Counter for accuracy.
                    block_accuracy = 0.0  # Accuracy for that 40 trial block
                    block_number = 1
                    ror_change = 0
                    block_change = 0
                    last_stim_trial = 0
                    last_condition_trial = 0
                    total_trials = 0
                    block_correct_count = 0  # Tracks the number of corrects in the block
                    block_valid_count = 0
                    stim_trial = 0
                    stim_trials = []
                    stim_trial_counter = 0
                    condition_trial_counter = 0
                    conditions = []


                    message = f"PI: Probability_WL_Training complete, Moving to Runthrough."
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

            if task == 'Probability_WL_Training_Runthrough_Acc':
                if stage == 4:
                    ror = []
                    completed_ror = []
                    current_ror = 0.0
                    # Variables for accuracy testing in Weber's Law Training:
                    trial_counter_ror = 0
                    block_size = 0  # Every 40 blocks the criteria will be tested.
                    block_trial_counter = 0  # Counter for accuracy.
                    block_accuracy = 0.0  # Accuracy for that 40 trial block
                    block_number = 0
                    ror_change = 0
                    block_change = 0
                    last_stim_trial = 0
                    last_condition_trial = 0
                    total_trials = 0
                    substage = 0
                    block_correct_count = 0  # Tracks the number of corrects in the block
                    block_valid_count = 0

                    #task = 'Probability_WebersLaw_Post'
                    stage = 4
                    block = 12  # This is the number of trials one conditions will remain for
                    conditions = []  # Takes the conditions from select task file.
                    completed_conditions = []  # To store completed conditions
                    current_condition = 0  # To track the current condition in progress
                    repetition = 2  # To store how many times the conditions needs to repeat.
                    current_repetition = 0  # To store how many times the condition has repeated.
                    trial_counter = 0  # Track the number of trials for the current condition
                    # Image output stims:
                    stim_trial = 0
                    stim_trials = []
                    stim_trial_counter = 0

                    message = f"PI: Probability_WL_Training_Runthrough complete, Moving to Post Training."
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

            # Ensure current_ror is an integer after processing
            if isinstance(current_ror, str):
                current_ror = float(current_ror)  # Convert to float if it's a string
                print(f"current_ror converted to int: {current_ror}")
            # Convert ror and completed_ror to lists using isinstance
            if isinstance(ror, str):
                ror = str_to_list(ror)
                print(f"Converted ror to list: {ror}")
            if isinstance(completed_ror, str):
                completed_ror = str_to_list(completed_ror)
                print(f"Converted completed_ror to list: {completed_ror}")

        # elif 'Probability_Turtle_Training' in task:
        #     trial_criteria = 30
        #     accuracy_criteria = 0.80
        #     trial_end_criteria = 3000
        #
        #     if my_subject == 'm2':
        #         trial_criteria = 3
        #         accuracy_criteria = 0.7
        #         trial_end_criteria = 10
        #
        #     trial_counter = last_row['trial_counter']
        #
        #     if trial_counter >= trial_end_criteria:
        #         stage = 7
        #         message = f"{trial_end_criteria} trials completed in substage {substage}. Task ended."
        #         print(f'{message}')
        #         try:
        #             telegram_bot.alarm_finish_session(message, my_subject)
        #             telegram_bot.alarm_completed_criteria(task, my_subject)
        #         except:
        #             print('Telegram message not sent')
        #             pass
        #
        #     if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria):
        #         # Move to the next stage up to stage 3
        #         if substage < 3:
        #             substage += 1
        #             trial_counter = 0
        #             message = (f"Moving to stage {substage} due to 80% accuracy in a session of {valid_trials_last} trials.")
        #             print(f'{message}')
        #             try:
        #                 telegram_bot.alarm_finish_session(message, my_subject)
        #             except:
        #                 print('Telegram message not sent')
        #                 pass
        #         else:
        #             stage = 7
        #             #task = 'Probability_Turtle_Test'
        #             message = (f"Last substage {substage} completed, Training complete")
        #             print(f'{message}')
        #             try:
        #                 telegram_bot.alarm_finish_session(message, my_subject)
        #                 telegram_bot.alarm_completed_criteria(task, my_subject)
        #             except:
        #                 print('Telegram message not sent')
        #                 pass
        #     else:
        #         message = ("Criteria for moving to the next stage not met.")
        #         print(f'{message}')
        #         try:
        #             telegram_bot.alarm_finish_session(message, my_subject)
        #         except:
        #             print('Telegram message not sent')
        #             pass

    elif task == 'Water_Filler':
        print("rat drank water")

    if my_subject == 'm2':
        wait_seconds = 1

    # Remove all the blank trials: It doesnt work as the file doesn'd get saved here.
    df = df.loc[~((df['trial_length'] == 0.1) & (df['trial_result'].isna()))].copy()

    #all of these are written in subjects.csv:
    return task, stage, substage, substage_bias, wait_seconds, stim_dur_ds, stim_dur_dm, stim_dur_dl, choice, block, conditions, completed_conditions, current_condition, repetition, current_repetition, trial_counter, stim_trial, stim_trials, stim_trial_counter, ror, completed_ror, current_ror, trial_counter_ror, moved_back_counter, block_size, block_trial_counter, block_accuracy, block_number, ror_change, block_change, last_stim_trial, last_condition_trial, total_trials, block_correct_count, block_valid_count, condition_trial_counter,stage_forward_change,stage_backward_change

# def str_append(my_str: str, value: str) -> str:
#     """Simulate appending a value to a string representation of a list."""
#     my_str = my_str.strip()  # Ensure no leading/trailing spaces
#     if my_str == "[]" or not my_str:  # If empty list, add value directly
#         return f"[{value}]"
#     return my_str[:-1] + f", {value}]"  # Insert value before the closing bracket
#
#
# def str_pop(my_str: str) -> tuple[str, str]:
#     """Simulate popping the first value from a string representation of a list."""
#     my_str = my_str.strip()  # Ensure no leading/trailing spaces
#     if my_str == "[]" or not my_str:  # Handle empty list
#         raise ValueError("Cannot pop from an empty list")
#
#     # Remove the brackets and split by commas
#     parts = my_str[1:-1].split(", ")
#     popped_value = parts.pop(0)  # Remove the first element
#     new_str = f"[{', '.join(parts)}]"  # Reconstruct the string
#     return new_str, popped_value
#
# # Convert ror and completed_ror back to lists
# # Convert ror and completed_ror back to lists
# def str_to_list(my_str: str) -> list:
#     """Convert a string representation of a list back to a Python list."""
#     my_str = my_str.strip()  # Ensure no leading/trailing spaces
#     if my_str == "[]" or not my_str:
#         return []  # Return an empty list if the string is empty or '[]'
#     return [float(x) if '.' in x else int(x) for x in my_str[1:-1].split(", ")]


# def calculate_move_back_criteria(df_last3, sessions, trial_criteria, accuracy_moveback_criteria):
#     """
#     Calculate low trial count and low accuracy count for given sessions.
#
#     Args:
#         df_last3 (pd.DataFrame): DataFrame containing data for the last three sessions.
#         sessions (list): List of session identifiers to evaluate.
#         trial_criteria (int): Minimum required trials per session.
#         accuracy_moveback_criteria (float): Minimum required accuracy per session.
#
#     Returns:
#         tuple: (low_trial_count, low_accuracy_count)
#             - low_trial_count (int): Number of sessions below the trial criteria.
#             - low_accuracy_count (int): Number of sessions below the accuracy criteria.
#     """
#     low_trial_count = 0
#     low_accuracy_count = 0
#     for session in sessions:
#         session_data = df_last3[df_last3['session'] == session]
#         # Calculate trial count and accuracy
#         trial_count = session_data['trial'].max()
#         correct_trials = session_data[session_data['trial_result'].isin(['correct', 'correct_first'])].shape[
#             0]
#         valid_trials = session_data[session_data['trial_result'] != 'miss'].shape[0]
#         accuracy = correct_trials / valid_trials if valid_trials > 0 else 0
#         # Check criteria
#         if trial_count < trial_criteria:
#             low_trial_count += 1
#         if accuracy < accuracy_moveback_criteria:
#             low_accuracy_count += 1
#     return low_trial_count, low_accuracy_count

# def calculate_move_back_criteria(df_last7, sessions, trial_criteria, accuracy_moveback_criteria):
#     """
#     Calculate low trial count and low accuracy count for given sessions.
#
#     Args:
#         df_last7 (pd.DataFrame): DataFrame containing data for the last seven sessions.
#         sessions (list): List of session identifiers to evaluate.
#         trial_criteria (int): Minimum required trials per session.
#         accuracy_moveback_criteria (float): Minimum required accuracy per session.
#
#     Returns:
#         tuple: (low_trial_count, low_accuracy_count)
#             - low_trial_count (int): Number of sessions below the trial criteria.
#             - low_accuracy_count (int): Number of sessions below the accuracy criteria.
#     """
#     low_trial_count = 0
#     low_accuracy_count = 0
#     for session in sessions:
#         session_data = df_last7[df_last7['session'] == session]
#         # Calculate trial count and accuracy
#         trial_count = session_data['trial'].max()
#         correct_trials = session_data[session_data['trial_result'].isin(['correct', 'correct_first'])].shape[
#             0]
#         valid_trials = session_data[session_data['trial_result'] != 'miss'].shape[0]
#         accuracy = correct_trials / valid_trials if valid_trials > 0 else 0
#         # Check criteria
#         if trial_count < trial_criteria:
#             low_trial_count += 1
#         if accuracy < accuracy_moveback_criteria:
#             low_accuracy_count += 1
#     return low_trial_count, low_accuracy_count
#
#
# def calculate_move_forward_criteria(df_last2, sessions, trial_count, trial_criteria, accuracy_forward_criteria):
#     """
#     Calculate high trial count and high accuracy count for given sessions.
#
#     Args:
#         df_last2 (pd.DataFrame): DataFrame containing data for the last two sessions.
#         sessions (list): List of session identifiers to evaluate.
#         trial_count (int): Trial count for the sessions.
#         trial_criteria (int): Minimum required trials per session.
#         accuracy_forward_criteria (float): Minimum required accuracy per session.
#
#     Returns:
#         bool: True if the subject meets the move forward criteria, False otherwise.
#     """
#     for session in sessions:
#         session_data = df_last2[df_last2['session'] == session]
#         correct_trials = session_data[session_data['trial_result'].isin(['correct', 'correct_first'])].shape[0]
#         valid_trials = session_data[session_data['trial_result'] != 'miss'].shape[0]
#         accuracy = correct_trials / valid_trials if valid_trials > 0 else 0
#         # Check criteria
#         if trial_count < trial_criteria or accuracy < accuracy_forward_criteria:
#             return False  # If either condition is not met in any session, do not move forward
#     return True  # Move forward if all sessions meet the criteria
