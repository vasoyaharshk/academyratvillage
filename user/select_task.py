import numpy as np
from wx.lib.pubsub.py2and3 import print_
from academy import telegram_bot
from user import settings
import random
import json
import pandas as pd
from types import SimpleNamespace
from datetime import datetime, timedelta


# Examples of functions to calculate new task and stage
# If the function fails to return, new task and stage will be previous task and previous stage
# df is the session dataframe for the subject


def select_task(df, subject):
    task = subject.task
    wait_seconds = 3600 * settings.TIME_TO_ENTER
    my_subject = df.subject.iloc[0]

    #This removes all the blank trials which the system generates by mistake:
    df = df[~((df['trial_result'].isna() | (df['trial_result'] == '')) & (
                df['trial_length'].isna() | (df['trial_length'] == '')))].copy()

    last_row = df.iloc[-1]  # Get the last row of the DataFrame

    #Assign reward decibels: Needs to be a dictionary if different for each individual.
    reward_db = 70.0

    #Reward Frequencies assigned again after the task:
    # Map each rat to its centre frequency
    reward_frequency_map = {
        'chand': 250.0,
        'felix': 290.0,
        'fergus': 336.4,
        'geralt': 390.2,
        'joey': 452.7,
        'ross': 525.1,
        'innes': 609.1,
        'pol': 706.6,
        'm3': 100.0,
    }

    # Assign frequency based on subject
    reward_frequency = reward_frequency_map.get(my_subject)

    # Double check the value for frequency from the above table
    reward_frequency_subjects = subject.reward_frequency

    if reward_frequency_subjects == reward_frequency:
        print("the reward frequencies match")
    else:
        message = f"Reward frequency mismatch for subject. Reward frequency map {reward_frequency}, Reward freuquency in subjects {reward_frequency_subjects}"
        try:
            telegram_bot.alarm_finish_session(message, my_subject)
        except:
            print('Telegram message not sent')

    reward_duration = 0 #Only change it when and if you need to for each rat different duration.

    # #Reward duration assigned again after the task:
    # # Map each rat to its duration
    # reward_duration_map = {
    #     'chandler': 1.0,
    #     'felix': 2.0,
    #     'fergus': 1.0,
    #     'geralt': 2.0,
    #     'joey': 1.0,
    #     'ross': 2.0,
    #     'innes': 1.0,
    #     'pol': 2.0,
    # }
    #
    # # Assign duration based on subject
    # reward_duration = reward_duration_map.get(my_subject)
    #
    # # Double check the value for duration from the above table
    # reward_duration_subjects = subject.reward_duration
    # if reward_duration_subjects == reward_duration:
    #     print("the reward duration match")
    # else:
    #     message = f"Reward duration mismatch for subject '{my_subject}'"
    #     try:
    #         telegram_bot.alarm_finish_session(message, my_subject)
    #     except:
    #         print('Telegram message not sent')
    #     raise ValueError(message)


    def get_val_from_df_or_default(column_name, default_val):
        if column_name in df.columns:
            val = last_row[column_name]
            if pd.isna(val):
                return default_val
            return val
        return default_val


    task_number = get_val_from_df_or_default('task_number', 0)
    stage = get_val_from_df_or_default('stage', 0)
    substage = get_val_from_df_or_default('substage', 0)
    substage_bias = get_val_from_df_or_default('substage_bias', 0)
    choice = get_val_from_df_or_default('choice', 0)
    stim_dur_ds = get_val_from_df_or_default('stim_dur_ds', 0)
    stim_dur_dm = get_val_from_df_or_default('stim_dur_dm', 0)
    stim_dur_dl = get_val_from_df_or_default('stim_dur_dl', 0)
    block = get_val_from_df_or_default('block', 0)
    conditions = get_val_from_df_or_default('conditions', [])
    completed_conditions = get_val_from_df_or_default('completed_conditions', [])
    current_condition = get_val_from_df_or_default('current_condition', 0)
    repetition = get_val_from_df_or_default('repetition', 0)
    current_repetition = get_val_from_df_or_default('current_repetition', 0)
    trial_counter = get_val_from_df_or_default('trial_counter', 0)
    stim_trial = get_val_from_df_or_default('stim_trial', 0)
    stim_trials = get_val_from_df_or_default('stim_trials', [])
    stim_trial_counter = get_val_from_df_or_default('stim_trial_counter', 0)
    ror = get_val_from_df_or_default('ror', [])
    completed_ror = get_val_from_df_or_default('completed_ror', [])
    current_ror = get_val_from_df_or_default('current_ror', 0.0)
    trial_counter_ror = get_val_from_df_or_default('trial_counter_ror', 0)
    block_size = get_val_from_df_or_default('block_size', 0)
    block_trial_counter = get_val_from_df_or_default('block_trial_counter', 0)
    block_accuracy = get_val_from_df_or_default('block_accuracy', 0.0)
    block_number = get_val_from_df_or_default('block_number', 0)
    ror_change = get_val_from_df_or_default('ror_change', 0)
    block_change = get_val_from_df_or_default('block_change', 0)
    last_stim_trial = get_val_from_df_or_default('last_stim_trial', 0)
    last_condition_trial = get_val_from_df_or_default('last_condition_trial', 0)
    total_trials = get_val_from_df_or_default('total_trials', 0)
    block_correct_count = get_val_from_df_or_default('block_correct_count', 0)
    block_valid_count = get_val_from_df_or_default('block_valid_count', 0)
    condition_trial_counter = get_val_from_df_or_default('condition_trial_counter', 0)
    stage_forward_change = get_val_from_df_or_default('stage_forward_change', 0)
    stage_backward_change = get_val_from_df_or_default('stage_backward_change', 0)
    moved_back_counter = get_val_from_df_or_default('moved_back_counter', 0)
    last_forward_stage = get_val_from_df_or_default('last_forward_stage', 0)
    last_backward_stage = get_val_from_df_or_default('last_backward_stage', 0)
    stage_sequence = get_val_from_df_or_default('stage_sequence', [])
    last_stage_trial  = get_val_from_df_or_default('last_stage_trial', 0)
    stage_sequence_counter  = get_val_from_df_or_default('stage_sequence_counter', 0)

    substage_counter_1  = get_val_from_df_or_default('substage_counter_1', 0)
    substage_counter_2  = get_val_from_df_or_default('substage_counter_2', 0)
    substage_counter_3  = get_val_from_df_or_default('substage_counter_3', 0)
    substage_counter_4  = get_val_from_df_or_default('substage_counter_4', 0)
    substage_counter_5  = get_val_from_df_or_default('substage_counter_5', 0)
    substage_counter_6  = get_val_from_df_or_default('substage_counter_6', 0)
    substage_counter_7  = get_val_from_df_or_default('substage_counter_7', 0)
    substage_counter_8  = get_val_from_df_or_default('substage_counter_8', 0)
    substage_counter_9  = get_val_from_df_or_default('substage_counter_9', 0)
    substage_counter_10  = get_val_from_df_or_default('substage_counter_10', 0)
    substage_counter_11  = get_val_from_df_or_default('substage_counter_11', 0)

    group  = get_val_from_df_or_default('group', 0)
    pair  = get_val_from_df_or_default('pair', 0)

    #Not tracked:
    max_move_backs = get_val_from_df_or_default('max_move_backs', 0)

    #Danger, only use this when the variables in df but not in defaulted list above are too many:
    # for key, val in last_row.items():
    #     if key not in variable_defaults:
    #         if isinstance(val, float) and pd.isna(val):
    #             val = None
    #         exec(f"{key} = {repr(val)}")

    # Check if task does not contain the word 'Probability'
    if 'Probability' not in task:  #Excludes all the task without the word Probability. Early Training Tasks.
        #dataframes
        last_session = df.session.max()
        df_last14 = df.loc[df['session'] > last_session - 14].copy()  # last 14 sessions
        df_last5 = df.loc[df['session'] > last_session - 5].copy()  # last five sessions
        df_last3 = df.loc[df['session'] > last_session - 3].copy()  # last three sessions
        df_last2 = df.loc[df['session'] > last_session - 2].copy()  # last two sessions
        df_last1 = df.loc[df['session'] == last_session].copy()           # last session
        # VERY IMPORTANT, THE ABOVE LINE IS COMMENTED OUT BECAUSE WE WANT THE DF TO REMAIN THE SUBJECT'S ALL SESSIONS INSTEAD OF JUST LAST AS
        # WE WANT TO GET LAST 55 TRIALS FOR THE CRITERIA CHANGED.

        # number of valid trials
        n_trials = df_last1[df_last1.trial_result != 'miss'].trial.count()
        n_trials_prev = df_last2[df_last2.trial_result != 'miss'].groupby('session')['trial'].count().values[0]

        if task == 'Automatic_Water':
            # Get last two sessions for this subject
            last2_sessions = df_last2['session'].unique()

            # Check if both of them are Automatic_Water
            recent_tasks = df[df['session'].isin(last2_sessions)]['task'].unique()
            if all(t == 'Automatic_Water' for t in recent_tasks):
                # Look at the session before those two
                min_session_in_auto = min(last2_sessions)
                df_before_auto = df[df['session'] < min_session_in_auto]
                previous_non_auto = df_before_auto[df_before_auto['task'] != 'Automatic_Water']

                if not previous_non_auto.empty:
                    last_valid_session = previous_non_auto.sort_values(by='session').iloc[-1]
                    task = last_valid_session.task

                    message = f"Completed 2 sessions of Automatic_Water. Reverting to task: {task}, stage: {stage}"
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')


        if task == 'Habituation':
            wait_seconds = 3600 * 1
            if len(df_last3.session.unique())>=3: # Pass after 3 sessions
                task = 'LickTeaching'
                message = 'Advance from Habituation to LickTeaching'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

        elif task == 'LickTeaching':
            message = f"DEBUG: Subject={my_subject}, Task={task}, Valid trials in last session={n_trials}"
            try:
                telegram_bot.alarm_finish_session(message, my_subject)
            except:
                print('Telegram message not sent')
                pass
            wait_seconds = 3600 * 2
            if n_trials >= 75:
                task = 'TouchTeaching_no_mask'
                stage = 1.0
                message = 'Advance from Lickteaching to Touchteaching'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

        elif task == 'TouchTeaching_no_mask':
            if n_trials >= 50:
                message = f"{my_subject} advance to next stage in Touchteaching from {stage}'"
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass
                if stage == 1:
                    stage = 2.0
                elif stage == 2:
                    stage = 3.0
                elif stage == 3:
                    task = 'Probability_Extra_Training_Acc'
                    stage = 1.0
                    task_number = 1
                    block_size = 40
                    block_number = 1
                    message = f"{my_subject} advance from early training to probability training with pegs'"
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

    #Probability tasks start from here:
    elif 'Probability' in task:     #Includes all the task without the word Probability
        if task == 'Probability_Extra_Training_Acc':
            if moved_back_counter > max_move_backs:
                message = f"URGENT: Moved back {moved_back_counter} FOR {my_subject}. CHECK DATA."
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

            if task_number == 2:
                stage = 1  # Current stage within the task
                substage = 0  # Current substage within the stage
                substage_bias = 0  # Side bias stage for substage behavior
                task_number = 2  # Each task has a unique number. See RV script guide.

                # Needed to create blocks of 40 trials for criterion to be assessed on:
                block_size = 40  # The number of trials in a block
                block_trial_counter = 0  # Trial count within the current block
                block_accuracy = 0.0  # Accuracy in the current block
                block_number = 1  # Sequential block number
                ror_change = 0  # If it is 1, ROR will change on the next trial.
                block_change = 0  # If it is 1, a new block will start on the next trial
                total_trials = 0  # Total trials across the task.
                block_correct_count = 0  # Number of correct responses in the block
                block_valid_count = 0  # Number of valid (non-missed) trials in the block
                condition_trial_counter = 0  # Counter for randomising conditions
                last_forward_stage = 0  # The stage moved forward from after a forward change
                last_backward_stage = 0  # The stage moved backward to after the last backward change
                moved_back_counter = 0  # Counter for how many times the subject moved back a stage
                stage_forward_change = 0  # Whether stage move forward on the next trial
                stage_backward_change = 0  # Whether stage move backward on the next trial

                # Left Right Function Randomisation variables:
                stim_trial = 0  # The function number of the correct stimulus in the current trial. This designates trial type, e.g. from Discrim. C: left is correct, big jar is correct, spacer in correct
                stim_trials = []  # List of correct stimulus function randomised.
                stim_trial_counter = 0  # It counts the number of trials within a randomization block. Doesnt change when Bias breaking is active.
                last_stim_trial = 0  # the function of the last trial of the previous block. Used to ensure first trial of next block is different

                task = 'Probability_Training_BB_Size_Acc'
                message = 'Advance from Etra training to Core training'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

        elif 'Probability_Extra_Training_Bias' in task:
            if moved_back_counter > max_move_backs:
                message = f"URGENT: Moved back {moved_back_counter} FOR {my_subject}. CHECK DATA."
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

            if task_number == 1:
                task = 'Probability_Extra_Training_Acc'
                substage_bias = 0
                message = 'Advance from Etra training Bias breaking to normal training'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

        elif task == 'Probability_Training_BB_Size_Acc':
            if moved_back_counter > max_move_backs:
                message = f"URGENT: Moved back {moved_back_counter} FOR {my_subject}. CHECK DATA."
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

            if task_number == 3:
                substage = 0  # Current substage within the stage
                substage_bias = 0  # Side bias stage for substage behavior
                task_number = 2  # Each task has a unique number. See RV script guide.

                # Needed to create blocks of 40 trials for criterion to be assessed on:
                block_size = 40  # The number of trials in a block
                block_trial_counter = 0  # Trial count within the current block
                block_accuracy = 0.0  # Accuracy in the current block
                block_number = 1  # Sequential block number
                ror_change = 0  # If it is 1, ROR will change on the next trial.
                block_change = 0  # If it is 1, a new block will start on the next trial
                total_trials = 0  # Total trials across the task.
                block_correct_count = 0  # Number of correct responses in the block
                block_valid_count = 0  # Number of valid (non-missed) trials in the block
                condition_trial_counter = 0  # Counter for randomising conditions
                last_forward_stage = 0  # The stage moved forward from after a forward change
                last_backward_stage = 0  # The stage moved backward to after the last backward change
                moved_back_counter = 0  # Counter for how many times the subject moved back a stage
                stage_forward_change = 0  # Whether stage move forward on the next trial
                stage_backward_change = 0  # Whether stage move backward on the next trial

                # Left Right Function Randomisation variables:
                last_stim_trial = 0  # the function of the last trial of the previous block. Used to ensure first trial of next block is different

                message = 'PI: Advance from Core training to Webers Law Pre Test'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

                # Weber's Law Pretest:
               #  stage = 4
               # # task = 'Probability_WebersLaw_Pre'
               #  block = 12  # This is the number of trials one conditions will remain for
               #  conditions = []  # Takes the conditions from select task file.
               #  completed_conditions = []  # To store completed conditions
               #  current_condition = 0  # To track the current condition in progress
               #  repetition = 2  # To store how many times the conditions needs to repeat.
               #  current_repetition = 0  # To store how many times the condition has repeated.
               #  trial_counter = 0  # Track the number of trials for the current condition
               #  # Image output stims:
               #  stim_trial = 0
               #  stim_trials = []
               #  stim_trial_counter = 0

                # Cognitive Bias:
                reward_group = {
                    'chandler': 1,
                    'felix': 1,
                    'joey': 1,
                    'ross': 1,
                    'fergus': 2,
                    'geralt': 2,
                    'innes': 2,
                    'pol': 2
                }

                group = reward_group.get(my_subject.lower(), group)
                pair = 1  # same for all rats

                print(f"Cognitive Bias: Subject={my_subject} → group={group}, pair={pair}")

        elif 'Cognitive_Bias_Auditory_Training' in task:
            #Move pair +1 when criterion is met:
            accuracy_criteria = 0.85

            df_cb = df[df['task'].str.contains('Cognitive_Bias_Auditory_Training', na=False)].copy()
            if not df_cb.empty:
                sessions = sorted(df_cb['session'].unique())

                def session_stats(sess_id):
                    s = df_cb[df_cb['session'] == sess_id]
                    valid = s[s['trial_result'] != 'miss']
                    n_valid = valid.shape[0]
                    correct = valid[valid['trial_result'].isin(['correct', 'correct_first'])].shape[0]
                    acc = (correct / n_valid) if n_valid > 0 else 0.0
                    return n_valid, acc

                # Version 1 (strict):
                # (uncomment this block if you want strict criterion)
                # (n1, a1) = session_stats(sessions[-2])
                # (n2, a2) = session_stats(sessions[-1])
                # print(f"[CB] last2 sessions={sessions[-2:]} "
                #       f"| s1: valid={n1}, acc={a1:.3f} | s2: valid={n2}, acc={a2:.3f}")
                # meets = (n1 == 75 and a1 >= accuracy_criteria) and (n2 == 75 and a2 >= accuracy_criteria)



                # Version 2 (skip short sessions):
                # (uncomment this block if you want skip-short behaviour)
                full_sessions = [s for s in sessions if session_stats(s)[0] == 75]
                if len(full_sessions) >= 2:
                    last_two_full = full_sessions[-2:]
                    (n1, a1) = session_stats(last_two_full[0])
                    (n2, a2) = session_stats(last_two_full[1])
                    print(f"[CB] last2 full sessions={last_two_full} "
                          f"| s1: valid={n1}, acc={a1:.3f} | s2: valid={n2}, acc={a2:.3f}")
                    meets = (a1 >= accuracy_criteria) and (a2 >= accuracy_criteria)
                else:
                    meets = False
                    print(f"[CB] Not enough full 75-trial sessions for {my_subject}")


                if meets:
                    new_pair = min(int(pair) + 1, 4)
                    if new_pair != pair:
                        message = (f"[CB] {my_subject}: criterion met (≥{accuracy_criteria * 100:.0f}% "
                                   f"on two 75-trial sessions). pair {pair} → {new_pair}")
                        print(message)
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                            telegram_bot.alarm_completed_criteria(f"CB pair→{new_pair}", my_subject)
                        except:
                            print('Telegram message not sent')
                        pair = new_pair
                    else:
                        print(f"[CB] {my_subject}: already at max pair={pair}, no change.")
            else:
                print(f"[CB] {my_subject}: no CB sessions found; no pair change.")


        elif 'Probability_Training_BB_Size_Bias' in task:
            if moved_back_counter > max_move_backs:
                message = f"URGENT: Moved back {moved_back_counter} FOR {my_subject}. CHECK DATA."
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

            if task_number == 1:
                task = 'Probability_Training_BB_Size_Acc'
                substage_bias = 0
                message = 'Advance from Core training Bias breaking to normal training'
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

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
                    task = 'Probability_Handtracking_Zoomed'
                    # Weber's Law:
                    stage = 1
                    substage = 1
                    ror = []
                    completed_ror = []
                    current_ror = 0.0
                    trial_counter_ror = 0
                    trial_counter = 0

                    block_size = 40  # Every 40 blocks the criteria will be tested.
                    block_trial_counter = 0  # Counter for accuracy.
                    block_accuracy = 0.0  # Accuracy for that 40 trial block
                    block_number = 1
                    ror_change = 0
                    block_change = 0
                    stim_trial = 0
                    stim_trials = []
                    stim_trial_counter = 0
                    last_stim_trial = 0
                    last_condition_trial = 0
                    total_trials = 0
                    block_correct_count = 0  # Tracks the number of corrects in the block
                    block_valid_count = 0  ##Tracks the number of valid trials in the block
                    moved_back_counter = 0
                    task_number = 4
                    stage_forward_change = 0
                    stage_backward_change = 0
                    last_forward_stage = 0
                    last_backward_stage = 0

                    message = 'PI: Probability_WebersLaw_Post Test complete, Moving to Probability_Handtracking_Gloves'
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

                    message = f"URGENT PI: Probability_WL_Training complete, Moving to {task}."
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
                    condition_trial_counter = 0

                    task = 'Probability_WebersLaw_Post'
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


                    message = f"URGENT PI: Probability_WL_Training_Runthrough complete, Moving to {task}."
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

    #AUTOMATIC WATER CRITERIA: LAST 5 DAYS, EXCLUDING POST-AW DAYS ========
    # Skip AW logic for subject m2
    if my_subject == 'm3':
        print("Subject is m2. no AW")
    else:
        today_aw = datetime.now().date()
        last5_full_days = [today_aw - timedelta(days=i) for i in range(1, 6)]  # last 5 full days (not today)
        last6_days = [today_aw - timedelta(days=i) for i in range(0, 6)]  # today + last 5 days

        df_aw_check = df.copy()
        df_aw_check['date'] = pd.to_datetime(df_aw_check['date']).dt.date

        # Check if ANY session in today+last5 is Automatic Water
        has_aw_session = (
                df_aw_check[
                    (df_aw_check['date'].isin(last6_days)) &
                    (df_aw_check['task'] == 'Automatic_Water')
                    ].shape[0] > 0
        )

        # Count corrects in last 5 full days (not including today)
        df_aw_valid = df_aw_check[df_aw_check['trial_result'].isin(['correct', 'correct_first'])]
        corrects_last5 = (
            df_aw_valid[df_aw_valid['date'].isin(last5_full_days)]
            .groupby('date')
            .size()
            .reindex(last5_full_days, fill_value=0)
        )
        total_corrects_last5 = corrects_last5.sum()

        # Determine if Automatic Water is needed
        automatic_water_needed = (not has_aw_session) and (total_corrects_last5 < 250)

        # (Optional) Annotate entire dataframe with the status for this run
        df_aw_check['automatic_water'] = automatic_water_needed

        # Assign Automatic Water if needed
        if task != "Automatic_Water" and automatic_water_needed:
            task = "Automatic_Water"
            try:
                message = f"AW Check: {my_subject} has only {total_corrects_last5} correct trials in last 5 full days. Moving to Automatic_Water."
                telegram_bot.alarm_finish_session(message, my_subject)
            except:
                print('Telegram message not sent')

        # Debug print (optional)
        print("-----DEBUG: AW CHECK-----")
        print("Has AW session in last 6 days (inc. today):", has_aw_session)
        print("Total corrects in last 5 full days:", total_corrects_last5)
        print("Assign Automatic Water?:", automatic_water_needed)
        print("-------------------------")

    if my_subject == 'm3':
        wait_seconds = 1
        block_size = 10

    #all of these are written in subjects.csv:
    return task, stage, substage, substage_bias, wait_seconds, stim_dur_ds, stim_dur_dm, stim_dur_dl, choice, block, conditions, completed_conditions, current_condition, repetition, current_repetition, trial_counter, stim_trial, stim_trials, stim_trial_counter, ror, completed_ror, current_ror, trial_counter_ror, moved_back_counter, block_size, block_trial_counter, block_accuracy, block_number, ror_change, block_change, last_stim_trial, last_condition_trial, total_trials, block_correct_count, block_valid_count, condition_trial_counter,stage_forward_change,stage_backward_change, task_number, last_forward_stage, last_backward_stage, reward_frequency, reward_db, reward_duration, stage_sequence, last_stage_trial, stage_sequence_counter, substage_counter_1, substage_counter_2, substage_counter_3, substage_counter_4, substage_counter_5, substage_counter_6, substage_counter_7,substage_counter_8, substage_counter_9, substage_counter_10, substage_counter_11, group, pair

