from academy.utils import utils
from academy import time_utils
from user import settings, select_task
import pandas as pd
import numpy as np
import os
from academy import telegram_bot


class TaskManager:
    def __init__(self, subject):
        self.subject = subject
        self.start = time_utils.now_string()
        self.df = None
        self.new_df = None

        filename = str(self.subject.name) + '_' + str(self.subject.task)
        filename += '-' + str(int(float(self.subject.stage))) + '-' + str(int(float(self.subject.substage)))
        filename += '_' + str(self.start)
        filename = filename.replace("/", "")
        filename = filename.replace(":", "")
        filename = filename.replace(" ", "-")
        self.filename = filename
        self.df_all = None

    def save_csvs(self, weight=None):

        subject_directory = os.path.join(settings.SESSIONS_DIRECTORY, self.subject.name)
        raw_path = os.path.join(subject_directory, self.filename + '_raw.csv')
        clean_path = os.path.join(subject_directory, self.filename + '.csv')
        subject_path = os.path.join(subject_directory, self.subject.name + '.csv')

        session_path = os.path.join(settings.SESSIONS_DIRECTORY, settings.SESSION_NAME) + '.csv'

        self.df = pd.read_csv(os.path.join(session_path), sep=';')

        if self.df.shape[0] > settings.OVERDETECTIONS:
            telegram_bot.alarm_overdetections(self.filename)


        if self.df['TRIAL'].iloc[-1] > 1:
            if not os.path.exists(subject_directory):
                os.mkdir(subject_directory)

            self.df.to_csv(raw_path, index=None, header=True, sep=';')

            self.new_df = self.transform_df()
            water = self.new_df['reward_drunk'].iloc[-1]
            self.new_df.to_csv(clean_path, sep=';', header=True, index=False)

            try:
                self.df_all = pd.read_csv(subject_path, sep=';')
                self.new_df['session'] = [(int(self.df_all['session'].iloc[-1]) + 1)] * self.new_df.shape[0]
                self.df_all = pd.concat([self.df_all, self.new_df], sort=True)
            except FileNotFoundError:
                self.new_df.insert(loc=0, column='session', value=1)
                self.df_all = self.new_df

            self.df_all.to_csv(subject_path, header=True, index=False, sep=';')
            self.df_all = self.df_all.apply(pd.to_numeric, args=('ignore', ))

            task, stage, substage, wait_seconds, stim_dur_ds, stim_dur_dm, stim_dur_dl, choice = select_task.select_task(self.df_all, self.subject)

            if weight:
                utils.subjects.add_new_item({'task': task,
                                             'stage': stage,
                                             'substage': substage,
                                             'wait_seconds': wait_seconds,
                                             'weight': weight,
                                             'water': water,
                                             'stim_dur_ds': stim_dur_ds,
                                             'stim_dur_dm': stim_dur_dm,
                                             'stim_dur_dl': stim_dur_dl, 'choice': choice}, item=self.subject)

            else:
                utils.subjects.add_new_item({'task': task,
                                             'stage': stage,
                                             'substage': substage,
                                             'wait_seconds': wait_seconds,
                                             'stim_dur_ds': stim_dur_ds,
                                             'stim_dur_dm': stim_dur_dm,
                                             'stim_dur_dl': stim_dur_dl, 'choice': choice}, item=self.subject)
        else:
            telegram_bot.alarm_few_trials(0, self.subject.name)
            pass

    def transform_df(self):

        def make_list(x):
            if x.size <= 1:
                return x
            elif x.isnull().all():
                return np.nan
            else:
                return ','.join([str(x.iloc[i]) for i in range(len(x))])

        df0 = self.df
        df0['idx'] = range(1, len(df0) + 1)
        df1 = df0.set_index('idx')
        df2 = df1.pivot_table(index='TRIAL', columns='MSG', values=['START', 'END'],
                              aggfunc=make_list)

        df3 = df1.pivot_table(index='TRIAL', columns='MSG', values='VALUE',
                              aggfunc=lambda x: x if x.size == 1 else x.iloc[0])
        df4 = pd.concat([df2, df3], axis=1, sort=False)

        columns_to_drop = [item for item in df4.columns if type(item) == tuple and
                           (item[1].startswith('_Tup') or item[1].startswith('_Transition') or
                            item[1].startswith('_Global') or item[1].startswith('_Condition'))]
        df4.drop(columns=columns_to_drop, inplace=True)

        columns_to_drop = [item for item in df4.columns if type(item) == str and
                           (item.startswith('_Tup') or item.startswith('_Transition') or
                            item.startswith('_Global') or item.startswith('_Condition'))]
        df4.drop(columns=columns_to_drop, inplace=True)

        df4.columns = [item[1] + '_' + item[0] if type(item) == tuple else item for item in df4.columns]

        df4.replace('', np.nan, inplace=True)
        df4.dropna(subset=['TRIAL_END'], inplace=True)
        df4['trial'] = range(1, len(df4) + 1)

        list_of_columns = df4.columns

        start_list = [item for item in list_of_columns if item.endswith('_START')]
        end_list = [item for item in list_of_columns if item.endswith('_END')]
        other_list = [item for item in list_of_columns if item not in start_list and item not in end_list]

        states_list = []
        for item in start_list:
            states_list.append(item)
            for item2 in end_list:
                if item2.startswith(item[:-5]):
                    states_list.append(item2)

        new_list = ['date', 'trial', 'subject', 'task', 'stage', 'checksum', 'box', 'TRIAL_START', 'TRIAL_END']
        new_list += states_list + other_list
        new_list = pd.Series(new_list).drop_duplicates().tolist()

        df4 = df4[new_list]

        return df4
