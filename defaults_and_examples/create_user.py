import os
from defaults_and_examples import default_settings


def create_user_from_defaults():

    defaults_directory = os.path.join(default_settings.DISTRIBUTION_DIRECTORY, 'defaults_and_examples')
    settings_file = os.path.join(default_settings.USER_DIRECTORY, 'settings.py')
    default_settings_file = os.path.join(defaults_directory, 'default_settings.py')

    if not os.path.exists(default_settings.DATA_DIRECTORY):
        os.mkdir(default_settings.DATA_DIRECTORY)

    if not os.path.exists(default_settings.BACKUP_TASKS_DIRECTORY):
        os.mkdir(default_settings.BACKUP_TASKS_DIRECTORY)

    if not os.path.exists(default_settings.SESSIONS_DIRECTORY):
        os.mkdir(default_settings.SESSIONS_DIRECTORY)

    if not os.path.exists(default_settings.VIDEOS_DIRECTORY):
        os.mkdir(default_settings.VIDEOS_DIRECTORY)

    if not os.path.exists(default_settings.ECOHAB_DIRECTORY):
        os.mkdir(default_settings.ECOHAB_DIRECTORY)

    if not os.path.exists(settings_file):
        with open(default_settings_file, "r") as inputfile:
            data = inputfile.read().splitlines(True)
        with open(settings_file, "w") as outputfile:
            outputfile.writelines(data[5:])