def str_append(my_str: str, value: str) -> str:
    """Simulate appending a value to a string representation of a list."""
    my_str = my_str.strip()  # Ensure no leading/trailing spaces
    if my_str == "[]" or not my_str:  # If empty list, add value directly
        return f"[{value}]"
    return my_str[:-1] + f", {value}]"  # Insert value before the closing bracket


def str_pop(my_str: str) -> tuple[str, str]:
    """Simulate popping the first value from a string representation of a list."""
    my_str = my_str.strip()  # Ensure no leading/trailing spaces
    if my_str == "[]" or not my_str:  #
        raise ValueError("Cannot pop from an empty list")

    # Remove the brackets and split by commas
    parts = my_str[1:-1].split(", ")
    popped_value = parts.pop(0)  # Remove the first element
    new_str = f"[{', '.join(parts)}]"  # Reconstruct the string
    return new_str, popped_value

# Convert ror and completed_ror back to lists
# Convert ror and completed_ror back to lists
def str_to_list(my_str: str) -> list:
    """Convert a string representation of a list back to a Python list."""
    my_str = my_str.strip()  # Ensure no leading/trailing spaces
    if my_str == "[]" or not my_str:
        return []  # Return an empty list if the string is empty or '[]'
    return [float(x) if '.' in x else int(x) for x in my_str[1:-1].split(", ")]


