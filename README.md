# LTE MicroPython

PPP networking driver for SIMCom A76xx cellular modules over UART, as used on the
[Pimoroni Clipper](https://shop.pimoroni.com/products/clipper) and other SP/CE hosts.

It brings the module up, registers on the network, and hands MicroPython a `network.PPP`
interface for standard socket networking.

## Installing

Install with `mip`:

```python
import mip
mip.install("github:pimoroni/lte-micropython/package.json")
```

Or with Thonny, via Tools -> Manage Packages, searching for `lte-micropython`.

## Getting Started

```python
from lte import LTE

lte = LTE(apn="your.apn.here")
lte.start_ppp()
```

`LTE()` resets the module and configures the UART. `start_ppp()` waits for the module,
switches to a faster baud rate, registers on the network, and starts PPP. It returns the
interface's `ifconfig()` tuple once connected.

Pass `skip_reset=True` to leave a running module untouched, or supply your own `uart` and
`reset_pin` to override the SP/CE defaults (UART0, TX 32, RX 33, RESET 35).

## Networking

Once `start_ppp()` returns, use `socket` as normal:

```python
import socket

addr = socket.getaddrinfo("example.com", 80)[0][-1]
sock = socket.socket()
sock.connect(addr)
sock.send(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
print(sock.recv(512))
sock.close()
```

Call `stop_ppp()` to drop the link and return the UART to command mode.

## Status and Diagnostics

```python
lte.signal_quality()   # RSSI in dBm, or None if unknown
lte.iccid()            # SIM ICCID
lte.status()           # (AT+CEREG?, AT+CGREG?) registration replies
```

## The Netlight LED

Mirror the module's netlight onto an LED by passing `netlight_led` (a `Pin` or PWM-like
object with `.value()`):

```python
from machine import Pin
lte = LTE(apn="your.apn.here", netlight_led=Pin("LED", Pin.OUT))
```
