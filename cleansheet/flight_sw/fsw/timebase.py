"""Fixed-rate task scheduler — the on-board timing skeleton.

Hard rule: no dynamic allocation patterns. Tasks are registered once at
construction with a fixed period and priority; dispatch order for tasks due on
the same tick is (next_due, priority) — fully deterministic.

Deployment rates (fsw/config.py): servo 400 Hz, sensors/roll 40 Hz, EKF predict
100 Hz, GNSS 1 Hz, guidance 1 Hz. The co-sim harness constructs the same task
set at the truth-step cadence for paired numerics (see FLIGHT_SOFTWARE.md).

Tasks that model free-running 1 Hz cadences anchored to in-flight events (the
guidance tick anchored to the first fix, GNSS arrival anchored to measurement
epochs) keep that cadence internally and self-gate — the scheduler only
guarantees they are offered a tick often enough.
"""


class Task:
    __slots__ = ("name", "period", "fn", "priority", "next_due", "runs")

    def __init__(self, name, period, fn, priority):
        self.name = name
        self.period = period
        self.fn = fn
        self.priority = priority
        self.next_due = 0.0
        self.runs = 0


class Scheduler:
    def __init__(self, eps=1e-9):
        self._tasks = []
        self._eps = eps

    def add(self, name, period, fn, priority=0):
        if any(t.name == name for t in self._tasks):
            raise ValueError(f"duplicate task name: {name}")
        self._tasks.append(Task(name, float(period), fn, int(priority)))

    def reset(self):
        for t in self._tasks:
            t.next_due = 0.0
            t.runs = 0

    def run(self, t, dt=None):
        """Dispatch every task whose next_due <= t (+eps), once, in
        (next_due, priority) order. Returns the names dispatched."""
        due = [task for task in self._tasks if task.next_due <= t + self._eps]
        due.sort(key=lambda task: (task.next_due, task.priority))
        ran = []
        for task in due:
            task.fn(t, dt)
            task.runs += 1
            task.next_due = t + task.period
            ran.append(task.name)
        return ran

    def tasks(self):
        return list(self._tasks)
