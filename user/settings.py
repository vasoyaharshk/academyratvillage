# THIS IS A BACKUP FILE. DO NOT CHANGE IT.
# THE FIRST TIME THE APPLICATION IS LAUNCHED, A COPY OF THIS FILE IS CREATED IN THE USER DIRECTORY.
# ALWAYS MODIFY THE WORKING VERSION IN THE USER DIRECTORY.


import pkg_resources
import os


# default bpod values (not to be changed)
TARGET_BPOD_FIRMWARE_VERSION = "22"
PYBPOD_BAUDRATE = 1312500
PYBPOD_SYNC_CHANNEL = 255
PYBPOD_SYNC_MODE = 1
PYBPOD_API_MODULES = []
SESSION_NAME = 'session'
DISTRIBUTION_DIRECTORY = pkg_resources.get_distribution('academy').location
TASKS_DIRECTORY = os.path.join(DISTRIBUTION_DIRECTORY, 'tasks')
USER_DIRECTORY = os.path.join(DISTRIBUTION_DIRECTORY, 'user')
DATA_DIRECTORY = os.path.join(DISTRIBUTION_DIRECTORY, 'data')
BACKUP_TASKS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'backup_tasks')
SESSIONS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'sessions')
VIDEOS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'videos')
DROPBOX_SESSIONS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'sessions')


# serial and net ports
#ARDUINO_SERIAL_PORT = '/dev/ttyUSB-Arduino'                                         # <-- TO CHANGE
ARDUINO_SERIAL_PORT = '/dev/ttyACM-Arduino'                                         # <-- TO CHANGE
ARDUINO_INSIDE_SERIAL_PORT = '/dev/ttyUSB-Arduino_inside'                           # <-- TO CHANGE
#PYBPOD_SERIAL_PORT = '/dev/ttyACM-Bpod3'                                            # <-- TO CHANGE
PYBPOD_SERIAL_PORT = '/dev/ttyACM-BPOD'
PYBPOD_NET_PORT = 36000  # network port to receive remote commands like softcodes
TOUCHSCREEN_PORT = '/dev/input/by-id/usb-Touch__KiT_Touch_Computer_INC.-event-if00' # <-- TO CHANGE
CAMERA1_PORT = "/dev/video-Cam1"
CAMERA2_PORT = "/dev/video-Cam2"
CAMERA3_PORT = "/dev/video-Cam3"


# bpod ports
BPOD_BNC_PORTS_ENABLED = [False, False]
BPOD_WIRED_PORTS_ENABLED = [False, False]
BPOD_BEHAVIOR_PORTS_ENABLED = [True, True, True, True, False, False, False, False]  # ports that are activated
BPOD_BEHAVIOR_PORTS_WATER = [True, False, False, False, False, False, False, False]  # ports that deliver water


# touchscreen
XINPUT = 'xinput map-to-output "Touch__KiT Touch  Computer INC." HDMI1'   # <-- TO CHANGE
WIN_SIZE = [403, 252]  # in mm
WIN_RESOLUTION = [1440, 900]
TOUCH_RESOLUTION = [4096, 4096]
SCREEN_NUMBER = 0
VIEW_POSITION = [-int(WIN_RESOLUTION[0] / 2), -int(WIN_RESOLUTION[1] / 2)]
WIN_COLOR = [-1, -1, -1]
PIXELS_PER_MM = 3.57
STIM_WIDTH = 40  # mm
TIME_BETWEEN_RESPONSES = 0.5


# mouse detection
NOMICECAGE = 20  # if area_cage > NOMICECAGE animal can not enter        # <-- TO CHANGE
NOMICEDOOR1 = 60  # if area_doors1 > NOMICEDOOR1 animal can not enter    # <-- TO CHANGE
NOMICEDOOR2 = 100  # if area_doors2 > NOMICEDOOR2 animal can not exit    # <-- TO CHANGE
ONEMOUSE = 2400  # if area_total > ONEMOUSE animal can not enter         # <-- TO CHANGE
SEVERALMICE = 1600  # if area_box > SEVERALMICE, alarm 2 mice inside box # <-- TO CHANGE
FLOORMOUSE = 50

THRESHOLD_DAY_CAGE = 43                                                  # <-- TO CHANGE
THRESHOLD_DAY_DOOR1 = 43                                                 # <-- TO CHANGE
THRESHOLD_DAY_DOOR2 = 43                                                 # <-- TO CHANGE

THRESHOLD_NIGHT_CAGE = 22                                                # <-- TO CHANGE
THRESHOLD_NIGHT_DOOR1 = 85                                               # <-- TO CHANGE
THRESHOLD_NIGHT_DOOR2 = 85                                               # <-- TO CHANGE