def calculate_move_back_criteria(df_last3, sessions, trial_criteria, accuracy_moveback_criteria):
    """
    Calculate low trial count and low accuracy count for given sessions.

    Args:
        df_last3 (pd.DataFrame): DataFrame containing data for the last three sessions.
        sessions (list): List of session identifiers to evaluate.
        trial_criteria (int): Minimum required trials per session.
        accuracy_moveback_criteria (float): Minimum required accuracy per session.

    Returns:
        tuple: (low_trial_count, low_accuracy_count)
            - low_trial_count (int): Number of sessions below the trial criteria.
            - low_accuracy_count (int): Number of sessions below the accuracy criteria.
    """
    low_trial_count = 0
    low_accuracy_count = 0
    for session in sessions:
        session_data = df_last3[df_last3['session'] == session]
        # Calculate trial count and accuracy
        trial_count = session_data['trial'].max()
        correct_trials = session_data[session_data['trial_result'].isin(['correct', 'correct_first'])].shape[
            0]
        valid_trials = session_data[session_data['trial_result'] != 'miss'].shape[0]
        accuracy = correct_trials / valid_trials if valid_trials > 0 else 0
        # Check criteria
        if trial_count < trial_criteria:
            low_trial_count += 1
        if accuracy < accuracy_moveback_criteria:
            low_accuracy_count += 1
    return low_trial_count, low_accuracy_count

