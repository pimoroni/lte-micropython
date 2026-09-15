# Changelog

Unreleased
----------

* Hold RESET low for 2.5s so the module reliably restarts
* Treat `+CME ERROR:` and `+CMS ERROR:` replies as terminal, raising the module's text instead of timing out

1.0.0
-----

* Initial release, imported from pimoroni-pico `micropython/modules_py/lte.py` (088bc15a)
