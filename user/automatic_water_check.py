import os
import json
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



TOUCH_TASK = "Automatic_Water_Touch"


def touch_criteria():
    """Read the intervention criteria from the local user/settings.py."""
    defaults = {
        "AUTOMATIC_WATER_DAYS_TO_CHECK": 2,
        "AUTOMATIC_WATER_TRIAL_THRESHOLD": 40,
        "AUTOMATIC_WATER_TOUCH_COOLDOWN_DAYS": 7,
        "AUTOMATIC_WATER_TOUCH_RETURN_TRIALS": 80,
        "AUTOMATIC_WATER_TOUCH_RETURN_ACCURACY": 0.80,
        "AUTOMATIC_WATER_TOUCH_ALERT_DAYS": 3,
    }
    values = {}
    for name, default in defaults.items():
        raw = getattr(settings, name, default)
        try:
            value = float(raw)
            if name.endswith("ACCURACY"):
                if not 0 <= value <= 1:
                    raise ValueError("accuracy must be between 0 and 1")
            else:
                if not value.is_integer() or value < 1:
                    raise ValueError("must be a positive whole number")
                value = int(value)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"Invalid {name}={raw!r}: {error}")
        values[name] = value
    return values


def _state_path():
    return os.path.join(settings.DATA_DIRECTORY, "automatic_water_touch_state.json")


def _read_states():
    try:
        with open(_state_path()) as stream:
            return json.load(stream)
    except FileNotFoundError:
        return {}


def _json_value(value):
    if hasattr(value, "item"):
        return value.item()
    raise TypeError("Cannot save original task value: " + repr(value))


def _write_states(states):
    # Save before assigning the intervention; a failure must not lose progress.
    path = _state_path()
    with open(path + ".tmp", "w") as stream:
        json.dump(states, stream, default=_json_value)
    os.replace(path + ".tmp", path)


def _trial_rows(history):
    if "trial_result" not in history:
        raise ValueError("session history has no trial_result column")
    # Exclude administrative tasks and blank phantom/end-of-task rows.
    rows = history[history["trial_result"].isin(
        ["correct", "correct_first", "incorrect", "miss"]
    )].copy()
    if "task" in rows:
        rows = rows[~rows["task"].isin(
            ["manual_water", "control_weight", "basal_weight"]
        )]
    return rows


def _dates(history):
    # Academy writes local dates; accept both its slash format and ISO dates.
    if history.empty:
        return pd.Series(index=history.index, dtype="object")
    parsed = pd.to_datetime(history["date"], errors="coerce")
    failed = parsed.isna() & history["date"].notna()
    if failed.any():
        parsed.loc[failed] = history.loc[failed, "date"].map(
            lambda value: pd.to_datetime(value, errors="coerce")
        )
    return parsed.dt.date


def _touch_day_stats(history, assigned_at):
    rows = _trial_rows(history)
    rows = rows[rows["task"] == TOUCH_TASK].copy()
    dates = _dates(rows)
    rows = rows[dates >= assigned_at.date()]
    dates = _dates(rows)
    stats = []
    for day in sorted(dates.dropna().unique()):
        day_rows = rows[dates == day]
        valid = day_rows[day_rows["trial_result"] != "miss"]
        n = len(valid)
        correct = valid["trial_result"].isin(["correct", "correct_first"]).sum()
        stats.append((day, n, float(correct / n) if n else 0.0))
    return stats


def _alert_overdue(subject_name, state, history, now):
    criteria = touch_criteria()
    alert_days = criteria["AUTOMATIC_WATER_TOUCH_ALERT_DAYS"]
    return_trials = criteria["AUTOMATIC_WATER_TOUCH_RETURN_TRIALS"]
    return_accuracy = criteria["AUTOMATIC_WATER_TOUCH_RETURN_ACCURACY"]
    assigned = datetime.fromisoformat(state["assigned_at"])
    if now - assigned <= timedelta(days=alert_days):
        return
    # At most one urgent notification each day, also when there are no sessions.
    if state.get("last_alert_date") == now.date().isoformat():
        return
    stats = _touch_day_stats(history, assigned)
    latest = stats[-1] if stats else None
    performance = (f"Latest day {latest[0]}: {latest[1]} valid trials, "
                   f"{latest[2]:.1%} accuracy. " if latest else "No touch trials. ")
    _notify(
        f"URGENT: {subject_name} has remained on {TOUCH_TASK} for more than "
        f"{alert_days} days (assigned {assigned:%Y-%m-%d %H:%M}). " + performance +
        f"Return criteria: at least {return_trials} valid trials and "
        f"{return_accuracy:.0%} accuracy in one "
        "calendar day. Please discuss with Alex whether to reduce the criteria. "
        "Criteria have NOT been reduced automatically.", subject_name,
    )
    state["last_alert_date"] = now.date().isoformat()


