import evdev

TOUCHSCREEN_PORT = '/dev/input/by-id/usb-Touch__KiT_Touch_Computer_INC.-event-if00'

device = evdev.InputDevice(TOUCHSCREEN_PORT)
device.grab()

