import os
import time
from datetime import datetime, timedelta

import pandas as pd

from academy import telegram_bot
from academy.utils import utils
from user import settings


_last_poll_time = 0.0


def _notify(message, subject_name):
    print(message)
    try:
        telegram_bot.alarm_finish_session(message, subject_name)
    except Exception as error:
        print("Automatic Water Telegram message not sent:", error)


def _marker_path():
    return os.path.join(
        settings.DATA_DIRECTORY,
        "automatic_water_check_date.txt",
    )


def _read_last_check_date():
    try:
        with open(_marker_path(), "r") as marker_file:
            return marker_file.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as error:
        _notify(
            "Automatic Water check could not read its date marker: "
            + str(error),
            "Academy",
        )
        return ""


def _write_last_check_date(check_date):
    with open(_marker_path(), "w") as marker_file:
        marker_file.write(check_date.isoformat())


def _active_subject_names():
    names = set()
    for item in utils.subjects.items:
        name = getattr(item, "name", None)
        if name is not None and not pd.isna(name):
            names.add(str(name))
    return sorted(names)


def run_daily_automatic_water_check(check_date):
    try:
        days_to_check = max(
            1,
            int(
                getattr(
                    settings,
                    "AUTOMATIC_WATER_DAYS_TO_CHECK",
                    2,
                )
            ),
        )
    except (TypeError, ValueError):
        days_to_check = 2
        _notify(
            "Invalid AUTOMATIC_WATER_DAYS_TO_CHECK setting. "
            "Using 2 days.",
            "Academy",
        )

    days_checked = [
        check_date - timedelta(days=days_ago)
        for days_ago in range(1, days_to_check + 1)
    ]

    excluded_subjects = set(
        getattr(
            settings,
            "AUTOMATIC_WATER_EXCLUDED_SUBJECTS",
            ["m3"],
        )
    )
    excluded_subjects.update(
        getattr(settings, "INACTIVE_SUBJECTS", [])
    )

    changed_subjects = []
    skipped_subjects = []

    for subject_name in _active_subject_names():
        if subject_name in excluded_subjects:
            continue

        subject = utils.subjects.read_last_value_excluding(
            "name",
            subject_name,
            "task",
            ["manual_water", "control_weight", "basal_weight"],
        )

        if subject is None:
            skipped_subjects.append(
                subject_name + ": current subject record not found"
            )
            continue

        if subject.task == "Automatic_Water":
            continue

        subject_path = os.path.join(
            settings.SESSIONS_DIRECTORY,
            subject_name,
            subject_name + ".csv",
        )

        if not os.path.exists(subject_path):
            skipped_subjects.append(
                subject_name + ": session history file not found"
            )
            continue

        try:
            subject_history = pd.read_csv(
                subject_path,
                sep=";",
                low_memory=False,
            )
        except Exception as error:
            skipped_subjects.append(
                subject_name + ": session history could not be read: "
                + str(error)
            )
            continue

        if "date" not in subject_history.columns:
            skipped_subjects.append(
                subject_name + ": session history has no date column"
            )
            continue

        history_dates = pd.to_datetime(
            subject_history["date"],
            errors="coerce",
        ).dt.date

        trials_in_check_period = int(
            history_dates.isin(days_checked).sum()
        )

        if trials_in_check_period == 0:
            utils.subjects.add_new_item(
                {
                    "task": "Automatic_Water",
                    "wait_seconds": 0.0,
                },
                item=subject,
            )
            changed_subjects.append(subject_name)
            _notify(
                "Automatic Water assigned because 0 trials were "
                "recorded from "
                + days_checked[-1].isoformat()
                + " to "
                + days_checked[0].isoformat()
                + " ("
                + str(days_to_check)
                + " full days)",
                subject_name,
            )

    for skipped_subject in skipped_subjects:
        _notify(
            "Automatic Water check skipped " + skipped_subject,
            "Academy",
        )

    return bool(changed_subjects)


def automatic_water_check_is_due():
    global _last_poll_time

    now_monotonic = time.monotonic()
    poll_seconds = getattr(
        settings,
        "AUTOMATIC_WATER_CHECK_POLL_SECONDS",
        60,
    )

    if now_monotonic - _last_poll_time < poll_seconds:
        return False

    _last_poll_time = now_monotonic
    now = datetime.now()

    check_hour = getattr(
        settings,
        "AUTOMATIC_WATER_CHECK_HOUR",
        19,
    )
    check_minute = getattr(
        settings,
        "AUTOMATIC_WATER_CHECK_MINUTE",
        55,
    )

    if (now.hour, now.minute) < (check_hour, check_minute):
        return False

    return _read_last_check_date() != now.date().isoformat()


def run_scheduled_automatic_water_check():
    today = datetime.now().date()

    # Defensive check in case the state is entered twice on the same day.
    if _read_last_check_date() == today.isoformat():
        return False

    try:
        subjects_changed = run_daily_automatic_water_check(today)
        _write_last_check_date(today)
        return subjects_changed
    except Exception as error:
        _notify(
            "Automatic Water daily check failed and will retry: "
            + str(error),
            "Academy",
        )
        return False
