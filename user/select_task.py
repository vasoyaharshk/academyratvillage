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
    choice = 0
    wait_seconds = 3600 * settings.TIME_TO_ENTER  # wait a minimum of x hours before allowed to start the new session)
    stim_dur_ds= 0
    stim_dur_dm= 0
    stim_dur_dl= 0
    #Weber's Law:
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
        #VERY IMPORTANT, THE ABOVE LINE IS COMMENTED OUT BECAUSE WE WANT THE DF TO REMAIN THE SUBJECT'S ALL SESSIONS INSTEAD OF JUST LAST AS
        #WE WANT TO GET LAST 55 TRIALS FOR THE CRITERIA CHANGED.

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
                #my_subject = df.subject.iloc[0]
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

            # subdataframes
            # vg_df = df.loc[df['trial_type'] == 'VG']
            # ds_df = df.loc[((df['trial_type'] == 'DS') | (df['trial_type'] == 'DSc1') | (df['trial_type'] == 'DSc2'))]
            # dm_df = df.loc[((df['trial_type'] == 'DM') | (df['trial_type'] == 'DMc1'))]
            # dl_df = df.loc[((df['trial_type'] == 'DL'))]

            # Calculate subdataframes for the last 55 trials
            last_trials = 55  # Define the number of trials to consider
            df_last_trials = df.tail(last_trials)  # Get the last `last_trials` rows of the dataframe

            # Subdataframes for each trial type
            vg_df = df_last_trials.loc[df_last_trials['trial_type'] == 'VG']
            ds_df = df_last_trials.loc[df_last_trials['trial_type'].isin(['DS', 'DSc1', 'DSc2'])]
            dm_df = df_last_trials.loc[df_last_trials['trial_type'].isin(['DM', 'DMc1'])]
            dl_df = df_last_trials.loc[df_last_trials['trial_type'] == 'DL']

            ############ STAGE 1 ############
            #Here last5_substages chanegd to last2_substages for the criteria to be 2 sessions rather than 5.
            if stage == 1:
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
                next_stage = False

                if substage == 1:
                    max_stim_dur = 0.45
                    average, initial = variable_calc('stim_dur_ds', max_stim_dur, max_stim_dur)
                    acc = ds_df['first_correct_bool'].mean()
                    acc_up = 0.6
                    change = 0.15
                elif substage ==2:
                    max_stim_dur = 0.4
                    average, initial = variable_calc('stim_dur_dm', max_stim_dur, max_stim_dur)
                    acc = (dm_df['first_correct_bool'].mean() + ds_df['first_correct_bool'].mean())/2
                    acc_up = 0.55
                    change = 0.15
                elif substage ==3:
                    max_stim_dur = 0.35
                    average, initial = variable_calc('stim_dur_dl', max_stim_dur, max_stim_dur)
                    acc = (dl_df['first_correct_bool'].mean() + dm_df['first_correct_bool'].mean()) / 2
                    acc_up = 0.5
                    change = 0.15

                # Check if accuracy is sufficient for advancement
                if acc > acc_up and len(df_last_trials) == last_trials:
                    print(f"Accuracy {acc:.2f} meets criteria. Adjusting stimulus duration.")
                    if initial >= change:
                        stim_dur = initial - change
                    else:
                        stim_dur = 0
                        next_stage = True  # Advance to next substage if duration is already minimal
                else:
                    print(f"Accuracy {acc:.2f} does not meet criteria. Keeping stimulus duration.")
                    stim_dur = initial

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

                #Ensure that stim_duration is below 0:
                stim_dur_ds = max(stim_dur_ds, 0)
                stim_dur_dm = max(stim_dur_dm, 0)
                stim_dur_dl = max(stim_dur_dl, 0)


    elif 'Probability' in task:     #Includes all the task without the word Probability
        trial_criteria = 20
        accuracy_criteria = 0.85

        if my_subject == 'm2':
            trial_criteria = 2
            accuracy_criteria = 0.5

        # Identify the last session and second-to-last session
        unique_sessions = sorted(df['session'].unique(), reverse=True)  # Sort sessions in descending order
        last_session = unique_sessions[0]  # The most recent session
        second_last_session = unique_sessions[1] if len(unique_sessions) > 1 else None  # The second most recent session
        third_last_session = unique_sessions[2] if len(unique_sessions) > 2 else None  # The third most recent session

        # Filter the DataFrame to include only the last two sessions
        df_last2 = df.loc[df['session'].isin([last_session, second_last_session])].copy()  # Last two sessions
        df_last_session = df.loc[df['session'] == last_session].copy()  # Only last session
        df_last3 = df.loc[df['session'].isin([last_session, second_last_session, third_last_session])].copy()  # Last three sessions

        #Get the number of trials in the last session and second-to-last session (if exists)
        n_trials_last = df_last_session.trial.max()  # Trials in the last session
        if second_last_session is not None:
            df_second_last_session = df_last2[df_last2['session'] == second_last_session].copy()
            n_trials_second_last = df_second_last_session.trial.max()
        else:
            n_trials_second_last = 0

        # number of trials
        if n_trials_last < 15:
            #my_subject = df.subject.iloc[0]
            if my_subject not in settings.INACTIVE_SUBJECTS:
                telegram_bot.alarm_few_trials(n_trials_last, my_subject)

        # Calculate accuracy for the last session
        correct_trials_last = df_last_session[df_last_session['trial_result'] == 'correct'].shape[0]
        valid_trials_last = df_last_session[df_last_session['trial_result'] != 'miss'].shape[0]
        print("Valid trials in session: ", valid_trials_last)
        accuracy_last = correct_trials_last / valid_trials_last if valid_trials_last > 0 else 0
        print(f"Accuracy in session: {accuracy_last * 100:.2f}%")

        # Condition for shifting them to normal task after demotivation, moves them after three sessions in demotivation task.
        if task == 'Probability_Training_Demotivation':
            # Ensure the last three sessions were all 'Probability_Training_Demotivation'
            if task == 'Probability_Training_Demotivation':
                # Ensure the last three sessions were all 'Probability_Training_Demotivation'
                last_three_sessions_tasks = df_last3['task'].unique()
                if len(df_last3.session.unique()) >= 3 and len(last_three_sessions_tasks) == 1 and last_three_sessions_tasks[0] == 'Probability_Training_Demotivation':
                    task = 'Probability_Training_BB'
                    print("Moved from demotivation task to normal task")

        # Calculate accuracy for the second-to-last session (if exists)
        if second_last_session is not None:
            correct_trials_second_last = df_second_last_session[df_second_last_session['trial_result'] == 'correct'].shape[0]
            valid_trials_second_last = df_second_last_session[df_second_last_session['trial_result'] != 'miss'].shape[0]
            print("Valid trials in previous session: ", valid_trials_second_last)
            accuracy_second_last = correct_trials_second_last / valid_trials_second_last if valid_trials_second_last > 0 else 0
            print(f"Accuracy in previous session: {accuracy_second_last * 100:.2f}%")
        else:
            valid_trials_second_last = 0
            accuracy_second_last = 0
            print("No previous session available.")

        # Check if the last session and second-to-last session are in different stages
        last_session_task = df_last_session['task'].iloc[0]  # Stage in the last session
        second_last_session_task = df_second_last_session['task'].iloc[0] if second_last_session is not None else None

        # Check if the last session and second-to-last session are in different stages
        last_session_stage = df_last_session['stage'].iloc[0]  # Stage in the last session
        second_last_session_stage = df_second_last_session['stage'].iloc[0] if second_last_session is not None else None

        # Check if the last session and second-to-last session are in different substages
        last_session_substage_stage = df_last_session['substage'].iloc[0]  # Stage in the last session
        second_last_session_substage_stage = df_second_last_session['substage'].iloc[0] if second_last_session is not None else None

        if 'Probability_Training_Bias' in task:
            if last_session_task == second_last_session_task:
                if last_session_stage == 1 and second_last_session_stage == 1:
                    if last_session_substage_stage == 1 and second_last_session_substage_stage == 1:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.1 to stage 1.2')
                            stage = 1
                            substage = 2
                    elif last_session_substage_stage == 2 and second_last_session_substage_stage == 2:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.2 to normal task')
                            task = 'Probability_Training_BB'
                            stage = 1
                            substage = 0

        elif 'Probability_Extra_Training' in task:
            if last_session_task == second_last_session_task:
                if last_session_stage == 1 and second_last_session_stage == 1:
                    if last_session_substage_stage == 1 and second_last_session_substage_stage == 1:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.1 to stage 1.2')
                            stage = 1
                            substage = 2
                    elif last_session_substage_stage == 2 and second_last_session_substage_stage == 2:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.2 to 1.3')
                            stage = 1
                            substage = 3
                    elif last_session_substage_stage == 3 and second_last_session_substage_stage == 3:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.3 to 1.4')
                            stage = 1
                            substage = 4
                    elif last_session_substage_stage == 4 and second_last_session_substage_stage == 4:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.4 to 1.5')
                            stage = 1
                            substage = 5
                    elif last_session_substage_stage == 5 and second_last_session_substage_stage == 5:
                        if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (
                            valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                            print(f'Advancing from stage 1.5 to normal task')
                            task = 'Probability_Training_BB'
                            stage = 1
                            substage = 0

        elif 'Probability_Training_BB' in task:
            # Check stage-specific conditions for advancement
            if last_session_task == second_last_session_task:
                # Stage 1 -> Stage 2 check
                if last_session_stage == 1 and second_last_session_stage == 1:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        print(f'Advancing from stage 1 to stage 2 with accuracy in both sessions')
                        stage = 2
                # Stage 2 -> Stage 3 check
                elif last_session_stage == 2 and second_last_session_stage == 2:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        print(f'Advancing from stage 2 to stage 3 with accuracy in both sessions')
                        stage = 3
                # Stage 3 -> Weber's Law
                elif last_session_stage == 3 and second_last_session_stage == 3:
                    if (valid_trials_last >= trial_criteria and accuracy_last >= accuracy_criteria) and (valid_trials_second_last >= trial_criteria and accuracy_second_last >= accuracy_criteria):
                        print(f'Should advance from stage 3 to Webers Law with accuracy in both sessions')
                        # print(f'Advancing from stage 3 to Webers Law with accuracy in both sessions')
                        # stage = 4
                        # task = 'Probability_WebersLaw'
                        # block = 12  # This is the number of trials one conditions will remain for
                        # conditions = []  # Takes the conditions from select task file.
                        # completed_conditions = []  # To store completed conditions
                        # current_condition = 0  # To track the current condition in progress
                        # repetition = 3  # To store how many times the conditions needs to repeat.
                        # current_repetition = 0  # To store how many times the condition has repeated.
                        # trial_counter = 0  # Track the number of trials for the current condition
                        # # Image output stims:
                        # stim_trial = 0
                        # stim_trials = []
                        # stim_trial_counter = 0

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
                task = 'Water_Filler'
                # variables by default
                stage = 5
                substage = 0
                choice = 0
                wait_seconds = 3600 * settings.TIME_TO_ENTER  # wait a minimum of x hours before allowed to start the new session)
                stim_dur_ds = 0
                stim_dur_dm = 0
                stim_dur_dl = 0
                # Weber's Law:
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


    elif task == 'Water_Filler':
        task = Water_Filler
        print("rat drank water")
        # variables by default
        stage = 5
        substage = 0
        choice = 0
        wait_seconds = 3600 * settings.TIME_TO_ENTER  # wait a minimum of x hours before allowed to start the new session)
        stim_dur_ds = 0
        stim_dur_dm = 0
        stim_dur_dl = 0
        # Weber's Law:
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

    if my_subject == 'm2':
        wait_seconds = 5

    return task, stage, substage, wait_seconds, stim_dur_ds, stim_dur_dm, stim_dur_dl, choice, block, conditions, completed_conditions, current_condition, repetition, current_repetition, trial_counter, stim_trial, stim_trials, stim_trial_counter
