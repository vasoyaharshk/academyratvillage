import time
from pybpodapi.protocol import Bpod, StateMachine
from academy import telegram_bot
from academy.softcode import softcode


def play_buzzer1(task=None):
    try:
        try:
            task.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, channel_number=2, value=255)
            time.sleep(0.5)
            task.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, channel_number=2, value=0)
        except Exception:
            my_bpod = create_Bpod()
            my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, channel_number=2, value=255)
            time.sleep(0.5)
            my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, channel_number=2, value=0)
            softcode.kill()
            my_bpod.close()
    except:
        telegram_bot.alarm_bpod("error buzzer1")


def play_buzzer2(task=None):
    try:
        try:
            task.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=255)
            time.sleep(0.5)
            task.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=0)
        except Exception:
            my_bpod = create_Bpod()
            my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=255)
            time.sleep(0.5)
            my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=0)
            softcode.kill()
            my_bpod.close()
    except:
        telegram_bot.alarm_bpod("error buzzer2")


def open_inner_door(task=None):
    try:
        try:
            task.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=11)
        except Exception:
            my_bpod = create_Bpod()
            my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=11)
            softcode.kill()
            my_bpod.close()
    except:
        telegram_bot.alarm_bpod("error open inner door")


def close_inner_door(task=None):
    try:
        try:
            task.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=12)
        except Exception:
            my_bpod = create_Bpod()
            my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=12)
            softcode.kill()
            my_bpod.close()
    except:
        telegram_bot.alarm_bpod("error close inner door")

def testing_connection():
    i = 0
    connection = False
    while i < 4:
        try:
            bpod = Bpod()
            sma = StateMachine(bpod)
            sma.add_state(
                state_name='End',
                state_timer=0.1,
                state_change_conditions={Bpod.Events.Tup: 'exit'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20)]
            )
            bpod.send_state_machine(sma)
            bpod.run_state_machine(sma)
            bpod.close()
            i = 4
            connection = True
        except Exception:
            time.sleep(2)
            i += 1
    return connection

def create_Bpod():
    i = 0
    bpod = None
    while i < 4:
        try:
            if i == 3:
                time.sleep(0.1)
            bpod = Bpod()
            i = 4
        except Exception:
            time.sleep(2)
            i += 1
    return bpod