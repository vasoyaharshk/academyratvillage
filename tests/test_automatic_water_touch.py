"""Offline policy tests: no hardware, subject data, or Telegram network calls."""
import importlib.util
import ast
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class Subjects:
    def __init__(self, subject):
        self.items = [subject]

    def read_last_value_excluding(self, column, name, *args):
        return next(item for item in reversed(self.items) if item.name == name)

    def add_new_item(self, changes, item):
        self.items.append(types.SimpleNamespace(**{**vars(item), **changes}))


class TouchPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.settings = types.SimpleNamespace(
            DATA_DIRECTORY=self.tmp.name, SESSIONS_DIRECTORY=self.tmp.name,
            TIME_TO_ENTER=1, INACTIVE_SUBJECTS=[],
        )
        academy = types.ModuleType('academy')
        academy.telegram_bot = types.SimpleNamespace(
            alarm_finish_session=lambda *args: None,
            alarm_finish_session_details=lambda *args: None,
        )
        utils_module = types.ModuleType('academy.utils')
        utils_module.utils = types.SimpleNamespace()
        user = types.ModuleType('user')
        user.settings = self.settings
        modules = {'academy': academy, 'academy.utils': utils_module, 'user': user}
        self.module_patch = patch.dict(sys.modules, modules)
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)
        spec = importlib.util.spec_from_file_location(
            'water_check_test', ROOT / 'user/automatic_water_check.py')
        self.water = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.water)
        user.automatic_water_check = self.water
        wx = types.ModuleType('wx.lib.pubsub.py2and3')
        wx.print_ = print
        with patch.dict(sys.modules, {'wx.lib.pubsub.py2and3': wx}):
            spec = importlib.util.spec_from_file_location(
                'select_task_test', ROOT / 'user/select_task.py')
            self.select = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.select)
        self.messages = []
        self.water._notify = lambda message, name: self.messages.append((message, name))
        self.original = {field: 7 for field in self.select.RETURN_FIELDS}
        self.original.update(name='rat', task='Probability_Test', stage=5,
                             stim_trials='[1, 2]', reward_frequency=123.0)
        self.subject = types.SimpleNamespace(**self.original)
        self.subjects = Subjects(self.subject)
        utils_module.utils.subjects = self.subjects
        self.today = datetime.now().date()
        Path(self.tmp.name, 'rat').mkdir()

    def history(self, counts=(39, 39)):
        rows = []
        for offset, count in zip((2, 1), counts):
            for i in range(count):
                rows.append(dict(date=str(self.today-timedelta(days=offset)),
                                 task='Probability_Test', trial_result='correct',
                                 session=offset, trial=i, subject='rat',
                                 trial_length=1, TRIAL_START=i, TRIAL_END=i+1))
        return pd.DataFrame(rows)

    def save_history(self, history):
        history.to_csv(Path(self.tmp.name, 'rat/rat.csv'), sep=';', index=False)

    def assign(self):
        self.save_history(self.history())
        self.assertTrue(self.water.run_daily_automatic_water_check(self.today))
        return self.subjects.items[-1]

    def touch_rows(self, n=80, correct=64, day=None, session=3):
        return pd.DataFrame([dict(
            date=str(day or self.today), task=self.water.TOUCH_TASK,
            trial_result='correct' if i < correct else 'incorrect',
            session=session, trial=i, subject='rat', trial_length=1,
            TRIAL_START=i, TRIAL_END=i+1,
        ) for i in range(n)])

    def test_entry_requires_each_day_below_40(self):
        self.save_history(self.history((0, 40)))
        self.assertFalse(self.water.run_daily_automatic_water_check(self.today))
        assigned = self.assign()
        self.assertEqual((assigned.task, assigned.stage, assigned.task_number),
                         (self.water.TOUCH_TASK, 2, 1))
        self.assertEqual(self.water._read_states()['rat']['original'], self.original)

    def test_blank_rows_do_not_count_and_zero_days_qualify(self):
        history = self.history((1, 1))
        history['trial_result'] = None
        self.save_history(history)
        self.assertTrue(self.water.run_daily_automatic_water_check(self.today))

    def test_cooldown_counts_assignments_without_sessions(self):
        self.assign()
        self.subjects.items.append(self.subject)
        self.assertFalse(self.water.run_daily_automatic_water_check(self.today))
        states = self.water._read_states()
        states['rat']['assigned_at'] = str(self.today-timedelta(days=7))+'T00:00:00'
        self.water._write_states(states)
        self.assertFalse(self.water.run_daily_automatic_water_check(self.today))
        states['rat']['assigned_at'] = str(self.today-timedelta(days=8))+'T00:00:00'
        self.water._write_states(states)
        self.assertTrue(self.water.run_daily_automatic_water_check(self.today))

    def test_cooldown_checks_trial_history(self):
        history = self.history((1, 1))
        history.loc[0, 'task'] = self.water.TOUCH_TASK
        self.save_history(history)
        self.assertFalse(self.water.run_daily_automatic_water_check(self.today))

    def test_manual_assignment_without_trials_enforces_cooldown(self):
        manual = types.SimpleNamespace(**{
            **self.original, 'task': self.water.TOUCH_TASK,
            'date': str(self.today-timedelta(days=4))+' 12:00:00',
        })
        self.subjects.items = [manual, self.subject]
        self.save_history(self.history())
        self.assertFalse(self.water.run_daily_automatic_water_check(self.today))

    def test_failed_subject_assignment_can_retry_without_losing_snapshot(self):
        self.save_history(self.history())
        with patch.object(self.subjects, 'add_new_item', side_effect=OSError('disk')):
            with self.assertRaises(OSError):
                self.water.run_daily_automatic_water_check(self.today)
        self.assertEqual(self.water._read_states()['rat']['original'], self.original)
        self.assertTrue(self.water.run_daily_automatic_water_check(self.today))

    def test_misses_do_not_satisfy_valid_trial_return_threshold(self):
        assigned = self.assign()
        df = self.touch_rows(100, 79)
        df.loc[df.trial_result == 'incorrect', 'trial_result'] = 'miss'
        self.assertEqual(self.select.select_touch_task(df, assigned, self.original)[0],
                         self.water.TOUCH_TASK)

    def test_return_sums_sessions_and_preserves_all_fields(self):
        assigned = self.assign()
        df = pd.concat([self.touch_rows(40, 32), self.touch_rows(40, 32, session=4)])
        defaults = {field: -100 for field in self.select.RETURN_FIELDS}
        result = dict(zip(self.select.RETURN_FIELDS,
                          self.select.select_touch_task(df, assigned, defaults)))
        for field in self.select.RETURN_FIELDS:
            self.assertEqual(result[field], 3600 if field == 'wait_seconds'
                             else self.original[field])

    def test_no_return_for_79_trials_or_less_than_80_percent(self):
        assigned = self.assign()
        for df in (self.touch_rows(79, 79), self.touch_rows(80, 63)):
            result = dict(zip(self.select.RETURN_FIELDS,
                              self.select.select_touch_task(df, assigned, self.original)))
            self.assertEqual((result['task'], result['stage']), (self.water.TOUCH_TASK, 2))

    def test_trials_from_different_days_are_not_combined(self):
        assigned = self.assign()
        states = self.water._read_states()
        states['rat']['assigned_at'] = (datetime.now()-timedelta(days=2)).isoformat()
        self.water._write_states(states)
        df = pd.concat([self.touch_rows(40, 40, self.today-timedelta(days=1)),
                        self.touch_rows(40, 40)])
        result = self.select.select_touch_task(df, assigned, self.original)
        self.assertEqual(result[0], self.water.TOUCH_TASK)

    def test_overdue_alert_without_trials_once_per_day(self):
        self.assign()
        states = self.water._read_states()
        states['rat']['assigned_at'] = (datetime.now()-timedelta(days=3, seconds=1)).isoformat()
        self.water._write_states(states)
        self.messages.clear()
        self.water.run_daily_automatic_water_check(self.today)
        self.water.run_daily_automatic_water_check(self.today)
        self.assertEqual(sum('URGENT' in msg for msg, _ in self.messages), 1)
        self.assertEqual(self.subjects.items[-1].task, self.water.TOUCH_TASK)

    def test_full_select_task_bypasses_original_progression(self):
        assigned = self.assign()
        wx = types.ModuleType('wx.lib.pubsub.py2and3')
        wx.print_ = print
        with patch.dict(sys.modules, {'wx.lib.pubsub.py2and3': wx}):
            spec = importlib.util.spec_from_file_location(
                'select_task_test', ROOT / 'user/select_task.py')
            select = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(select)
        df = self.touch_rows()
        result = dict(zip(self.select.RETURN_FIELDS, select.select_task(df, assigned)))
        self.assertEqual(result['task'], self.original['task'])
        self.assertEqual(result['stage'], self.original['stage'])
        self.assertEqual(result['stage_forward_change'], self.original['stage_forward_change'])

    def test_task_clears_stale_stage_flags_before_stimulus(self):
        tree = ast.parse((ROOT / 'tasks/Automatic_Water_Touch.py').read_text())
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        main = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                    and node.name == 'main_loop')
        # Run the real beginning of main_loop through the fixed-stage guard,
        # stopping before hardware/stimulus operations.
        stop = next(i for i, node in enumerate(main.body)
                    if isinstance(node, ast.If) and
                    ast.unparse(node.test) == 'self.stage == 0')
        main.body = main.body[:stop]
        module = ast.Module(body=[main], type_ignores=[])
        namespace = {}
        exec(compile(ast.fix_missing_locations(module), '<stage guard>', 'exec'), namespace)
        task = types.SimpleNamespace(current_trial=1, block_change=0,
            stage=9, task_number=2, stage_forward_change=1, stage_backward_change=1)
        namespace['main_loop'](task)
        self.assertEqual((task.stage, task.task_number, task.stage_forward_change,
                          task.stage_backward_change), (2, 1, 0, 0))


if __name__ == '__main__':
    unittest.main()
