import pandas as pd
import threading
import time
from datetime import datetime, timedelta
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.dates as mdates
import seaborn as sns
from academy.utils import utils
from user import settings
from academy import aws, queues, telegram_bot
import matplotlib
import os


matplotlib.use("TkAgg")

def unique(my_list):
    unique_list = []
    for x in my_list:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def read_dataframes(init_time, final_time):
    subjects = utils.subjects.as_df()
    subjects = subjects[~subjects['name'].isin(settings.INACTIVE_SUBJECTS)]

    subjects['date'] = subjects['date'].apply(lambda x: str(x))
    subjects['date'] = subjects['date'].apply(lambda x: pd.to_datetime(x, format='%Y/%m/%d %H:%M:%S'))

    subjects['basal_weight'] = 1000000
    all_subject_names = sorted(subjects.name.unique())
    for name in all_subject_names:
        try:
            basal = subjects['weight'].loc[(subjects['name'] == name) & (subjects['task'] == 'basal_weight')].iloc[-1]
            subjects.loc[(subjects['name'] == name, 'basal_weight')] = basal
        except:
            pass
    subjects['water'] = pd.to_numeric(subjects['water'])
    subjects['weight'] = pd.to_numeric(subjects['weight'])
    subjects['perc_weight'] = subjects['weight'] / subjects['basal_weight'] * 100

    events = utils.events.as_df()
    events = events[~events['subject'].isin(settings.INACTIVE_SUBJECTS)]

    events['date'] = events['date'].apply(lambda x: str(x))
    events['date'] = events['date'].apply(lambda x: pd.to_datetime(x, format='%Y/%m/%d %H:%M:%S'))

    subjects = subjects[subjects['date'] > init_time]
    subjects = subjects[subjects['date'] < final_time]

    events = events[events['date'] < final_time]
    events = events[events['date'] > init_time]

    subject_names = sorted(subjects.name.unique())

    weight_df = subjects.loc[subjects['task'] != 'manual_water']
    weight_df = weight_df.drop(columns=['tag', 'water', 'wait_seconds'])
    water_df = subjects.loc[(subjects['task'] != 'control_weight') & (subjects['task'] != 'basal_weight')]
    water_df = water_df.drop(columns=['tag', 'weight', 'basal_weight', 'perc_weight', 'wait_seconds'])

    start_task = events[events['type'] == 'START']
    end_task = events[events['type'] == 'END']
    missed_task = events[events['description'].str.contains('Movement in the|Not allowed to enter until')]

    task_df = pd.DataFrame(columns=['subject', 'start_task', 'end_task', 'task_name', 'stage', 'substage'], dtype=object)
    missed_df = pd.DataFrame(columns=['subject', 'date'], dtype=object)

    try:
        for name in subject_names:
            start_times = start_task['date'].loc[start_task['subject'] == name].tolist()
            task_name_total = start_task['description'].loc[start_task['subject'] == name].tolist()

            try:
                task_list = [task.split('-') for task in task_name_total]
                task_name = [task[0] for task in task_list]
                stage = [int(task[1]) for task in task_list]
                substage = [int(task[2]) for task in task_list]
            except:
                task_name = task_name_total
                stage = [1]*len(task_name_total)
                substage = [1]*len(task_name_total)

            end_times = end_task['date'].loc[end_task['subject'] == name].tolist()
            miss_times = missed_task['date'].loc[missed_task['subject'] == name].tolist()

            start_times2 = []
            end_times2 = []
            task_name2 = []
            stage2 = []
            substage2 = []
            i = 0
            j = 0

            while i < len(start_times) and j < len(end_times):

                if start_times[i] < end_times[j]:
                    if i + 1 < len(start_times):
                        if start_times[i + 1] < end_times[j]:
                            i += 1
                            continue

                    start_times2.append(start_times[i])
                    end_times2.append(end_times[j])
                    task_name2.append(task_name[i])
                    stage2.append(stage[i])
                    substage2.append(substage[i])
                    i += 1
                    j += 1
                else:
                    j += 1

            missed_df2 = pd.DataFrame({'subject': name, 'date': miss_times})

            missed_df = pd.concat([missed_df, missed_df2])


            task_df2 = pd.DataFrame({'subject': name, 'start_task': start_times2, 'end_task': end_times2,
                               'task_name': task_name2, 'stage': stage2, 'substage': substage2})

            task_df = pd.concat([task_df, task_df2])

        weight_df['day'] = weight_df['date'] - timedelta(hours=8)
        weight_df['day'] = weight_df['day'].dt.normalize() + timedelta(hours=20)
        water_df['day'] = water_df['date'] - timedelta(hours=8)
        water_df['day'] = water_df['day'].dt.normalize() + timedelta(hours=20)
        missed_df['day'] = missed_df['date'] - timedelta(hours=8)
        missed_df['day'] = missed_df['day'].dt.normalize() + timedelta(hours=20)
        task_df['day'] = task_df['start_task'] - timedelta(hours=8)
        task_df['day'] = task_df['day'].dt.normalize() + timedelta(hours=20)
        weight_df.rename({'name': 'subject'}, axis=1, inplace=True)
        water_df.rename({'name': 'subject'}, axis=1, inplace=True)
    except:
        pass

    return all_subject_names, weight_df, water_df, missed_df, task_df


