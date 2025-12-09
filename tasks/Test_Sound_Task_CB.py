from pybpodapi.protocol import Bpod
from academy.task_collection import Task
from user import settings
import time

class Test_Sound_Task_CB(Task):
    def __init__(self):
        super().__init__()

        # Rat grouping: "A" or "B"
        self.group = 1

        # SOUND PARAMETERS
        self.pair   = 1       # 1..4
        self.probe  = 0       # 0..4
        self.shape  = None    # Will be assigned each trial

        # STIMULUS DIMENSIONS (mm)
        self.y_correcth = 152
        self.width  = 100
        self.height = 100

        # Two possible horizontal positions (mm)
        self.x_correcth_pos = [95, 281]  # Left, Right
        self.side = None  # Will be set each trial
        self.x_correcth = None

        self.valve_factor_c = 5.6
        self.valve_factor_i = 2.8

        self.probes = [0, 4]


    def configure_gui(self):
        #self.gui_input = ['pair', 'probe', 'group']
        self.gui_input = ['duration_max']

    def main_loop(self):
        print(f"Tone: {self.pair}, {self.probe}")

        # Assign side & shape based on group and pair
        if self.group == 1:
            if self.pair in [1, 3]: #Left side is higher rewarding
                self.side = "left"
                self.shape = "triangle"
                self.probe = 4
            elif self.pair in [2, 4]:  # Left side is higher rewarding
                self.side = "right"
                self.shape = "circle"
                self.probe = 0
            else:
                message = "pair not found"
                print(message)
        elif self.group == 2:
            if self.pair in [1, 3]: #Left side is higher rewarding
                self.side = "right"
                self.shape = "circle"
                self.probe = 0
            elif self.pair in [2, 4]:  # Left side is higher rewarding
                self.side = "left"
                self.shape = "triangle"
                self.probe = 4
            else:
                message = "pair not found"
                print(message)
        else:
            message = "group not found"
            print(message)

        if self.side == "left":
            self.x_correcth = self.x_correcth_pos[0]
            self.x_incorrecth = self.x_correcth_pos[1]
        elif self.side == "right":
            self.x_correcth = self.x_correcth_pos[1]
            self.x_incorrecth = self.x_correcth_pos[0]
        else:
            message = "Side not found"
            print(message)

        print(f"Group: {self.group}, Pair: {self.pair}, Probe: {self.probe}, Side: {self.side}, Shape: {self.shape}, "
              f"x_correcth: {self.x_correcth}, x_incorrecth: {self.x_incorrecth}, y_correcth: {self.y_correcth}, "
              f"width: {self.width}, height: {self.height}")

        self.sma.add_state(
            state_name='Wait_for_Poke',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Play_Reward_Tone'},
            output_actions=[]
        )

        self.sma.add_state(
            state_name='Play_Reward_Tone',
            state_timer=60.0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 230)]
        )

        self.sma.add_state(
            state_name='Exit',
            state_timer=5.0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 222)]
        )

    def after_trial(self):
        print(f"Trial {self.current_trial + 1} completed.")
