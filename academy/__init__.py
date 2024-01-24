import argparse
import psutil
import os

try:
    from user import settings
except Exception:
    from defaults_and_examples.create_user import create_user_from_defaults
    create_user_from_defaults()
    from user import settings


# ARGUMENT PARSER
description = """
academy runs behavioural protocols automatically
"""
epilog = """
use 'academy' without arguments for normal running, to exit press 'CTRL + C' in the terminal
"""

parser = argparse.ArgumentParser(description=description, epilog=epilog)

parser.add_argument("-i", "--inside",
                    help="relaunching after an error with an animal still inside the behavioural box",
                    action="store_true")

parser.add_argument('tag',
                    type=int,
                    nargs='*',
                    default='',
                    help="0 to start in automatic mode, 1 to start in day mode, "
                         "2 to start in night mode, 3 to start not reading tags")

arg = parser.parse_args()


# killing all other python processes (similar to pkill python)
this_proc = os.getpid()

for proc in psutil.process_iter():
    procd = proc.as_dict(attrs=['pid', 'name'])
    if "python" in str(procd['name']) and procd['pid'] != this_proc:
        proc.kill()