DURATION_TAG = 1  # seconds the rfid lecture is stored
DURATION_TAGS = 10  # seconds tags are stored if there is a tag different than current animal can not enter
HOUR_DAY = 8  # night is more restrictive so it last 1 minute more when changing
MINUTE_DAY = 1
HOUR_NIGHT = 19
MINUTE_NIGHT = 59
TIME_TO_ENTER = 5 # time between session and session (hours)            # <-- TO CHANGE
LONGER_TIME_TO_ENTER = [] #animals with longer inter session times      # <-- TO CHANGE

# camera
CAM1_NUMBER = 1
CAM1_NAME_VIDEO = 'Cam1'
CAM1_WIDTH = 640
CAM1_HEIGHT = 480
CAM1_FPS = 120
CAM1_CODEC_VIDEO = 'X264'
CAM1_STATES = {}
CAM1_DURATION_VIDEO = 1800
CAM1_NUMBER_OF_VIDEOS = 50
CAM1_THRESHOLD = 0
CAM1_CAGE_ZONE = [20, 135, 180, 300]      # <-- TO CHANGE
CAM1_DOORS1_ZONE = [150, 300, 238, 255]   # <-- TO CHANGE
CAM1_DOORS2_ZONE = [300, 425, 235, 265]   # <-- TO CHANGE
CAM1_TEXT_X = 100                         # <-- TO CHANGE
CAM1_TEXT_Y = 300                         # <-- TO CHANGE

CAM2_NUMBER = 2
CAM2_NAME_VIDEO = 'Cam2'
CAM2_WIDTH = 640
CAM2_HEIGHT = 480
CAM2_FPS = 120
CAM2_CODEC_VIDEO = 'X264'
CAM2_STATES = {}
CAM2_DURATION_VIDEO = 0
CAM2_NUMBER_OF_VIDEOS = 0
CAM2_THRESHOLD = 30
CAM2_CAGE_ZONE = None
CAM2_DOORS1_ZONE = None
CAM2_DOORS2_ZONE = None

CAM3_NUMBER = 3
CAM3_NAME_VIDEO = 'Cam3'
CAM3_WIDTH = 640
CAM3_HEIGHT = 480
CAM3_FPS = 120
CAM3_CODEC_VIDEO = 'X264'
CAM3_STATES = {"Correct": (600, 30),
               "Incorrect": (600, 70),
               "Punish": (600, 100),
               "Miss": (600, 130),
               "Resp Win": (600, 160)}
CAM3_DURATION_VIDEO = 0
CAM3_NUMBER_OF_VIDEOS = 0
CAM3_THRESHOLD = 50
CAM3_CAGE_ZONE = None
CAM3_DOORS1_ZONE = [200, 500, 65, 125]     # <-- TO CHANGE
CAM3_DOORS2_ZONE = [330, 360, 125, 470]    # <-- TO CHANGE
CAM3_FLOOR1_ZONE = [230, 300, 190, 380]    # <-- TO CHANGE
CAM3_FLOOR2_ZONE = [390, 460, 190, 380]    # <-- TO CHANGE
CAM3_FLOOR_ON = True

# telegram
#TELEGRAM_TOKEN = '1325645850:AAH9792W9DkFRE1BlOBxMp93A2R3lH6ySao'             # <-- TO CHANGE
TELEGRAM_TOKEN = '6745482132:AAFLKnMmUZU0G2ImH7DR3Ak8cRkNdQy3zRc'             # <-- TO CHANGE
TELEGRAM_CHAT = '-4048080460'                                                  # <-- TO CHANGE
TELEGRAM_USERS = {  # dictionary of users that can send telegram messages
    'Harsh': '5842767043',
}

#AWS
OPERATION_TABLE = 'operation_times'   # <-- TO CHANGE
TASK_TABLE = 'task_times'             # <-- TO CHANGE

# other
BOX_NAME = 3                         # <-- TO CHANGE

DEFAULT_TRIALS_MIN = 0
DEFAULT_DURATION_MIN = 0  # seconds
DEFAULT_TRIALS_MAX = 1000
DEFAULT_DURATION_MAX = 36000  # seconds
DEFAULT_TRIALS_TIRED = 1000
DEFAULT_DURATION_TIRED = 36000  # seconds

MINIMUM_WATER_24 = 200  # in 24 hours
MINIMUM_WATER_48 = 1000  # in 48 hours

MINIMUM_WEIGHT = 50  # in percentage
MAXIMUM_WEIGHT = 200  # in percentage

MAXIMUM_TEMPERATURE = 30
MAXIMUM_TIME = 7200  # in seconds

INACTIVE_SUBJECTS = ['None', 'manual']  # subjects that don't raise alarms and not save data
TESTING = True  # if true academy works without cams, arduino, screen or bpod

OVERDETECTIONS = 50000