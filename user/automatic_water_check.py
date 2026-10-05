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


RETURN_FIELDS = ['task', 'stage', 'substage', 'substage_bias', 'wait_seconds', 'stim_dur_ds', 'stim_dur_dm', 'stim_dur_dl', 'choice', 'block', 'conditions', 'completed_conditions', 'current_condition', 'repetition', 'current_repetition', 'trial_counter', 'stim_trial', 'stim_trials', 'stim_trial_counter', 'ror', 'completed_ror', 'current_ror', 'trial_counter_ror', 'moved_back_counter', 'block_size', 'block_trial_counter', 'block_accuracy', 'block_number', 'ror_change', 'block_change', 'last_stim_trial', 'last_condition_trial', 'total_trials', 'block_correct_count', 'block_valid_count', 'block_stim_correct_count_1', 'block_stim_valid_count_1', 'block_stim_accuracy_1', 'block_stim_correct_count_2', 'block_stim_valid_count_2', 'block_stim_accuracy_2', 'condition_trial_counter', 'stage_forward_change', 'stage_backward_change', 'task_number', 'last_forward_stage', 'last_backward_stage', 'reward_frequency', 'reward_db', 'reward_duration', 'stage_sequence', 'last_stage_trial', 'stage_sequence_counter', 'substage_counter_1', 'substage_counter_2', 'substage_counter_3', 'substage_counter_4', 'substage_counter_5', 'substage_counter_6', 'substage_counter_7', 'substage_counter_8', 'substage_counter_9', 'substage_counter_10', 'substage_counter_11', 'group', 'pair', 'prev_block_accuracy', 'last_block_accuracy', 'last_two_stim', 'unrewarded_list', 'pr_carry_tone', 'pr_carry_pending', 'consecutive_good_blocks']

TOUCH_TASK = "Automatic_Water_Touch"


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
    assigned = datetime.fromisoformat(state["assigned_at"])
    if now - assigned <= timedelta(days=3):
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
        f"3 days (assigned {assigned:%Y-%m-%d %H:%M}). " + performance +
        "Return criteria: at least 80 valid trials and 80% accuracy in one "
        "calendar day. Please discuss with Alex whether to reduce the criteria. "
        "Criteria have NOT been reduced automatically.", subject_name,
    )
    state["last_alert_date"] = now.date().isoformat()


def select_touch_task(history, subject, defaults):
    states = _read_states()
    name = str(subject.name)
    state = states.get(name)
    if not state or "original" not in state:
        # A manually assigned intervention cannot safely reconstruct a subject
        # record from trial history. Keep the task fixed and request review.
        _notify("URGENT: Missing saved original task for " + TOUCH_TASK +
                ". Review this subject before restoring progress.", name)
        values = dict(defaults)
    else:
        assigned = datetime.fromisoformat(state["assigned_at"])
        stats = _touch_day_stats(history, assigned)
        qualified = [item for item in stats if item[1] >= 80 and item[2] >= 0.8]
        if qualified:
            values = dict(defaults)
            values.update(state["original"])
            # Keep the snapshot until the caller durably writes the subject.
            # Repeating selection after a failed write remains safe.
            day, trials, accuracy = qualified[-1]
            _notify(f"{TOUCH_TASK} return criteria met on {day}: "
                    f"{trials} valid trials, {accuracy:.1%} accuracy. "
                    f"Restoring {values['task']}, stage {values['stage']}, "
                    "with saved progression.", name)
            values["wait_seconds"] = 3600 * settings.TIME_TO_ENTER
            return tuple(values[field] for field in RETURN_FIELDS)
        _alert_overdue(name, state, history, datetime.now())
        _write_states(states)
        values = dict(defaults)

    values.update(task=TOUCH_TASK, stage=2, task_number=1,
                  stage_forward_change=0, stage_backward_change=0)
    return tuple(values[field] for field in RETURN_FIELDS)


def run_daily_automatic_water_check(check_date):
    # Always examine the two preceding COMPLETE days independently.
    days = [check_date - timedelta(days=i) for i in (2, 1)]
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
        if not all(count < 40 for count in counts):
            continue
        # Assignment records enforce cooldown even if the rat never enters.
        cutoff = check_date - timedelta(days=7)
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
        _notify(f"{TOUCH_TASK} assigned at fixed stage 2 (9 cm blob): "
                f"{days[0]} = {counts[0]} trials; {days[1]} = {counts[1]} trials "
                "(each fewer than 40). No touch task in previous 7 days. "
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