def rt_plot(init_time, final_time):

    print('starting rt plot')

    # reading dataframes
    try:
        subject_names, weight_df, water_df, missed_df, task_df = read_dataframes(init_time, final_time)
    except:
        utils.log('Academy', 'Error reading dataframes in rt_plots', 'ACTION')


    print('starting manipulate data')

    # manipulating data
    try:
        # subject colors
        colors = ['darkgreen', 'mediumseagreen', 'greenyellow',
        'yellow', 'orange', 'salmon', 'tomato', 'crimson', 'mediumvioletred',
        'darkorchid', 'darkblue', 'royalblue', 'lightskyblue', 'mediumaquamarine',
        'green', 'yellowgreen'] # 'gold',  'goldenrod',

        missed_df['colors'] = 'black'
        for idx, subject in enumerate(subject_names):
            missed_df.loc[(missed_df['subject'] == subject, 'colors')] = colors[idx]

        #tasks colors
        task_df['colors'] = 'black'
        colors2 = ['purple', 'royalblue', 'yellowgreen',  'forestgreen']

        stages = task_df.stage.unique()
        stages.sort()
        for idx, stage in enumerate(stages):
            if stage == 0:
                colors2.insert(0, "crimson")
            task_df.loc[(task_df['stage'] == stage, 'colors2')] = colors2[idx]

        task_df.loc[(task_df['task_name'] == 'Habituation', 'colors2')] = 'orange'
        task_df.loc[(task_df['task_name'] == 'LickTeaching', 'colors2')] = 'salmon'
        task_df.loc[(task_df['task_name'] == 'TouchTeaching', 'colors2')] = 'crimson'

        day = init_time
        days = []

        while day < final_time:
            days.append(day)
            day += timedelta(days=1)

        days_at_20 = [day + timedelta(hours=12) for day in days]
        days_at_20.append(days_at_20[-1] + timedelta(days=1))
        days_at_8 = days
        days_at_8.append(days[-1] + timedelta(days=1))

        ax1.cla()
        ax2.cla()
        ax3.cla()
        ax4.cla()
    except:
        utils.log('Academy', 'Error manipulating data in rt_plots', 'ACTION')


    print('starting plot1')

    # plot1
    try:
        for i in range(len(days_at_8) - 1):
            ax1.axvspan(days_at_20[i], days_at_8[i + 1], facecolor='lightgray', zorder=0)
        palette = sns.color_palette(colors, len(subject_names))

        df = weight_df[['day', 'subject', 'perc_weight']]
        df = df.groupby(['day', 'subject']).median()

        ax1.eventplot(days, color='black', linelengths=200, lineoffsets=100, linewidths=1)
        sns.lineplot(x='day', y='perc_weight', hue='subject', palette=palette, data=df, linewidth=1, ax=ax1)
        sns.scatterplot(x='day', y='perc_weight', hue='subject', palette=palette, data=df, ax=ax1)
        sns.lineplot(x='day', y='perc_weight', hue='subject', palette=palette, data=df, ax=ax1)
        ax1.hlines(xmin=days[-1], xmax=days[0], y=100, linestyles=':', color='gray').set_linewidth(1.5)
        ax1.set_ylabel('Relative\nWeight (%)')
        ax1.yaxis.set_tick_params(labelsize=8)
        ax1.set_xticks(days_at_8 + days_at_20)
        ax1.xaxis.set_ticklabels([])
        ax1.set_ylim(80, 120)
        ax1.set_xlim(days[0], days[-1])
        ax1.set_xlabel('')

        labels = subject_names
        lines = [Line2D([0], [0], color=colors[i], marker='o', markersize=6, ) for i in range(len(subject_names))]
        ax1.legend(lines, labels, fontsize=8, loc='center', bbox_to_anchor=(1, 0.2))
    except:
        utils.log('Academy', 'Error in plot 1', 'ACTION')


    #plot2
    try:
        for i in range(len(days_at_8) - 1):
            ax2.axvspan(days_at_20[i], days_at_8[i + 1], facecolor='lightgray', zorder=0)

        df = water_df[['day', 'subject', 'water']]
        df = df.groupby(['day', 'subject']).sum()
        df['water_ml'] = df['water'] / 1000
        max_water = df.water_ml.max() + 0.5

        ax2.eventplot(days, color='black', linelengths=max_water, lineoffsets=max_water / 2, linewidths=1)
        sns.lineplot(x='day', y='water_ml', hue='subject', palette=palette, data=df, ax=ax2)
        sns.scatterplot(x='day', y='water_ml', hue='subject', palette=palette, data=df, ax=ax2)
        ax2.hlines(xmin=days[-1], xmax=days[0], y=1, linestyles=':', color='gray').set_linewidth(1.5)
        ax2.set_ylabel('Water (mL)')
        ax2.yaxis.set_tick_params(labelsize=8)
        ax2.set_xticks(days_at_8 + days_at_20)
        ax2.xaxis.set_ticklabels([])
        ax2.set_xlim(days[0], days[-1])
        ax2.set_ylim(0, max_water)
        ax2.set_xlabel('')

        colors3 = ['White', 'Silver']
        labels = ['Day', 'Night']
        lines = [Patch(facecolor=colors3[i], edgecolor='black') for i in range(len(colors3))]
        ax2.legend(lines, labels, fontsize=8, loc='center', bbox_to_anchor=(1, 0.4))
    except:
        utils.log('Academy', 'Error in plot 2', 'ACTION')


    # plot3
    try:
        for i in range(len(days_at_8) - 1):
            ax3.axvspan(days_at_20[i], days_at_8[i + 1], facecolor='lightgray', zorder=0)
        ax3.eventplot(days, color='black', linelengths=30, lineoffsets=0, linewidths=1)
        ax3.scatter(missed_df.date, missed_df.subject, color=missed_df.colors, s=0.1)

        for substage in task_df.substage.unique():
            new_df = task_df.loc[task_df['substage'] == substage]
            alpha=1
            if substage ==2:
                alpha=0.7
            elif substage ==3:
                alpha = 0.35
            ax3.hlines(y=new_df.subject, xmin=new_df.start_task, xmax=new_df.end_task, color=new_df.colors2, alpha=alpha).set_linewidth(10)
        ax3.set_ylabel('Subject')
        ax3.set_xlabel('')
        ax3.set_xticks(days_at_8 + days_at_20)
        ax3.xaxis.set_tick_params(labelsize=6)
        ax3.xaxis.set_ticklabels([])
        ax3.set_ylim(-1, len(subject_names))
        ax3.set_xlim(days[0], days[-1])

        colors = ['black', 'black', 'orange', 'salmon', 'crimson', 'purple', 'royalblue',  'yellowgreen']
        labels = ['Behavioral box', 'Corridor','Habituation', 'LickTeaching', 'TouchTeaching', 'Stage 1', 'Stage 2', 'Stage 3']
        markers = ['s', '.', 's', 's', 's', 's', 's', 's']
        lines = []
        for i in range(len(labels)):
            lines.append(Line2D([0], [0], color=colors[i], linestyle='None',
                                marker=markers[i], markersize=6, markerfacecolor=colors[i]))
        ax3.legend(lines, labels, fontsize=7, loc='center', title='Subject in:', bbox_to_anchor=(1, 0.8))
    except:
        utils.log('Academy', 'Error in plot 3', 'ACTION')


    print('starting plot4')
    # plot 4
    try:
        task_df['hour'] = task_df['start_task'].dt.hour
        task_df['dn'] = 'day'
        task_df.loc[((task_df['hour'] < 8) | (task_df['hour'] >= 20)), 'dn'] = 'night'
        task_df['time_box'] = task_df['end_task'] - task_df['start_task']
        task_df['day'] = task_df['start_task'] - timedelta(hours=8)
        task_df['day'] = task_df['day'].dt.normalize() + timedelta(hours=20)

        df = task_df.groupby(['day', 'dn'])['time_box'].sum().reset_index()
        df['date'] = df.apply(lambda x:
                            x['day'].replace(hour=14, minute=0) if x['dn'] == 'day' else x['day'].replace(hour=2,
                            minute=0), axis=1)
        df['occupancy'] = 100 * df['time_box'] / timedelta(hours=12)

        for i in range(len(days_at_8) - 1):
            ax4.axvspan(days_at_20[i], days_at_8[i + 1], facecolor='lightgray', zorder=0)
        # ax4.eventplot(days, color='black', linelengths=50, lineoffsets=0, linewidths=1)
        sns.lineplot(x='date', y='occupancy', color='black', data=df, linewidth=1, ax=ax4, estimator=sum,
                     marker='o')
        ax4.hlines(xmin=days[-1], xmax=days[0], y=50, linestyles=':', color='gray').set_linewidth(1.5)
        ax4.set_ylabel('Occupancy (%)')
        ax4.set_xlabel('Date')
        ax4.xaxis.set_tick_params(labelsize=6)
        ax4.yaxis.set_tick_params(labelsize=8)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))
        ax4.set_xlim(days[0], days[-1])
    except:
        utils.log('Academy', 'Error in plot 4', 'ACTION')


