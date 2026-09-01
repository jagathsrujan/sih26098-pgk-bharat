import pytest

from fsw.modes import ModeLadder


def test_ladder_pre_to_acq_to_guide():
    m = ModeLadder()
    assert m.mode == "pre"
    m.deadline_tick(49.9)
    assert m.mode == "pre"
    m.on_first_fix(t_e=46.0)
    assert m.mode == "acq" and m.next_guid == 46.0 + 2.0  # T_GUID_ENGAGE quirk
    # before engagement threshold: no steering
    assert not m.guidance_tick(46.5, sig_p=3.0, roll_ref_available=False, blind=False)
    # engaged but no roll reference: still acq
    assert not m.guidance_tick(47.5, sig_p=3.0, roll_ref_available=False, blind=False)
    # roll reference arrives -> guide, steer
    assert m.guidance_tick(48.0, sig_p=3.0, roll_ref_available=True, blind=False)
    assert m.mode == "guide"
    # blind path engages without roll reference
    m2 = ModeLadder()
    m2.on_first_fix(45.0)
    assert m2.guidance_tick(48.0, sig_p=2.0, roll_ref_available=False, blind=True)
    assert m2.mode == "guide"


def test_ladder_degraded_denied_resume():
    m = ModeLadder()
    m.on_first_fix(45.0)
    m.guidance_tick(47.0, 3.0, True, False)
    assert m.mode == "guide"
    # sigma > degraded threshold (but < denied) -> degraded, still steers
    assert m.guidance_tick(50.0, 13.0, True, False)
    assert m.mode == "degraded"
    # 3 consecutive hard rejects in guide -> degraded (fix path)
    m3 = ModeLadder()
    m3.on_first_fix(45.0)
    m3.guidance_tick(47.0, 3.0, True, False)
    m3.on_fix_result(False)
    m3.on_fix_result(False)
    m3.on_fix_result(False)
    assert m3.mode == "degraded"
    # accepted fix resets the counter
    m3.on_fix_result(True)
    assert m3.hard_rej == 0
    # sigma > denied -> denied (neutral coast)
    assert not m.guidance_tick(52.0, 26.0, True, False)
    assert m.mode == "denied"
    # still denied between thresholds
    assert not m.guidance_tick(53.0, 9.9, True, False)
    # resume below 8 -> guide AND steering resumes on the same tick
    assert m.guidance_tick(54.0, 7.5, True, False)
    assert m.mode == "guide"


def test_ladder_deadline_ballistic():
    m = ModeLadder()
    m.deadline_tick(50.0)
    assert m.mode == "ballistic"
    # ballistic never re-enters via deadline
    m.deadline_tick(60.0)
    assert m.mode == "ballistic"


def test_r_floor_by_mode():
    m = ModeLadder()
    assert m.r_floor() == 1.0
    m.on_first_fix(45.0)
    assert m.r_floor() == 2.0
    m.mode = "degraded"
    assert m.r_floor() == 4.0
    m.mode = "denied"
    assert m.r_floor() == 16.0
