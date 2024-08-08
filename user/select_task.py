import numpy as np
from academy import telegram_bot
from user import settings

# Examples of functions to calculate new task and stage
# If the function fails to return, new task and stage will be previous task and previous stage
# df is the session dataframe for the subject


def select_task(df, subject):

    # variables by default
    task = subject.task
    stage = float(subject.stage)
    substage = float(subject.substage)
    choice = subject.choice
    wait_seconds = 3600 * settings.TIME_TO_ENTER  # wait a minimum of x hours before allowed to start the new session)
    stim_dur_ds= 0
    stim_dur_dm= 0
    stim_dur_dl= 0

    # dataframes
    last_session = df.session.max()
    df_last14 = df.loc[df['session'] > last_session - 14].copy()  # last 14 sessions
    df_last5 = df.loc[df['session'] > last_session - 5].copy()  # last five sessions
    df_last3 = df.loc[df['session'] > last_session - 3].copy()  # last three sessions
    df_last2 = df.loc[df['session'] > last_session - 2].copy()  # last two sessions
    df = df.loc[df['session'] == last_session].copy()           # last session

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
            my_subject = df.subject.iloc[0]
            if my_subject not in settings.INACTIVE_SUBJECTS:
                telegram_bot.alarm_few_trials(n_trials, my_subject)

        # get first and last responses
        sort = df['response_x'].astype(str).str.split(',', expand=True) # separate reponses in columns
        df['first_resp'] = sort[0].astype(float)                        # select first reponses
        df['last_resp'] = sort.apply(func, axis=1).astype(float)        # select last reponses
        # useful columns
        df['first_error'] = df['first_resp'] - df['x']  # error calculation
        df['last_error'] = df['last_resp'] - df['x']
        df['first_correct_bool'] = np.where(df['correct_th'] / 2 >= df['first_error'].abs(), 1, 0)  # correct bool calc
        df['last_correct_bool'] = np.where(df['correct_th'] / 2 >= df['last_error'].abs(), 1, 0)
        df.loc[(df.trial_result == 'miss', ['first_correct_bool', 'last_correct_bool'])] = np.nan  # misses correction

        # last 3
        sort_last3 = df_last3['response_x'].astype(str).str.split(',', expand=True)
        df_last3['first_resp'] = sort_last3[0].astype(float)
        df_last3['last_resp'] = sort_last3.apply(func, axis=1).astype(float)
        df_last3['first_error'] = df_last3['first_resp'] - df_last3['x']
        df_last3['last_error'] = df_last3['last_resp'] - df_last3['x']
        df_last3['first_correct_bool'] = np.where(df_last3['correct_th'] / 2 >= df_last3['first_error'].abs(), 1, 0)
        df_last3['last_correct_bool'] = np.where(df_last3['correct_th'] / 2 >= df_last3['last_error'].abs(), 1, 0)

        # last 5
        sort_last5 = df_last5['response_x'].astype(str).str.split(',', expand=True)
        df_last5['first_resp'] = sort_last5[0].astype(float)
        df_last5['last_resp'] = sort_last5.apply(func, axis=1).astype(float)
        df_last5['first_error'] = df_last5['first_resp'] - df_last5['x']
        df_last5['last_error'] = df_last5['last_resp'] - df_last5['x']
        df_last5['last_correct_bool'] = np.where(df_last5['correct_th'] / 2 >= df_last5['last_error'].abs(), 1, 0)
        df_last5['first_correct_bool'] = np.where(df_last5['correct_th'] / 2 >= df_last5['first_error'].abs(), 1, 0)

        # last substages lists
        last3_stages = df_last3.stage.unique()
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
        vg_df = df.loc[df['trial_type'] == 'VG']
        ds_df = df.loc[((df['trial_type'] == 'DS') | (df['trial_type'] == 'DSc1') | (df['trial_type'] == 'DSc2'))]
        dm_df = df.loc[((df['trial_type'] == 'DM') | (df['trial_type'] == 'DMc1'))]
        dl_df = df.loc[((df['trial_type'] == 'DL'))]


        ############################ STAGE & SUBSTAGE SELECTION ############################

        ########## OPTO ############
        try:
            df.subject.iloc[0]
            if df.opto_type.iloc[-1]== 6 or df.opto_type.iloc[-1]== 7:  # 0 off, 6 for inhibition, 7 for activation
                choice = 0
            elif df.opto_type.iloc[-1] == 0:
                choice = 6
        except: # no opto sessions
            choice = subject.choice

        ############ STAGE 1 ############
        if stage == 1:
            if substage == 1:
                if last3_poke_acc >= 0.8 and len(last5_substages) == 1 and n_trials > 60:  # next substage
                    substage += 1
                # elif n_trials <= 15 and len(last5_substages) == 1:  # go to Touchteaching
                #     task = 'TouchTeaching'
                #     stage -= 1
                #     substage -= 1

            elif substage == 2:
                stim_pos_acc = vg_df.groupby('x')['first_correct_bool'].mean() # accuracy by stimulus in VG trials
                stim_pos_acc.to_list()
                if all(i >= 0.7 for i in stim_pos_acc) and len(last5_substages) == 1 and n_trials > 60 and first3_poke_acc >0.65:  # next substage
                    substage += 1
                elif first_poke_acc <= 0.33 and len(last3_substages) == 1:  # lower substage
                    substage -= 1

            elif substage == 3:
                acc_ds = ds_df['first_correct_bool'].mean() # accuracy in delay short
                if acc_ds >= 0.55 and len(last5_substages) == 1 and n_trials > 60 and first3_poke_acc >0.7:  # next stage
                    stage += 1
                    substage = float(1)
                    stim_dur_ds = 0.45
                elif first_poke_acc < 0.35 and len(last3_substages) == 1 :  # lower substage
                    substage -= 1

        ############ STAGE 2 ############
        elif stage == 2:
            next_stage = False
            lower_stage = False
            if substage == 1:
                max_stim_dur = 0.45
                average, initial = variable_calc('stim_dur_ds', max_stim_dur, max_stim_dur)
                acc = ds_df['first_correct_bool'].mean()
                last3_stim_dur = df_last3.loc[df_last3['trial'] == 10]['stim_dur_ds'].median()
                acc_up = 0.6
                acc_down = 0.45
                change = 0.075
            elif substage ==2:
                max_stim_dur = 0.4
                average, initial = variable_calc('stim_dur_dm', max_stim_dur, max_stim_dur)
                acc = (dm_df['first_correct_bool'].mean() + ds_df['first_correct_bool'].mean())/2
                last3_stim_dur = df_last3.loc[df_last3['trial'] == 10]['stim_dur_dm'].median()
                acc_up = 0.55
                acc_down = 0.4
                change = 0.05
            elif substage ==3:
                max_stim_dur = 0.35
                average, initial = variable_calc('stim_dur_dl', max_stim_dur, max_stim_dur)
                acc = (dl_df['first_correct_bool'].mean() + dm_df['first_correct_bool'].mean()) / 2
                last3_stim_dur = df_last3.loc[df_last3['trial'] == 10]['stim_dur_dl'].median()
                acc_up = 0.5
                acc_down = 0.35
                change = 0.025

            # Good accuracy -> shorten stim_dur
            if acc > acc_up and n_trials>55:
                if initial >= change:
                    stim_dur = initial - change
                else:
                    stim_dur = 0
                    if last3_stim_dur < change and len(last5_substages)==1: # if stim_dur is the minimum for 3 sessions advance stage
                        next_stage = True  # next substage

            # Bad accuracy or demotivation -> elongate stim_dur
            else:
                stim_dur = initial # maintain last session value unless ...
                if n_trials <= 25 and n_trials_prev<= 25:       # Hard demotivation
                    if initial <= max_stim_dur:
                        stim_dur = initial + change
                    else:
                        if last3_stim_dur >= max_stim_dur:
                            lower_stage =True # lower substage
                if acc <acc_down:                               # Low specific accuracy
                    if initial <= max_stim_dur:
                        stim_dur = initial + change
                if df_last3.first_correct_bool.mean() <= 0.4:   # Low global accuracy
                    lower_stage = True # lower substage

            if substage == 1:  # stage 2 remain now in substage 1 ds 0
                stim_dur_ds = stim_dur
                if next_stage == True:
                    substage += 1
                    stim_dur_ds = 0
                    stim_dur_dm = 0.4
                elif lower_stage == True:
                    stage -=1
                    substage = float(3)
                    stim_dur_ds = 0
            elif substage == 2:
                stim_dur_dm = stim_dur
                if next_stage == True:
                    substage += 1
                    stim_dur_dm = 0
                    stim_dur_dl = 0.35
                elif lower_stage == True:
                    if subject.name != "ciri" or subject.name != "sorrel":   #if subject.names not in ["sorrel", "ciri"]:
                        #substage -=1
                        stim_dur_ds = 0.45
                        stim_dur_dm = 0
            elif substage == 3:
                stim_dur_dl = stim_dur
                if next_stage == True:
                    print('pass to stage 3')
                    if len(last14_substages) == 1:
                        stage += 1
                        substage = float(1)
                        stim_dur_dl = 0
                elif lower_stage == True:
                    substage -=1
                    stim_dur_dm = 0.4
                    stim_dur_dl = 0

    elif task == 'Probability_1':
        if n_trials < 15:
            my_subject = df.subject.iloc[0]
            if my_subject not in settings.INACTIVE_SUBJECTS:
                telegram_bot.alarm_few_trials(n_trials, my_subject)

        # get first and last responses
        sort = df['response_x'].astype(str).str.split(',', expand=True) # separate reponses in columns
        df['first_resp'] = sort[0].astype(float)                        # select first reponses
        df['last_resp'] = sort.apply(func, axis=1).astype(float)        # select last reponses
        # useful columns
        df['first_error'] = df['first_resp'] - df['x']  # error calculation
        df['last_error'] = df['last_resp'] - df['x']
        df['first_correct_bool'] = np.where(df['correct_th'] / 2 >= df['first_error'].abs(), 1, 0)  # correct bool calc
        df['last_correct_bool'] = np.where(df['correct_th'] / 2 >= df['last_error'].abs(), 1, 0)
        df.loc[(df.trial_result == 'miss', ['first_correct_bool', 'last_correct_bool'])] = np.nan  # misses correction

        # last 2 sessions:
        sort_last2 = df_last2['response_x'].astype(str).str.split(',', expand=True)
        df_last2['first_resp'] = sort_last2[0].astype(float)
        df_last2['last_resp'] = sort_last2.apply(func, axis=1).astype(float)
        df_last2['first_error'] = df_last2['first_resp'] - df_last2['x']
        df_last2['last_error'] = df_last2['last_resp'] - df_last2['x']
        df_last2['first_correct_bool'] = np.where(df_last2['correct_th'] / 2 >= df_last3['first_error'].abs(), 1, 0)
        df_last2['last_correct_bool'] = np.where(df_last2['correct_th'] / 2 >= df_last3['last_error'].abs(), 1, 0)

        # accuracies calc
        first_poke_acc = df.first_correct_bool.mean()
        last_poke_acc = df.last_correct_bool.mean()
        first2_poke_acc = df_last2.first_correct_bool.mean()
        last2_poke_acc = df_last2.last_correct_bool.mean()

        # last 2 stages lists:
        last2_stages = df_last2.stage.unique()

        if stage == 1:
            #if first2_poke_acc >= 0.5 and len(last2_stages) == 1 and n_trials > 40:  # next substage
            if first2_poke_acc >= 0.5 and len(last2_stages) == 1 and n_trials > 5:  # next substage
                stage += 1

    return task, stage, substage, wait_seconds, stim_dur_ds, stim_dur_dm, stim_dur_dl, choice
