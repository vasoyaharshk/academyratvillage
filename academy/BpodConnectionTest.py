from pybpodapi.protocol import Bpod, StateMachine


print('starting')
bpod = Bpod()
print('starting')
sma = StateMachine(bpod)
print('starting')
sma.add_state(
    state_name='End',
    state_timer=5,
    state_change_conditions={Bpod.Events.Tup: 'exit'},
    output_actions=[(Bpod.OutputChannels.SoftCode, 20)]
)
print('starting')
bpod.send_state_machine(sma)
print('starting')
bpod.run_state_machine(sma)
print('starting')
bpod.close()
print('starting')

print('Success 10')
