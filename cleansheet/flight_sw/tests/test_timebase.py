import fsw
from fsw.timebase import Scheduler


def test_fixed_rate_dispatch_order_and_periods():
    calls = []
    s = Scheduler()
    s.add("gnss", 1.0, lambda t, dt: calls.append(("gnss", t)), priority=0)
    s.add("ctrl", 0.025, lambda t, dt: calls.append(("ctrl", t)), priority=1)
    s.add("guide", 1.0, lambda t, dt: calls.append(("guide", t)), priority=2)
    # tick 0: all due at t=0, dispatched in priority order
    ran = s.run(0.0, 0.025)
    assert ran == ["gnss", "ctrl", "guide"]
    # advance 0.025: only ctrl due again
    ran = s.run(0.025, 0.025)
    assert ran == ["ctrl"]
    # advance to 1.0: gnss + ctrl + guide due on the shared boundary,
    # dispatched in (next_due, priority) order
    calls.clear()
    for i in range(1, 41):
        s.run(round(i * 0.025, 6), 0.025)
    names = [c[0] for c in calls]
    assert names.count("gnss") == 1
    assert names.count("guide") == 1
    assert names.count("ctrl") == 39  # ticks i=2..40 (t=0.025 was served pre-clear)
    at_boundary = [c for c in calls if abs(c[1] - 1.0) < 1e-9]
    assert [c[0] for c in at_boundary] == ["gnss", "ctrl", "guide"]


def test_scheduler_is_registration_static():
    s = Scheduler()
    s.add("a", 0.1, lambda t, dt: None)
    try:
        s.add("a", 0.2, lambda t, dt: None)
        raise AssertionError("duplicate registration must fail")
    except ValueError:
        pass
    assert [t.name for t in s.tasks()] == ["a"]


def test_flightcomputer_registers_expected_tasks():
    fc = fsw.FlightComputer(cd_cal=0.2115, rates=fsw.COSIM_RATES)
    names = [t.name for t in fc.sched.tasks()]
    assert names == ["gnss", "ctrl", "anchor", "fit", "predict", "deadline", "guide"]
    # deployment default rates differ from the co-sim pairing rates
    fc2 = fsw.FlightComputer(cd_cal=0.2115)
    periods = {t.name: t.period for t in fc2.sched.tasks()}
    assert periods["predict"] == 0.01
    assert periods["ctrl"] == 0.0025
    assert periods["gnss"] == 1.0
