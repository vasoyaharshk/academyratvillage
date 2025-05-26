from pybpodapi.protocol import Bpod
from academy.task_collection import Task
from user import settings
import time

class Test_Sound_Task(Task):
    def __init__(self):
        super().__init__()

        # SOUND PARAMETERS (used by functions.py softcode logic)
        #self.reward_freq = 6000.0     # Hz, float allowed
        #self.reward_db = 70           # dB SPL

    def configure_gui(self):
        self.gui_input = []

    def main_loop(self):
        print(f"Reward tone: {self.reward_frequency} Hz, {self.reward_db} dB")

        self.sma.add_state(
            state_name='Wait_for_Poke',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port2In: 'Play_Reward_Tone'},
            output_actions=[]
        )

        self.sma.add_state(
            state_name='Play_Reward_Tone',
            state_timer=1.0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 220)]
        )

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[]
        )

    def after_trial(self):
        print(f"Trial {self.current_trial + 1} completed.")
        print(f"Reward Frequency: {self.reward_frequency} Hz")
