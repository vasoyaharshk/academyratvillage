import datetime
import time


def now_seconds():
    return time.time()


def now_string():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def now_string_for_files():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def now_datetime():
    return datetime.datetime.now()


def now_time():
    return datetime.datetime.now().time()


def datetime_to_string(t):
    return t.strftime("%Y/%m/%d %H:%M:%S")


def string_to_datetime(time_string, delay):
    time0 = datetime.datetime.strptime(time_string, "%Y/%m/%d %H:%M:%S")
    time1 = datetime.timedelta(seconds=delay)
    return time0 + time1


def hour_minute_to_time(hour, minute):
    return datetime.time(hour, minute)


class Chrono:
    def __init__(self):
        self.init_time = time.time()

    def reset(self):
        self.init_time = time.time()

    def get_seconds(self):
        return time.time() - self.init_time

    def get_time_string(self):
        t = self.get_seconds()
        h = int(t / 3600)
        m = int((t - h * 3600) / 60)
        s = int(t - h * 3600 - m * 60)

        if h < 10:
            h = '0' + str(h)
        else:
            h = str(h)
        if m < 10:
            m = '0' + str(m)
        else:
            m = str(m)
        if s < 10:
            s = '0' + str(s)
        else:
            s = str(s)

        return h + ':' + m + ':' + s


class Timer:
    def __init__(self, timeup):
        self.init_time = time.time()
        self.timeup = timeup  # in seconds

    def reset(self):
        self.init_time = time.time()

    def get_remaining_time(self):
        seconds = self.init_time + self.timeup - time.time()

        if seconds < 0:
            return 0
        else:
            return seconds