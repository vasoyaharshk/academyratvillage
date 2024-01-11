from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings


class WaterCalibration(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        Instructions of the task.
        Water and tolerance are measured in microliters.
        Weight is measured in grams.
        """

    def init_variables(self):
        self.trials_max = 100

        self.interval = 0.3
        self.tolerance = 0.5

        self.collection = utils.water_calibration
        self.ports = settings.BPOD_BEHAVIOR_PORTS_WATER
        self.water = [8] * 8
        self.pulse_duration = [0.005] * 8
        for i in range(len(self.ports)):
            item = self.collection.read_last_value('port', i + 1)
            if item is not None:
                self.water[i] = item.water
                self.pulse_duration[i] = item.pulse_duration

        self.weight = [0] * 8
        self.min_pulse_duration = [0] * 8
        self.max_pulse_duration = [1000] * 8
        self.min_weight = [0] * 8
        self.max_weight = [1000] * 8

        self.calibrated = [False] * 8

    def configure_gui(self):
        self.gui_input = ['trials_max', 'interval', 'tolerance', 'ports', 'water', 'weight']
        self.gui_output = ['pulse_duration', 'calibrated']

        active_ports = [i for i in range(len(self.ports)) if self.ports[i] and not self.calibrated[i]]  # starting at 0
        number_active_ports = len(active_ports)

        for i in range(number_active_ports):

            if self.weight[i] == 0:
                # first calibration, weight has not been introduced yet
                pass
            else:
                if (self.weight[i] * 1000 / self.trials_max) - self.water[i] > self.tolerance:
                    self.max_weight[i] = self.weight[i]
                    self.max_pulse_duration[i] = self.pulse_duration[i]
                elif (self.weight[i] * 1000 / self.trials_max) - self.water[i] < -self.tolerance:
                    self.min_weight[i] = self.weight[i]
                    self.min_pulse_duration[i] = self.pulse_duration[i]
                else:
                    self.calibrated[i] = True
                    self.collection.add_new_item({'port': i+1,
                                                  'water': self.water[i],
                                                  'pulse_duration': self.pulse_duration[i]
                                                  })
                if self.min_pulse_duration[i] > 0 and self.max_pulse_duration[i] < 1000:
                    self.pulse_duration[i] = self.bisection(i)
                else:
                    self.pulse_duration[i] = self.linear(i)

    def main_loop(self):

        active_ports = [i for i in range(len(self.ports)) if self.ports[i] and not self.calibrated[i]]
        number_active_ports = len(active_ports)

        if number_active_ports > 0:
            for i in range(number_active_ports):

                port = active_ports[i] + 1  # ports are numerated from 1 to 8

                if i == number_active_ports - 1:
                    change_to_state = 'Valve_off'
                else:
                    next_port = active_ports[i + 1] + 1
                    change_to_state = 'Valve_on_' + str(next_port)

                self.sma.add_state(
                    state_name='Valve_on_' + str(port),
                    state_timer=self.pulse_duration[i],
                    state_change_conditions={Bpod.Events.Tup: change_to_state},
                    output_actions=[(Bpod.OutputChannels.Valve, port), (Bpod.OutputChannels.LED, port)])

            self.sma.add_state(
                state_name='Valve_off',
                state_timer=float(self.interval),
                state_change_conditions={Bpod.Events.Tup: 'exit'},
                output_actions=[])

    def after_trial(self):
        pass

    def linear(self, i):

        if self.min_pulse_duration[i] > 0:
            duration = self.min_pulse_duration[i]
            result = self.min_weight[i] * 1000 / self.trials_max
        else:
            duration = self.max_pulse_duration[i]
            result = self.max_weight[i] * 1000 / self.trials_max

        target = self.water[i]
        new_duration = round(duration * target / result, 4)

        return new_duration

    def bisection(self, i):
        result_high = self.max_weight[i] * 1000 / self.trials_max
        result_low = self.min_weight[i] * 1000 / self.trials_max
        result_target = self.water[i]
        duration_high = self.max_pulse_duration[i]
        duration_low = self.min_pulse_duration[i]

        bis = (result_target - result_low) * (duration_high - duration_low) / (result_high - result_low) + duration_low
        new_duration = round(bis, 4)

        return new_duration
