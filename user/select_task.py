import numpy as np
from wx.lib.pubsub.py2and3 import print_

from academy import telegram_bot
from user import settings
import random

# Examples of functions to calculate new task and stage
# If the function fails to return, new task and stage will be previous task and previous stage
# df is the session dataframe for the subject


def select_task(df, subject):

    # variables by default
    task = subject.task
    stage = float(subject.stage)
    substage = float(subject.substage)
    substage_bias = float(subject.substage_bias)
    choice = 0
    wait_seconds = 3600 * settings.TIME_TO_ENTER  # wait a minimum of x hours before allowed to start the new session)
    stim_dur_ds= 0
    stim_dur_dm= 0
    stim_dur_dl= 0
    #Weber's Law Test:
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
    #Weber's Law Training:
    ror = []
    completed_ror = []
    current_ror = 0
    trial_counter_ror = 0

    my_subject = df.subject.iloc[0]

    # Check if task does not contain the word 'Probability'
    if 'Probability' not in task:  #Excludes all the task without the word Probability
        # dataframes
        last_session = df.session.max()
        df_last14 = df.loc[df['session'] > last_session - 14].copy()  # last 14 sessions
        df_last5 = df.loc[df['session'] > last_session - 5].copy()  # last five sessions
        df_last3 = df.loc[df['session'] > last_session - 3].copy()  # last three sessions
        df_last2 = df.loc[df['session'] > last_session - 2].copy()  # last two sessions
        #df = df.loc[df['session'] == last_session].copy()           # last session
        # VERY IMPORTANT, THE ABOVE LINE IS COMMENTED OUT BECAUSE WE WANT THE DF TO REMAIN THE SUBJECT'S ALL SESSIONS INSTEAD OF JUST LAST AS
        # WE WANT TO GET LAST 55 TRIALS FOR THE CRITERIA CHANGED.

        # number of trials
        n_trials = df.trial.max()  # number of trials in current session
        n_trials_prev = df_last2.groupby('session')['trial'].max().values[0]  # number of trials in previous session

        #setup
        setup = df.box.unique()

        #Long time to enter for certain subjects
        if df.subject.iloc[0] in settings.LONGER_TIME_TO_ENTER:
            wait_seconds = 3600 * 24  #longer times for lazy animals
            print('Longer time to enter!')

        if task == 'Automatic_Water': # We want to recover previous sessions parameters after this emergency water stage
            prev_session = df.loc[df['session'] == last_session - 2].iloc[-1]
            wait_seconds = 3600 * 5
            task = prev_session.task
            stage = float(prev_session.stage)
            substage = float(prev_session.substage)
            stim_dur_ds = float(prev_session.stim_dur_ds)
            stim_dur_dm = float(prev_session.stim_dur_dm)
            stim_dur_dl= float(prev_session.stim_dur_dl)

        elif task == 'Habituation':
            wait_seconds = 3600 * 1
            if len(df_last2.session.unique())>=2: # Pass after 2 sessions
                task = 'LickTeaching'

        elif task == 'LickTeaching':
            wait_seconds = 3600 * 2
            if n_trials > 55:
                task = 'TouchTeaching'

        elif task == 'TouchTeaching':
            if n_trials >= 50:
                task = 'StageTraining_RatB_V1'
                stage = float(1)
                substage = float(1)

        elif 'StageTraining' in task:
            ############################ FUNTIONS ############################
            def func(x):
                if x.last_valid_index() is None:
                    return None
                else:
                    return x[x.last_valid_index()]

            def variable_calc(variable, initial, final):
                "calculates the average between initial and final values of a changing variable"
                try:
                    init = df[variable].iloc[10]
                    fin = df[variable].iloc[-1]
                except:  # very short session, pick previous session value
                    try:
                        previous = df_last2.loc[df_last2['session'] < last_session].copy()
                        init = previous[variable].iloc[10]
                        fin = previous[variable].iloc[-1]
                    except:  # 2 very short sessions pick the easiest value
                        init = initial
                        fin = final
                average = (init + fin) / 2
                return (average, init)

            ############################ SMALL PARSING ############################

            #number of trials
            if n_trials < 15:
                if my_subject not in settings.INACTIVE_SUBJECTS:
                    telegram_bot.alarm_few_trials(n_trials, my_subject)

            # get first and last responses
            sort = df['response_x'].astype(str).str.split(',', expand=True) # separate reponses in columns
            df['first_resp'] = sort[0].astype(float)                        # select first reponses
            df['last_resp'] = sort.apply(func, axis=1).astype(float)        # select last reponses
            # useful columns
            df['first_error'] = df['first_resp'] - df['x']  # error calculation
            df['last_error'] = df['last_resp'] - df['x']
            df['first_correct_bool'] = np.where(df['correct_th'] >= df['first_error'].abs(), 1, 0)  # correct bool calc
            df['last_correct_bool'] = np.where(df['correct_th'] >= df['last_error'].abs(), 1, 0)
            df.loc[(df.trial_result == 'miss', ['first_correct_bool', 'last_correct_bool'])] = np.nan  # misses correction

            # last 3
            sort_last3 = df_last3['response_x'].astype(str).str.split(',', expand=True)
            df_last3['first_resp'] = sort_last3[0].astype(float)
            df_last3['last_resp'] = sort_last3.apply(func, axis=1).astype(float)
            df_last3['first_error'] = df_last3['first_resp'] - df_last3['x']
            df_last3['last_error'] = df_last3['last_resp'] - df_last3['x']
            df_last3['first_correct_bool'] = np.where(df_last3['correct_th'] >= df_last3['first_error'].abs(), 1, 0)
            df_last3['last_correct_bool'] = np.where(df_last3['correct_th'] >= df_last3['last_error'].abs(), 1, 0)

            # last 5
            sort_last5 = df_last5['response_x'].astype(str).str.split(',', expand=True)
            df_last5['first_resp'] = sort_last5[0].astype(float)
            df_last5['last_resp'] = sort_last5.apply(func, axis=1).astype(float)
            df_last5['first_error'] = df_last5['first_resp'] - df_last5['x']
            df_last5['last_error'] = df_last5['last_resp'] - df_last5['x']
            df_last5['last_correct_bool'] = np.where(df_last5['correct_th'] >= df_last5['last_error'].abs(), 1, 0)
            df_last5['first_correct_bool'] = np.where(df_last5['correct_th'] >= df_last5['first_error'].abs(), 1, 0)

            # last substages lists
            last3_stages = df_last3.stage.unique()
            last2_substages = df_last2.substage.unique()
            last3_substages = df_last3.substage.unique()
            last5_substages = df_last5.substage.unique()
            last14_substages = df_last14.substage.unique()

            # accuracies calc
            first_poke_acc = df.first_correct_bool.mean()
            last_poke_acc = df.last_correct_bool.mean()
            first3_poke_acc = df_last3.first_correct_bool.mean()
            last3_poke_acc = df_last3.last_correct_bool.mean()
            first5_poke_acc = df_last5.first_correct_bool.mean()
            last5_poke_acc = df_last5.last_correct_bool.mean()

            #subdataframes:
            vg_df = df.loc[df['trial_type'] == 'VG']
            ds_df = df.loc[((df['trial_type'] == 'DS') | (df['trial_type'] == 'DSc1') | (df['trial_type'] == 'DSc2'))]
            dm_df = df.loc[((df['trial_type'] == 'DM') | (df['trial_type'] == 'DMc1'))]
            dl_df = df.loc[((df['trial_type'] == 'DL'))]

            ############ STAGE 1 ############
            #Here last5_substages chanegd to last2_substages for the criteria to be 2 sessions rather than 5.
            if stage == 3:
                # Count the total number of trials where stage == 3
                last_row = df.iloc[-1]  # Get the last row of the DataFrame
                trial_counter = last_row['trial_counter']
                # Check if the total trials exceed or equal 4000
                if trial_counter >= 4000:
                    task = "Probability_Training_BB"
                    stage = 1
                    substage = 0
                    message = (f"Total trials in Stage 3 reached {trial_counter}. Moving to Probability task.")
                    trial_counter = 0
                    print(message)
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print("Telegram message not sent")
                        pass
            elif stage == 1:
                if substage == 1:
                    if last3_poke_acc >= 0.8 and len(last2_substages) == 1 and n_trials > 60:  # next substage
                        substage += 1
                    # elif n_trials <= 15 and len(last5_substages) == 1:  # go to Touchteaching
                    #     task = 'TouchTeaching'
                    #     stage -= 1
                    #     substage -= 1
                elif substage == 2:
                    stim_pos_acc = vg_df.groupby('x')['first_correct_bool'].mean() # accuracy by stimulus in VG trials
                    stim_pos_acc.to_list()
                    if all(i >= 0.7 for i in stim_pos_acc) and len(last2_substages) == 1 and n_trials > 60 and first3_poke_acc >0.65:  # next substage
                        substage += 1
                    elif first_poke_acc <= 0.33 and len(last3_substages) == 1:  # lower substage
                        substage -= 1
                elif substage == 3:
                    acc_ds = ds_df['first_correct_bool'].mean() # accuracy in delay short
                    if acc_ds >= 0.55 and len(last2_substages) == 1 and n_trials > 60 and first3_poke_acc >0.7:  # next stage
                        stage += 1
                        substage = float(1)
                        stim_dur_ds = 0.45
                    elif first_poke_acc < 0.35 and len(last3_substages) == 1 :  # lower substage
                        substage -= 1

            ############ STAGE 2 ############
            elif stage == 2:
                # Calculate subdataframes for the last 55 trials with the same substage
                #last_trials = 55  # Define the number of trials to consider
                last_trials = 55  # Define the number of trials to consider
                df_last_trials = df.tail(last_trials)  # Get the last `last_trials` rows of the dataframe

                # Check if all the trials in the last 55 rows have the same substage
                if df_last_trials['substage'].nunique() == 1:
                    # Proceed with the last 55 trials
                    message = (
                        f"All {last_trials} trials have the same substage: {df_last_trials['substage'].iloc[0]}"
                    )
                    print(message)
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass
                else:
                    # Filter to include only trials from the last substage
                    last_substage = df_last_trials['substage'].iloc[-1]  # Identify the last substage
                    df_last_trials = df_last_trials[df_last_trials['substage'] == last_substage]
                    message = (
                        f"The last {last_trials} trials have different substages. "
                        f"Filtering to include only substage {last_substage}."
                    )
                    print(message)
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

                # Check if stim_dur was modified in the last 55 trials
                recent_stim_dur_ds = df_last_trials['stim_dur_ds'].iloc[0] == df_last_trials['stim_dur_ds'].iloc[-1]
                recent_stim_dur_dm = df_last_trials['stim_dur_dm'].iloc[0] == df_last_trials['stim_dur_dm'].iloc[-1]
                recent_stim_dur_dl = df_last_trials['stim_dur_dl'].iloc[0] == df_last_trials['stim_dur_dl'].iloc[-1]

                # Subdataframes for each trial type
                ds_df = df_last_trials.loc[df_last_trials['trial_type'].isin(['DS', 'DSc1', 'DSc2'])]
                dm_df = df_last_trials.loc[df_last_trials['trial_type'].isin(['DM', 'DMc1'])]
                dl_df = df_last_trials.loc[df_last_trials['trial_type'] == 'DL']

                stim_dur_ds = df_last_trials['stim_dur_ds'].iloc[-1]
                stim_dur_dm = df_last_trials['stim_dur_dm'].iloc[-1]
                stim_dur_dl = df_last_trials['stim_dur_dl'].iloc[-1]

                if recent_stim_dur_ds == True and recent_stim_dur_dm == True and recent_stim_dur_dl == True:
                    message = (
                        f"Stimulus duration are same in last {last_trials} trials: "
                        f"stim_dur_ds={stim_dur_ds}, stim_dur_dm={stim_dur_dm}, stim_dur_dl={stim_dur_dl}."
                    )
                    print(message)
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass
                    next_stage = False

                    if substage == 1:
                        max_stim_dur = 0.45
                        #average, initial = variable_calc('stim_dur_ds', max_stim_dur, max_stim_dur)
                        initial = df_last_trials['stim_dur_ds'].iloc[-1]
                        acc = ds_df['first_correct_bool'].mean()
                        acc_up = 0.6
                        change = 0.15
                    elif substage ==2:
                        max_stim_dur = 0.4
                        #average, initial = variable_calc('stim_dur_dm', max_stim_dur, max_stim_dur)
                        initial = df_last_trials['stim_dur_dm'].iloc[-1]
                        acc = (dm_df['first_correct_bool'].mean() + ds_df['first_correct_bool'].mean())/2
                        acc_up = 0.55
                        change = 0.15
                    elif substage ==3:
                        max_stim_dur = 0.35
                        #average, initial = variable_calc('stim_dur_dl', max_stim_dur, max_stim_dur)
                        initial = df_last_trials['stim_dur_dl'].iloc[-1]
                        acc = (dl_df['first_correct_bool'].mean() + dm_df['first_correct_bool'].mean()) / 2
                        acc_up = 0.5
                        change = 0.15
                    # Check if accuracy is sufficient for advancement
                    if acc > acc_up and len(df_last_trials) == last_trials:
                        if initial >= change:
                            stim_dur = initial - change
                            message = f"Accuracy {acc:.2f} meets criteria. Adjusting stimulus duration from {initial} to {stim_dur}."
                            print(message)
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass
                        else:
                            stim_dur = 0
                            next_stage = True  # Advance to next substage if duration is already minimal
                            message = f"Accuracy {acc:.2f} meets criteria. Adjusting stimulus duration from {initial} to {stim_dur}."
                            print(message)
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass
                    else:
                        stim_dur = initial
                        message = f"Accuracy {acc:.2f} does not meet criteria. Keeping stimulus duration the same: {stim_dur}."
                        print(message)
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                        except:
                            print('Telegram message not sent')
                            pass
                    if substage == 1:  # stage 2 remain now in substage 1 ds 0
                        stim_dur_ds = stim_dur
                        if next_stage == True:
                            print("Advancing to Stage 2.2")
                            substage += 1
                            stim_dur_ds = 0
                            stim_dur_dm = 0.4
                    elif substage == 2:
                        stim_dur_dm = stim_dur
                        if next_stage == True:
                            print("Advancing to Stage 2.3")
                            substage += 1
                            stim_dur_dm = 0
                            stim_dur_dl = 0.35
                    elif substage == 3:
                        stim_dur_dl = stim_dur
                        if next_stage == True:
                            print("Advancing to Stage 3.1")
                            #if len(last14_substages) == 1:
                            stage += 1
                            substage = float(1)
                            stim_dur_dl = 0
                            message = 'WM: Advancing to Stage 3.1'
                            try:
                                telegram_bot.alarm_completed_criteria(task, my_subject)
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass

                    #Ensure that stim_duration is below 0:
                    stim_dur_ds = max(stim_dur_ds, 0)
                    stim_dur_dm = max(stim_dur_dm, 0)
                    stim_dur_dl = max(stim_dur_dl, 0)
                else:
                    print("Stimulus duration has already been modified recently. Skipping further adjustment.")
                    # Assign the last row's stim_dur values to skip further adjustment
                    stim_dur_ds = df_last_trials['stim_dur_ds'].iloc[-1]
                    stim_dur_dm = df_last_trials['stim_dur_dm'].iloc[-1]
                    stim_dur_dl = df_last_trials['stim_dur_dl'].iloc[-1]
                    message = (
                        f"Retaining stimulus durations: "
                        f"stim_dur_ds={stim_dur_ds}, stim_dur_dm={stim_dur_dm}, stim_dur_dl={stim_dur_dl}."
                    )
                    print(message)
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass


    elif 'Probability' in task:     #Includes all the task without the word Probability
        trial_criteria = 20
        accuracy_criteria = 0.85
        accuracy_moveback_criteria = 0.4

        if my_subject == 'm2':
            trial_criteria = 3
            accuracy_criteria = 0.5
            accuracy_moveback_criteria = 0.4


        # First: Identify the last session and second-to-last session:
        unique_sessions = sorted(df['session'].unique(), reverse=True)  # Sort sessions in descending order
        last_session = unique_sessions[0]  # The most recent session
        second_last_session = unique_sessions[1] if len(unique_sessions) > 1 else None  # The second most recent session
        third_last_session = unique_sessions[2] if len(unique_sessions) > 2 else None  # The third most recent session

        # Second: Filter the DataFrame to include only the last two sessions/three sessions
        df_last2 = df.loc[df['session'].isin([last_session, second_last_session])].copy()  # Last two sessions
        df_last_session = df.loc[df['session'] == last_session].copy()  # Only last session
        df_last3 = df.loc[df['session'].isin([last_session, second_last_session, third_last_session])].copy()  # Last three sessions

        # Third: Get the number of trials in the last session and second-to-last session (if exists)
        n_trials_last = df_last_session.trial.max()  # Trials in the last session
        if second_last_session is not None:
            df_second_last_session = df_last2[df_last2['session'] == second_last_session].copy()
            n_trials_second_last = df_second_last_session.trial.max()
        else:
            n_trials_second_last = 0

        if third_last_session is not None:
            df_third_last_session = df_last3[df_last3['session'] == third_last_session].copy()

        #Telegram message for low number of trials.
        if n_trials_last < 15:
            if my_subject not in settings.INACTIVE_SUBJECTS:
                telegram_bot.alarm_few_trials(n_trials_last, my_subject)

        # Fourth: Calculate accuracy for the last session and second last session (if exists)
        correct_trials_last = df_last_session[df_last_session['trial_result'].isin(['correct', 'correct_first'])].shape[
            0]
        valid_trials_last = df_last_session[df_last_session['trial_result'] != 'miss'].shape[0]
        message = f"Valid trials in session: {valid_trials_last}"
        print(f'{message}')
        try:
            telegram_bot.alarm_finish_session(message, my_subject)
        except:
            print('Telegram message not sent')
            pass
        accuracy_last = correct_trials_last / valid_trials_last if valid_trials_last > 0 else 0
        message = f"Accuracy in session: {accuracy_last * 100:.2f}%"
        print(f'{message}')
        try:
            telegram_bot.alarm_finish_session(message, my_subject)
        except:
            print('Telegram message not sent')
            pass

        # Calculate accuracy for the second-to-last session (if exists)
        if second_last_session is not None:
            correct_trials_second_last = df_second_last_session[df_second_last_session['trial_result'].isin(['correct', 'correct_first'])].shape[
            0]
            valid_trials_second_last = df_second_last_session[df_second_last_session['trial_result'] != 'miss'].shape[0]
            message = f"Valid trials in previous session: {valid_trials_second_last}"
            print(f'{message}')
            try:
                telegram_bot.alarm_finish_session(message, my_subject)
            except:
                print('Telegram message not sent')
                pass
            accuracy_second_last = correct_trials_second_last / valid_trials_second_last if valid_trials_second_last > 0 else 0
            message = f"Accuracy in previous session: {accuracy_second_last * 100:.2f}%"
            print(f'{message}')
            try:
                telegram_bot.alarm_finish_session(message, my_subject)
            except:
                print('Telegram message not sent')
                pass
        else:
            valid_trials_second_last = 0
            accuracy_second_last = 0
            print("No previous session available.")

        # Fifth: Check if the last session and second-to-last session are in different tasks
        last_session_task = df_last_session['task'].iloc[0]  # Stage in the last session
        second_last_session_task = df_second_last_session['task'].iloc[0] if second_last_session is not None else None
        third_last_session_task = df_third_last_session['task'].iloc[0] if third_last_session is not None else None

        # Sixth: Check if the last session and second-to-last session are in different stages
        last_session_stage = df_last_session['stage'].iloc[0]  # Stage in the last session
        second_last_session_stage = df_second_last_session['stage'].iloc[0] if second_last_session is not None else None
        third_last_session_stage = df_third_last_session['stage'].iloc[0] if third_last_session is not None else None

        # Seventh: Check if the last session and second-to-last session are in different substages
        last_session_substage = df_last_session['substage'].iloc[0]  # Substage in the last session
        second_last_session_substage = df_second_last_session['substage'].iloc[0] if second_last_session is not None else None
        third_last_session_substage = df_third_last_session['substage'].iloc[0] if third_last_session is not None else None

        # Eight: Check if the last session and second-to-last session are in different substages_bias for bias breaking in Extra training only:
        last_session_substage_bias = df_last_session['substage_bias'].iloc[0]  # Substage for bias breaking in the last session
        second_last_session_substage_bias = df_second_last_session['substage_bias'].iloc[0] if second_last_session is not None else None
        third_last_session_substage_bias = df_third_last_session['substage_bias'].iloc[0] if third_last_session is not None else None

        # Condition for shifting them to normal task after demotivation, moves them after three sessions in demotivation task.
        if task == 'Probability_Training_BB_Demotivation':
            # Ensure the last three sessions were all 'Probability_Training_Demotivation'
            last_three_sessions_tasks = df_last3['task'].unique()
            if len(df_last3.session.unique()) >= 3 and len(last_three_sessions_tasks) == 1 and last_three_sessions_tasks[0] == 'Probability_Training_BB_Demotivation':
                task = 'Probability_Training_BB'
                print("Moved from demotivation task to normal task")

        elif 'Probability_Extra_Training_Bias' in task:
            if last_session_task == second_last_session_task:
                if last_session_stage == second_last_session_stage:
                    if last_session_substage == second_last_session_substage:
                        if last_session_substage_bias == 1 and second_last_session_substage_bias == 1:
                            if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                                valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                                substage_bias = 2
                                message = f'Advancing from substage_bias 1 to substage_bias 2'
                                print(f'{message}')
                                try:
                                    telegram_bot.alarm_finish_session(message, my_subject)
                                except:
                                    print('Telegram message not sent')
                                    pass
                        elif last_session_substage_bias == 2 and second_last_session_substage_bias == 2:
                            if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                                valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                                substage_bias = 3
                                message = f'Advancing from substage_bias 2 to substage_bias 3'
                                print(f'{message}')
                                try:
                                    telegram_bot.alarm_finish_session(message, my_subject)
                                except:
                                    print('Telegram message not sent')
                                    pass
                        elif last_session_substage_bias == 3 and second_last_session_substage_bias == 3:
                                if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                                    valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                                    # Increment substage until it reaches 2
                                    while substage < 2:
                                        substage += 1
                                        message = f'Advancing to substage {substage}'
                                        print(f'{message}')
                                        try:
                                            telegram_bot.alarm_finish_session(message, my_subject)
                                        except:
                                            print('Telegram message not sent')
                                            pass

                                    # When substage reaches 2, update task, substage_bias, and substage
                                    if substage == 2:
                                        if 'Probability_Extra_Training_Bias_Left_Correction' in task:
                                            task = "Probability_Extra_Training_Bias_Left"
                                            substage_bias = 3
                                            substage = 2
                                            message = f'Substage is now 2, task changed to {task}, substage_bias reset to 3'
                                            print(f'{message}')
                                            try:
                                                telegram_bot.alarm_finish_session(message, my_subject)
                                                telegram_bot.alarm_completed_criteria(task, my_subject)
                                            except:
                                                print('Telegram message not sent')
                                                pass
                                        else:
                                            task = "Probability_Extra_Training"
                                            substage_bias = 0
                                            substage = 3
                                            message = f'Substage is now 3, task changed to {task}, substage_bias reset to 0'
                                            print(f'{message}')
                                            try:
                                                telegram_bot.alarm_finish_session(message, my_subject)
                                                telegram_bot.alarm_completed_criteria(task, my_subject)
                                            except:
                                                print('Telegram message not sent')
                                                pass


        elif 'Probability_Training_Bias' in task:
            if last_session_task == second_last_session_task:
                if last_session_stage == second_last_session_stage:
                    if last_session_substage == 1 and second_last_session_substage == 1:
                            if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                                valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                                substage = 2
                                message = 'PI: Advancing from substage 1 to substage 2'
                                print(f'{message}')
                                try:
                                    ttelegram_bot.alarm_finish_session(message, my_subject)
                                except:
                                    print('Telegram message not sent')
                                    pass
                    elif last_session_substage == 2 and second_last_session_substage == 2:
                            if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                                valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                                task = 'Probability_Training_BB'
                                substage = 0
                                message = 'PI: Advancing from substage 2 to normal task'
                                print(f'{message}')
                                try:
                                    telegram_bot.alarm_finish_session(message, my_subject)
                                    telegram_bot.alarm_completed_criteria(task, my_subject)
                                except:
                                    print('Telegram message not sent')
                                    pass

            # Check for move-back criteria using the function
            if len(unique_sessions) >= 3:
                if last_session_task == second_last_session_task == third_last_session_task:
                    if last_session_stage == second_last_session_stage == third_last_session_stage:
                        if last_session_stage == second_last_session_stage == third_last_session_stage:
                            if last_session_substage == second_last_session_substage == third_last_session_substage:
                                sessions = [last_session, second_last_session, third_last_session]
                                low_trial_count, low_accuracy_count = calculate_move_back_criteria(
                                    df_last3, sessions, trial_criteria, accuracy_moveback_criteria
                                )

                                # Apply move-back logic if all three sessions fail the criteria
                                if low_trial_count == 3 or low_accuracy_count == 3:
                                    print("Move-back criteria met. Moving back one substage.")
                                    substage = max(substage - 1, 1)  # Ensure stage doesn't go below 1
                                    message = f"PI: Subject moved back one stage due to low performance. Substage: {substage}"
                                    print(f'{message}')
                                    try:
                                        telegram_bot.alarm_finish_session(message, my_subject)
                                    except Exception as e:
                                        print(f"Telegram message not sent: {e}")


        elif task == 'Probability_Extra_Training':
            if last_session_task == second_last_session_task:
                if last_session_stage == 1 and second_last_session_stage == 1:
                    if last_session_substage == 1 and second_last_session_substage == 1:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.1 to stage 1.2')
                            stage = 1
                            substage = 2
                            message = 'PI: Advancing from stage 1 to stage 2'
                            print(f'{message}')
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass
                    elif last_session_substage == 2 and second_last_session_substage == 2:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.2 to 1.3')
                            stage = 1
                            substage = 3
                            message = 'PI: Advancing from stage 1 to stage 2'
                            print(f'{message}')
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass
                    elif last_session_substage == 3 and second_last_session_substage == 3:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.3 to 1.4')
                            stage = 1
                            substage = 4
                            message = 'PI: Advancing from stage 1 to stage 2'
                            print(f'{message}')
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass
                    elif last_session_substage == 4 and second_last_session_substage == 4:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.4 to 1.5')
                            stage = 1
                            substage = 5
                            message = 'PI: Advancing from stage 1 to stage 2'
                            print(f'{message}')
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass
                    elif last_session_substage == 5 and second_last_session_substage == 5:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            task = 'Probability_Training_BB'
                            stage = 2
                            substage = 0
                            message = 'PI: Advancing to Probability_Training_BB to stage 2'
                            print(f'{message}')
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                                telegram_bot.alarm_completed_criteria(task, my_subject)
                            except:
                                print('Telegram message not sent')
                                pass


        elif 'Probability_Training_BB' in task:
            # Check stage-specific conditions for advancement
            if last_session_task == second_last_session_task:
                # Stage 1 -> Stage 2 check
                if last_session_stage == 1 and second_last_session_stage == 1:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        stage = 2
                        message = 'PI: Advancing from stage 1 to stage 2'
                        print(f'{message}')
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                        except:
                            print('Telegram message not sent')
                            pass
                # Stage 2 -> Stage 3 check
                elif last_session_stage == 2 and second_last_session_stage == 2:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        stage = 3
                        message = 'PI: Advancing from stage 2 to stage 3'
                        print(f'{message}')
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                        except:
                            print('Telegram message not sent')
                            pass
                elif last_session_stage == 3 and second_last_session_stage == 3:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        stage = 4
                        message = 'PI: Advancing from stage 3 to stage 4'
                        print(f'{message}')
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                        except:
                            print('Telegram message not sent')
                            pass
                # Stage 3 -> Weber's Law
                elif last_session_stage == 4 and second_last_session_stage == 4:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        message = 'PI: Advance from stage 3 to Webers Law with accuracy in both sessions'
                        print(f'{message}')
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                            telegram_bot.alarm_completed_criteria(task, my_subject)
                        except:
                            print('Telegram message not sent')
                            pass
                        stage = 4
                        task = 'Probability_WebersLaw'
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

            # Check for move-back criteria using the function
            if len(unique_sessions) >= 3:
                if last_session_task == second_last_session_task == third_last_session_task:
                    if last_session_stage == second_last_session_stage == third_last_session_stage:
                        sessions = [last_session, second_last_session, third_last_session]
                        low_trial_count, low_accuracy_count = calculate_move_back_criteria(
                            df_last3, sessions, trial_criteria, accuracy_moveback_criteria
                        )

                        # Apply move-back logic if all three sessions fail the criteria
                        if low_trial_count == 3 or low_accuracy_count == 3:
                            print("Move-back criteria met. Moving back one stage.")
                            stage = max(stage - 1, 1)  # Ensure stage doesn't go below 1
                            message = f"PI: Subject moved back one stage due to low performance. Stage: {stage}"
                            print(f'{message}')
                            try:
                                telegram_bot.alarm_finish_session(message, my_subject)
                            except Exception as e:
                                print(f"Telegram message not sent: {e}")


        elif 'Probability_WebersLaw' in task:
            last_row = df.iloc[-1]  # Get the last row of the DataFrame
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
                task = 'Probability_WL_Training'
                # Weber's Law:
                stage = 5
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

                #Weber's Law Training Variables:
                ror = [16.0, 12.0, 8.0, 6.0, 4.0, 2.0, 1.5]
                completed_ror = []
                current_ror = 16.0
                trial_counter_ror = 0

                message = 'PI: Probability_WebersLaw completes, Moving to Webers law Training.'
                print(f'{message}')
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass


        elif 'Probability_WL_Training' in task:
            if task == 'Probability_WL_Training':
                trial_criteria = 72
                accuracy_criteria = 0.70
                trial_end_criteria = 1500

                if my_subject == 'm2':
                    trial_criteria = 5
                    accuracy_criteria = 0.7
                    trial_end_criteria = 1000

                ror_to_conditions = {
                    16.0: [16, 15],
                    12.0: [14, 13],
                    8.0: [12, 11],
                    6.0: [10, 9],
                    4.0: [8, 7],
                    2.0: [6, 5],
                    1.5: [4, 3],
                }

                last_row = df.iloc[-1]  # Get the last row of the DataFrame

                # Check if the last session and second-to-last session are in different rors:
                last_session_ror = df_last_session['current_ror'].iloc[0]  # Stage in the last session
                second_last_session_ror = df_second_last_session['current_ror'].iloc[0] if second_last_session is not None else None

                # Assign each value from the last row to the variables:
                ror = last_row['ror']
                completed_ror = last_row['completed_ror']
                current_ror = last_row['current_ror']
                trial_counter_ror = last_row['trial_counter_ror']

                if trial_counter_ror >= trial_end_criteria:
                    task = 'Probability_WL_Training_Runthrough'
                    # Ensure completed_ror is a proper list
                    if isinstance(completed_ror, str):
                        completed_ror = str_to_list(completed_ror)
                    ror = completed_ror
                    completed_ror = []
                    current_ror = 16.0
                    trial_counter_ror = 0
                    stage = 5
                    substage = 0
                    trial_counter = 0
                    message = f"{trial_end_criteria} trials completed in ROR {current_ror}. Task ended."
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

                elif last_session_task == second_last_session_task:
                    # Update the logic to use trial_condition
                    if last_session_ror == second_last_session_ror:
                        # Allowed trial_conditions for the current ROR
                        allowed_conditions_last = ror_to_conditions.get(last_session_ror, [])
                        allowed_conditions_second_last = ror_to_conditions.get(second_last_session_ror, [])
                        print(f"Current ROR: {last_session_ror}, Allowed Conditions: {allowed_conditions_last}")
                        print(f"Second Last ROR: {second_last_session_ror}, Allowed Conditions: {allowed_conditions_second_last}")

                        # Filter for the specific trial_condition in the last session and calculate accuracy and
                        last_condition_trials = df_last_session[df_last_session['trial_condition'].isin(allowed_conditions_last)]
                        correct_trials_last = last_condition_trials[last_condition_trials['trial_result'] == 'correct'].shape[0]
                        valid_trials_last = last_condition_trials[last_condition_trials['trial_result'] != 'miss'].shape[0]
                        accuracy_last = correct_trials_last / valid_trials_last if valid_trials_last > 0 else 0
                        print(f"Accuracy for last session in trial_condition: {accuracy_last * 100:.2f}%")

                        # Filter for the specific trial_condition in the second last session
                        if second_last_session is not None:
                            second_last_condition_trials = df_second_last_session[df_second_last_session['trial_condition'].isin(allowed_conditions_second_last)]
                            correct_trials_second_last = second_last_condition_trials[second_last_condition_trials['trial_result'] == 'correct'].shape[0]
                            valid_trials_second_last = second_last_condition_trials[second_last_condition_trials['trial_result'] != 'miss'].shape[0]
                            accuracy_second_last = correct_trials_second_last / valid_trials_second_last if valid_trials_second_last > 0 else 0
                            print(f"Accuracy for second last session in trial_condition: {accuracy_second_last * 100:.2f}%")
                        else:
                            accuracy_second_last = 0
                            print("No second last session available.")

                        total_trials = valid_trials_last + valid_trials_second_last

                        message = (
                            f"Last Session ROR: {last_session_ror}\n"
                            f"Second Last Session ROR: {second_last_session_ror}\n"
                            f"Total Trials in last two sessions: {total_trials}\n"
                            f"Total trials in current ROR: {trial_counter_ror}"
                        )
                        print(message)
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                        except Exception as e:
                            print('Telegram message not sent:', e)
                            pass

                        if ((total_trials >= trial_criteria and accuracy_last >= accuracy_criteria and accuracy_second_last >= accuracy_criteria)
                                or (trial_counter_ror >= trial_end_criteria)):
                            # Move the current_ror to completed_ror
                            completed_ror = str_append(completed_ror, current_ror)  # Append using str_append
                            trial_counter_ror = 0
                            # Move to the next ror, if any are left
                            if ror != "[]" and ror:  # Check if ror is not empty
                                ror, current_ror = str_pop(ror)  # Use str_pop to remove the first ROR
                                if ror != "[]" and ror:
                                    current_ror = ror[1:-1].split(", ")[0]  # Get the first ROR
                                    # Create a message indicating the change in current_ror
                                    message = (
                                        f"Current ROR has been updated.\n"
                                        f"Remaining ROR: {ror}\n"
                                        f"New Current ROR: {current_ror}\n"
                                        f"Completed RORs: {completed_ror}"
                                    )
                                    print(message)
                                    try:
                                        telegram_bot.alarm_finish_session(message, my_subject)
                                    except Exception as e:
                                        print('Telegram message not sent:', e)
                                        pass
                                else:
                                    print("All RORs are completed. Task ends.")
                                    current_ror = 0
                                    #task = 'Probability_Turtle_Training'
                                    stage = 6
                                    substage = 0
                                    trial_counter = 0
                                    message = 'PI: Webers law Training completed'
                                    print(f'{message}')
                                    try:
                                        telegram_bot.alarm_finish_session(message, my_subject)
                                        telegram_bot.alarm_completed_criteria(task, my_subject)
                                    except:
                                        print('Telegram message not sent')
                                        pass
                            else:
                                message = (
                                    f"Criteria not met.\n"
                                    f"Current ROR not updated.\n"
                                    f"Current ROR: {current_ror}\n"
                                    f"Completed RORs: {completed_ror}"
                                )
                                print(message)
                                try:
                                    telegram_bot.alarm_finish_session(message, my_subject)
                                except Exception as e:
                                    print('Telegram message not sent:', e)
                                    pass

                # Ensure current_ror is an integer after processing
                if isinstance(current_ror, str):
                    current_ror = float(current_ror)  # Convert to int if it's a string
                    print(f"current_ror converted to int: {current_ror}")

                # Convert ror and completed_ror to lists using isinstance
                if isinstance(ror, str):
                    ror = str_to_list(ror)
                    print(f"Converted ror to list: {ror}")

                if isinstance(completed_ror, str):
                    completed_ror = str_to_list(completed_ror)
                    print(f"Converted completed_ror to list: {completed_ror}")

            elif task == 'Probability_WL_Training_Runthrough':
                trial_criteria = 72
                accuracy_criteria = 0.70
                trial_end_criteria = 1500

                if my_subject == 'm2':
                    trial_criteria = 3
                    accuracy_criteria = 0.5
                    trial_end_criteria = 10

                ror_to_conditions = {
                    16.0: [16, 15],
                    12.0: [14, 13],
                    8.0: [12, 11],
                    6.0: [10, 9],
                    4.0: [8, 7],
                    2.0: [6, 5],
                    1.5: [4, 3],
                }

                last_row = df.iloc[-1]  # Get the last row of the DataFrame

                # Check if the last session and second-to-last session are in different rors:
                last_session_ror = df_last_session['current_ror'].iloc[0]  # Stage in the last session
                second_last_session_ror = df_second_last_session['current_ror'].iloc[
                    0] if second_last_session is not None else None

                # Assign each value from the last row to the variables:
                ror = last_row['ror']
                completed_ror = last_row['completed_ror']
                current_ror = last_row['current_ror']
                trial_counter_ror = last_row['trial_counter_ror']

                trial_message_criteria = 216

                if trial_counter_ror >= trial_message_criteria:
                    message = f"{trial_message_criteria} trials completed in ROR {current_ror}. Check Data."
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

                if trial_counter_ror >= trial_end_criteria:
                    ror = []
                    completed_ror = []
                    current_ror = 0
                    trial_counter_ror = 0
                    # task = 'Probability_Turtle_Training'
                    stage = 6
                    substage = 0
                    trial_counter = 0
                    message = f"{trial_end_criteria} trials completed in ROR {current_ror}. Task ended."
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass

                elif last_session_task == second_last_session_task:
                    # Update the logic to use trial_condition
                    if last_session_ror == second_last_session_ror:
                        # Allowed trial_conditions for the current ROR
                        allowed_conditions_last = ror_to_conditions.get(last_session_ror, [])
                        allowed_conditions_second_last = ror_to_conditions.get(second_last_session_ror, [])
                        print(f"Current ROR: {last_session_ror}, Allowed Conditions: {allowed_conditions_last}")
                        print(
                            f"Second Last ROR: {second_last_session_ror}, Allowed Conditions: {allowed_conditions_second_last}")

                        # Filter for the specific trial_condition in the last session and calculate accuracy and
                        last_condition_trials = df_last_session[
                            df_last_session['trial_condition'].isin(allowed_conditions_last)]
                        correct_trials_last = \
                        last_condition_trials[last_condition_trials['trial_result'] == 'correct'].shape[0]
                        valid_trials_last = \
                        last_condition_trials[last_condition_trials['trial_result'] != 'miss'].shape[0]
                        accuracy_last = correct_trials_last / valid_trials_last if valid_trials_last > 0 else 0
                        print(f"Accuracy for last session in trial_condition: {accuracy_last * 100:.2f}%")

                        # Filter for the specific trial_condition in the second last session
                        if second_last_session is not None:
                            second_last_condition_trials = df_second_last_session[
                                df_second_last_session['trial_condition'].isin(allowed_conditions_second_last)]
                            correct_trials_second_last = second_last_condition_trials[
                                second_last_condition_trials['trial_result'] == 'correct'].shape[0]
                            valid_trials_second_last = \
                            second_last_condition_trials[second_last_condition_trials['trial_result'] != 'miss'].shape[
                                0]
                            accuracy_second_last = correct_trials_second_last / valid_trials_second_last if valid_trials_second_last > 0 else 0
                            print(
                                f"Accuracy for second last session in trial_condition: {accuracy_second_last * 100:.2f}%")
                        else:
                            accuracy_second_last = 0
                            print("No second last session available.")

                        total_trials = valid_trials_last + valid_trials_second_last

                        message = (
                            f"Last Session ROR: {last_session_ror}\n"
                            f"Second Last Session ROR: {second_last_session_ror}\n"
                            f"Total Trials in last two sessions: {total_trials}\n"
                            f"Total trials in current ROR: {trial_counter_ror}"
                        )
                        print(message)
                        try:
                            telegram_bot.alarm_finish_session(message, my_subject)
                        except Exception as e:
                            print('Telegram message not sent:', e)
                            pass

                        if ((
                                total_trials >= trial_criteria and accuracy_last >= accuracy_criteria and accuracy_second_last >= accuracy_criteria)
                                or (trial_counter_ror >= trial_end_criteria)):
                            # Move the current_ror to completed_ror
                            completed_ror = str_append(completed_ror, current_ror)  # Append using str_append
                            trial_counter_ror = 0
                            # Move to the next ror, if any are left
                            if ror != "[]" and ror:  # Check if ror is not empty
                                ror, current_ror = str_pop(ror)  # Use str_pop to remove the first ROR
                                if ror != "[]" and ror:
                                    current_ror = ror[1:-1].split(", ")[0]  # Get the first ROR
                                    # Create a message indicating the change in current_ror
                                    message = (
                                        f"Current ROR has been updated.\n"
                                        f"Remaining ROR: {ror}\n"
                                        f"New Current ROR: {current_ror}\n"
                                        f"Completed RORs: {completed_ror}"
                                    )
                                    print(message)
                                    try:
                                        telegram_bot.alarm_finish_session(message, my_subject)
                                    except Exception as e:
                                        print('Telegram message not sent:', e)
                                        pass
                                else:
                                    print("All RORs are completed. Task ends.")
                                    current_ror = 0
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
                                    substage = 0
                                    message = 'PI: Webers law Training completed. Move to Probability_WebersLaw_Post'
                                    print(f'{message}')
                                    try:
                                        telegram_bot.alarm_finish_session(message, my_subject)
                                        telegram_bot.alarm_completed_criteria(task, my_subject)
                                    except:
                                        print('Telegram message not sent')
                                        pass
                            else:
                                message = (
                                    f"Criteria not met.\n"
                                    f"Current ROR not updated.\n"
                                    f"Current ROR: {current_ror}\n"
                                    f"Completed RORs: {completed_ror}"
                                )
                                print(message)
                                try:
                                    telegram_bot.alarm_finish_session(message, my_subject)
                                except Exception as e:
                                    print('Telegram message not sent:', e)
                                    pass

                # Ensure current_ror is an integer after processing
                if isinstance(current_ror, str):
                    current_ror = float(current_ror)  # Convert to int if it's a string
                    print(f"current_ror converted to int: {current_ror}")

                # Convert ror and completed_ror to lists using isinstance
                if isinstance(ror, str):
                    ror = str_to_list(ror)
                    print(f"Converted ror to list: {ror}")

                if isinstance(completed_ror, str):
                    completed_ror = str_to_list(completed_ror)
                    print(f"Converted completed_ror to list: {completed_ror}")

        elif 'Probability_Turtle_Training' in task:
            trial_criteria = 30
            accuracy_criteria = 0.80
            trial_end_criteria = 3000

            if my_subject == 'm2':
                trial_criteria = 3
                accuracy_criteria = 0.7
                trial_end_criteria = 10

            last_row = df.iloc[-1]  # Get the last row of the DataFrame
            trial_counter = last_row['trial_counter']

            if trial_counter >= trial_end_criteria:
                stage = 7
                message = f"{trial_end_criteria} trials completed in substage {substage}. Task ended."
                print(f'{message}')
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                    telegram_bot.alarm_completed_criteria(task, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

            if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria):
                # Move to the next stage up to stage 3
                if substage < 3:
                    substage += 1
                    trial_counter = 0
                    message = (f"Moving to stage {substage} due to 80% accuracy in a session of {valid_trials_last} trials.")
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass
                else:
                    stage = 7
                    #task = 'Probability_Turtle_Test'
                    message = (f"Last substage {substage} completed, Training complete")
                    print(f'{message}')
                    try:
                        telegram_bot.alarm_finish_session(message, my_subject)
                        telegram_bot.alarm_completed_criteria(task, my_subject)
                    except:
                        print('Telegram message not sent')
                        pass
            else:
                message = ("Criteria for moving to the next stage not met.")
                print(f'{message}')
                try:
                    telegram_bot.alarm_finish_session(message, my_subject)
                except:
                    print('Telegram message not sent')
                    pass

    elif task == 'Water_Filler':
        print("rat drank water")
        # # variables by default
        # stage = 5
        # substage = 0
        # choice = 0
        # wait_seconds = 3600 * settings.TIME_TO_ENTER  # wait a minimum of x hours before allowed to start the new session)
        # stim_dur_ds = 0
        # stim_dur_dm = 0
        # stim_dur_dl = 0
        # # Weber's Law:
        # block = 0
        # conditions = []  # Takes the conditions from task file after first session.
        # completed_conditions = []  # To store completed conditions
        # current_condition = 0  # To track the current condition in progress
        # repetition = 0
        # current_repetition = 0  # To store how many times the condition has repeated.
        # trial_counter = 0  # Track the number of trials for the current condition.
        # # Image output stims:
        # stim_trial = 0
        # stim_trials = []
        # stim_trial_counter = 0

    if my_subject == 'm2':
        wait_seconds = 1

    return task, stage, substage, substage_bias, wait_seconds, stim_dur_ds, stim_dur_dm, stim_dur_dl, choice, block, conditions, completed_conditions, current_condition, repetition, current_repetition, trial_counter, stim_trial, stim_trials, stim_trial_counter, ror, completed_ror, current_ror, trial_counter_ror


def str_append(my_str: str, value: str) -> str:
    """Simulate appending a value to a string representation of a list."""
    my_str = my_str.strip()  # Ensure no leading/trailing spaces
    if my_str == "[]" or not my_str:  # If empty list, add value directly
        return f"[{value}]"
    return my_str[:-1] + f", {value}]"  # Insert value before the closing bracket


def str_pop(my_str: str) -> tuple[str, str]:
    """Simulate popping the first value from a string representation of a list."""
    my_str = my_str.strip()  # Ensure no leading/trailing spaces
    if my_str == "[]" or not my_str:  # Handle empty list
        raise ValueError("Cannot pop from an empty list")

    # Remove the brackets and split by commas
    parts = my_str[1:-1].split(", ")
    popped_value = parts.pop(0)  # Remove the first element
    new_str = f"[{', '.join(parts)}]"  # Reconstruct the string
    return new_str, popped_value

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

