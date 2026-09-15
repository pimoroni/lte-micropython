# Changelog

Unreleased
----------

* Hold RESET low for 2.5s so the module reliably restarts
* Treat `+CME ERROR:` and `+CMS ERROR:` replies as terminal, raising the module's text instead of timing out
* Disable echo in `_wait_ready` so state reads work after bring-up, not only after `connect()`
* Return `None` from `signal_quality()` for the `99` "no signal" sentinel instead of a bogus positive dBm

1.0.0
-----

* Initial release, imported from pimoroni-pico `micropython/modules_py/lte.py` (088bc15a)