def telegram_data(hours):
    final_time = datetime.now()
    init_time = final_time - timedelta(hours=hours)

    subject_names, weight_df, water_df, missed_df, task_df = read_dataframes(init_time, final_time)

    error_mice_list = []
    data = 'STATUS:' + '\n'

    if utils.state == 0:
        data += 'Box is empty' + '\n'
    else:
        try:
            data += 'Subject in box: ' + utils.subject.name + '\n'
        except:
            data += 'State is unknown' + '\n'

    data += '\n'
    data += 'SUMMARY OF THE LAST ' + str(hours) + ' HOURS:' + '\n'
    data += '\n'

    for name in subject_names:
        try:
            weight = weight_df.loc[weight_df['subject'] == name, 'weight'].median()
        except:
            weight = 0
        try:
            perc_weight = weight_df.loc[weight_df['subject'] == name, 'perc_weight'].median()
        except:
            perc_weight = 0
        try:
            water = water_df.loc[water_df['subject'] == name, 'water'].sum()
        except:
            water = 0
        try:
            weights = weight_df.loc[weight_df['subject'] == name, 'weight'].map(str).tolist()
        except:
            weights = ''
        try:
            waters = water_df.loc[water_df['subject'] == name, 'water'].map(str).tolist()
        except:
            waters = ''
        try:
            end_tasks = task_df.loc[task_df['subject'] == name, 'end_task'].dt.strftime('%d-%m %H:%M').tolist()
        except:
            end_tasks = []

        data += name + '\n'
        if len(end_tasks) == 1:
            data += '1 session'
        else:
             data += str(len(end_tasks)) + ' sessions'
        if len(end_tasks) > 0:
            data += ': ' + ', '.join(end_tasks) + '\n'
            data += '\n'
            data += 'weights: ' + ', '.join(weights) + '\n'
            data += '\n'
            data += 'mean weight: ' + str(round(weight, 2)) + ' (' + str(int(perc_weight)) + '%)' + '\n'
            data += '\n'
            data += 'water: ' + ' + '.join(waters) + ' = ' + str(water) + '\n'
            data += '\n'
        else:
            data += '\n'
            data += '\n'
        w = float(perc_weight)
        water = float(water)

        if hours == 24:
            if w < settings.MINIMUM_WEIGHT or w > settings.MAXIMUM_WEIGHT or water < settings.MINIMUM_WATER_24:
                error_mice_list.append(name)
        elif hours == 48:
            if water < settings.MINIMUM_WATER_48:
                error_mice_list.append(name)

    return data, error_mice_list