def calculate_move_back_criteria(df_last7, sessions, trial_criteria, accuracy_moveback_criteria):
    """
    Calculate low trial count and low accuracy count for given sessions.

    Args:
        df_last7 (pd.DataFrame): DataFrame containing data for the last seven sessions.
        sessions (list): List of session identifiers to evaluate.
        trial_criteria (int): Minimum required trials per session.
        accuracy_moveback_criteria (float): Minimum required accuracy per session.

    Returns:
        tuple: (low_trial_count, low_accuracy_count)
            - low_trial_count (int): Number of sessions below the trial criteria.
            - low_accuracy_count (int): Number of sessions below the accuracy criteria.
    """
    low_trial_count = 0
    low_accuracy_count = 0
    for session in sessions:
        session_data = df_last7[df_last7['session'] == session]
        # Calculate trial count and accuracy
        trial_count = session_data['trial'].max()
        correct_trials = session_data[session_data['trial_result'].isin(['correct', 'correct_first'])].shape[
            0]
        valid_trials = session_data[session_data['trial_result'] != 'miss'].shape[0]
        accuracy = correct_trials / valid_trials if valid_trials > 0 else 0
        # Check criteria
        if trial_count < trial_criteria:
            low_trial_count += 1
        if accuracy < accuracy_moveback_criteria:
            low_accuracy_count += 1
    return low_trial_count, low_accuracy_count


def calculate_move_forward_criteria(df_last2, sessions, trial_count, trial_criteria, accuracy_forward_criteria):
    """
    Calculate high trial count and high accuracy count for given sessions.

    Args:
        df_last2 (pd.DataFrame): DataFrame containing data for the last two sessions.
        sessions (list): List of session identifiers to evaluate.
        trial_count (int): Trial count for the sessions.
        trial_criteria (int): Minimum required trials per session.
        accuracy_forward_criteria (float): Minimum required accuracy per session.

    Returns:
        bool: True if the subject meets the move forward criteria, False otherwise.
    """
    for session in sessions:
        session_data = df_last2[df_last2['session'] == session]
        correct_trials = session_data[session_data['trial_result'].isin(['correct', 'correct_first'])].shape[0]
        valid_trials = session_data[session_data['trial_result'] != 'miss'].shape[0]
        accuracy = correct_trials / valid_trials if valid_trials > 0 else 0
        # Check criteria
        if trial_count < trial_criteria or accuracy < accuracy_forward_criteria:
            return False  # If either condition is not met in any session, do not move forward
    return True  # Move forward if all sessions meet the criteria
