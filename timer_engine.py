import time
from enum import Enum


class TimerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class SessionType(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class TimerEngine:
    def __init__(self, on_tick, on_complete, schedule_fn, cancel_fn):
        self.on_tick = on_tick
        self.on_complete = on_complete
        self.schedule = schedule_fn
        self.cancel = cancel_fn

        self.state = TimerState.IDLE
        self.session_type = SessionType.WORK
        self.completed_pomodoros = 0
        self.long_break_interval = 4

        self.durations = {
            SessionType.WORK: 25 * 60,
            SessionType.SHORT_BREAK: 5 * 60,
            SessionType.LONG_BREAK: 15 * 60,
        }

        self._remaining = self.durations[SessionType.WORK]
        self._target_time = None
        self._timer_id = None
        self._started_at = None

    @property
    def remaining(self):
        return self._remaining

    @property
    def total_duration(self):
        return self.durations[self.session_type]

    @property
    def started_at(self):
        return self._started_at

    def start(self):
        if self.state != TimerState.IDLE:
            return
        self._remaining = self.durations[self.session_type]
        self._started_at = time.time()
        self._target_time = time.time() + self._remaining
        self.state = TimerState.RUNNING
        self.on_tick(self._remaining, self.session_type)
        self._schedule_tick()

    def pause(self):
        if self.state != TimerState.RUNNING:
            return
        if self._timer_id is not None:
            self.cancel(self._timer_id)
            self._timer_id = None
        self._remaining = max(0, int(self._target_time - time.time()))
        self._target_time = None
        self.state = TimerState.PAUSED

    def resume(self):
        if self.state != TimerState.PAUSED:
            return
        self._target_time = time.time() + self._remaining
        self.state = TimerState.RUNNING
        self._schedule_tick()

    def reset(self):
        if self._timer_id is not None:
            self.cancel(self._timer_id)
            self._timer_id = None
        self._remaining = self.durations[self.session_type]
        self._target_time = None
        self._started_at = None
        self.state = TimerState.IDLE
        self.on_tick(self._remaining, self.session_type)

    def skip(self):
        if self._timer_id is not None:
            self.cancel(self._timer_id)
            self._timer_id = None
        self._advance_session()
        self._remaining = self.durations[self.session_type]
        self._target_time = None
        self._started_at = None
        self.state = TimerState.IDLE
        self.on_tick(self._remaining, self.session_type)

    def set_durations(self, work, short_break, long_break):
        self.durations[SessionType.WORK] = work
        self.durations[SessionType.SHORT_BREAK] = short_break
        self.durations[SessionType.LONG_BREAK] = long_break
        if self.state == TimerState.IDLE:
            self._remaining = self.durations[self.session_type]
            self.on_tick(self._remaining, self.session_type)

    def _schedule_tick(self):
        self._timer_id = self.schedule(200, self._tick)

    def _tick(self):
        self._timer_id = None
        if self.state != TimerState.RUNNING:
            return

        self._remaining = max(0, round(self._target_time - time.time()))

        if self._remaining <= 0:
            self._remaining = 0
            self.on_tick(0, self.session_type)
            completed_type = self.session_type
            if completed_type == SessionType.WORK:
                self.completed_pomodoros += 1
            self.on_complete(completed_type)
            self._advance_session()
            self._remaining = self.durations[self.session_type]
            self._target_time = None
            self._started_at = None
            self.state = TimerState.IDLE
            self.on_tick(self._remaining, self.session_type)
        else:
            self.on_tick(self._remaining, self.session_type)
            self._schedule_tick()

    def _advance_session(self):
        if self.session_type == SessionType.WORK:
            if self.completed_pomodoros % self.long_break_interval == 0:
                self.session_type = SessionType.LONG_BREAK
            else:
                self.session_type = SessionType.SHORT_BREAK
        else:
            self.session_type = SessionType.WORK