def animate_thread():

    filename = os.path.join(settings.DATA_DIRECTORY, 'plots.jpg')
    set_alarm = True
    # last_alarm = 0
    aws.send_timing()

    while True:

        time.sleep(3)

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        try:
            queues.update_plots.get_nowait()
            final_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if hour >= 8:
                final_time += timedelta(days=1)
            init_time = final_time - timedelta(days=utils.x_max)
            plot = True
        except:
            plot = False

        if plot:
            try:
                print('message to rt plot')
                rt_plot(init_time, final_time)
                print('putting in the queues')
                queues.reload_canvas.put(True)
                print('saving')
                plt.savefig(filename)
                print('saved')
            except:
                pass

        if minute == 55:
            if set_alarm:
                set_alarm = False
                aws.send_timing()
                if hour == 7 or hour == 17:
                    try:
                        data, error_mice_list = telegram_data(hours=24)
                        if error_mice_list:
                            telegram_bot.alarm_mouse(error_mice_list)
                        else:
                            data, error_mice_list = telegram_data(hours=48)
                            if error_mice_list:
                                telegram_bot.alarm_mouse(error_mice_list)
                    except:
                        pass
        else:
            set_alarm = True

fig = plt.figure()
ax1 = plt.subplot2grid((9, 1), (0, 0), colspan=1, rowspan=2)
ax2 = plt.subplot2grid((9, 1), (2, 0), colspan=1, rowspan=2)
ax3 = plt.subplot2grid((9, 1), (4, 0), colspan=1, rowspan=3)
ax4 = plt.subplot2grid((9, 1), (7, 0), colspan=1, rowspan=2)

plt.tight_layout()
sns.despine()

thread = threading.Thread(target=animate_thread, daemon=True).start()
