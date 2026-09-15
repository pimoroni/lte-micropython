import pytest


def make_lte(uart, reset_pin, responses=None, **kwargs):
    from lte import LTE

    if responses is not None:
        uart.responses = responses
    kwargs.setdefault("skip_reset", True)
    return LTE("test.apn", uart=uart, reset_pin=reset_pin, **kwargs)


def test_reset_pulse_holds_low_for_datasheet_duration(clock, uart, reset_pin):
    make_lte(uart, reset_pin, skip_reset=False)

    assert reset_pin.values == [0, 1]
    assert clock.sleeps == [2.5]


def test_skip_reset_leaves_reset_alone(uart, reset_pin):
    make_lte(uart, reset_pin, skip_reset=True)

    assert reset_pin.values == []


def test_signal_quality_parses_rssi(uart, reset_pin):
    lte = make_lte(uart, reset_pin, {"AT+CSQ": [b"+CSQ: 22,99", b"OK"]})

    assert lte.signal_quality() == -69


def test_signal_quality_no_signal_returns_sentinel(uart, reset_pin):
    lte = make_lte(uart, reset_pin, {"AT+CSQ": [b"+CSQ: 99,99", b"OK"]})

    # Baseline behaviour: the 99 "unknown" sentinel is converted like a reading.
    assert lte.signal_quality() == 85


def test_signal_quality_on_error_returns_none(uart, reset_pin):
    lte = make_lte(uart, reset_pin, {"AT+CSQ": [b"ERROR"]})

    assert lte.signal_quality() is None


def test_iccid_returns_whole_response_line(uart, reset_pin):
    lte = make_lte(uart, reset_pin, {"AT+CICCID": [b"+ICCID: 89882280666142410640", b"OK"]})

    # Baseline behaviour: the raw line is returned, prefix and all.
    assert lte.iccid() == "+ICCID: 89882280666142410640"


def test_iccid_on_cme_error_returns_none(uart, reset_pin):
    lte = make_lte(uart, reset_pin, {"AT+CICCID": [b"+CME ERROR: SIM not inserted"]})

    # Baseline behaviour: +CME ERROR is not terminal, so the read times out and
    # iccid() swallows the CellularError.
    assert lte.iccid() is None


def test_send_at_command_raises_on_error(uart, reset_pin):
    from lte import CellularError

    lte = make_lte(uart, reset_pin, {"AT+CFUN=1": [b"ERROR"]})

    with pytest.raises(CellularError):
        lte._send_at_command("AT+CFUN=1")