def run_daily_automatic_water_check(check_date):
    criteria = touch_criteria()
    days_to_check = criteria["AUTOMATIC_WATER_DAYS_TO_CHECK"]
    trial_threshold = criteria["AUTOMATIC_WATER_TRIAL_THRESHOLD"]
    cooldown_days = criteria["AUTOMATIC_WATER_TOUCH_COOLDOWN_DAYS"]
    # Examine each preceding COMPLETE calendar day independently.
    days = [check_date - timedelta(days=i)
            for i in range(days_to_check, 0, -1)]
    excluded = set(getattr(settings, "AUTOMATIC_WATER_EXCLUDED_SUBJECTS", ["m3"]))
    excluded.update(getattr(settings, "INACTIVE_SUBJECTS", []))
    states = _read_states()
    changed = False
    for name in _active_subject_names():
        if name in excluded:
            continue
        subject = utils.subjects.read_last_value_excluding(
            "name", name, "task", ["manual_water", "control_weight", "basal_weight"]
        )
        if subject is None:
            _notify("Touch engagement check skipped: current record missing", name)
            continue
        path = os.path.join(settings.SESSIONS_DIRECTORY, name, name + ".csv")
        try:
            history = pd.read_csv(path, sep=";", low_memory=False)
            if "date" not in history or "task" not in history:
                raise ValueError("session history needs date and task columns")
            rows = _trial_rows(history)
            dates = _dates(rows)
            if rows["date"].notna().any() and dates.isna().any():
                raise ValueError("unparseable trial dates")
        except Exception as error:
            _notify("Touch engagement check skipped: " + str(error), name)
            continue

        state = states.get(name)
        if subject.task == TOUCH_TASK:
            if state and "original" in state:
                _alert_overdue(name, state, history, datetime.now())
                _write_states(states)
            else:
                _notify("URGENT: Touch task has no saved original task state", name)
            continue
        if subject.task == "Automatic_Water":
            # Preserve legacy one-session water assignments until they finish.
            continue

        counts = [int((dates == day).sum()) for day in days]
        if not all(count < trial_threshold for count in counts):
            continue
        # Assignment records enforce cooldown even if the rat never enters.
        cutoff = check_date - timedelta(days=cooldown_days)
        if (state and not state.get("assignment_pending", False) and
                datetime.fromisoformat(state["assigned_at"]).date() >= cutoff):
            continue
        if ((rows["task"] == TOUCH_TASK) & (dates >= cutoff)).any():
            continue
        # Also catch manual assignments with no trials, using subjects history.
        recent_assignment = any(
            getattr(item, "name", None) == name and
            getattr(item, "task", None) == TOUCH_TASK and
            pd.notna(pd.to_datetime(getattr(item, "date", None), errors="coerce")) and
            pd.to_datetime(item.date).date() >= cutoff
            for item in utils.subjects.items
        )
        if recent_assignment:
            continue

        states[name] = {"assigned_at": datetime.now().isoformat(),
                        "assignment_pending": True,
                        "original": subject.__dict__.copy()}
        _write_states(states)
        utils.subjects.add_new_item({
            "task": TOUCH_TASK, "stage": 2, "task_number": 1,
            "wait_seconds": 0.0, "block_size": 40, "block_number": 1,
            "block_trial_counter": 0, "block_correct_count": 0,
            "block_valid_count": 0, "block_accuracy": 0.0, "block_change": 0,
            "total_trials": 0, "stim_trials": "[]", "stim_trial_counter": 0,
            "last_stim_trial": 0, "last_two_stim": "[]",
            "stage_forward_change": 0, "stage_backward_change": 0,
            "moved_back_counter": 0, "prev_block_accuracy": -1.0,
            "last_block_accuracy": 0.0,
        }, item=subject)
        states[name]["assignment_pending"] = False
        _write_states(states)
        changed = True
        daily_counts = "; ".join(f"{day} = {count} trials"
                                 for day, count in zip(days, counts))
        _notify(f"{TOUCH_TASK} assigned at fixed stage 2 (9 cm blob): "
                + daily_counts +
                f" (each fewer than {trial_threshold}). "
                f"No touch task in previous {cooldown_days} days. "
                "Original task progression saved.", name)
    return changed


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
