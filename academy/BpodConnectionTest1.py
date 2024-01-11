import time
from pybpodapi.protocol import Bpod, StateMachine

i = 0
connection = False
while i < 4:
        bpod = Bpod()
        sma = StateMachine(bpod)
        sma.add_state(
            state_name='End',
            state_timer=5,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 20)]
        )
        bpod.send_state_machine(sma)
        bpod.run_state_machine(sma)
        bpod.close()
        i = 4
        connection = True
        print('Success')
