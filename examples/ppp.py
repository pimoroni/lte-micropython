import socket

from lte import LTE

lte = LTE(apn="your.apn.here")

print("Connecting...")
print(lte.start_ppp())

print(f"Signal: {lte.signal_quality()} dBm")

addr = socket.getaddrinfo("example.com", 80)[0][-1]
sock = socket.socket()
sock.connect(addr)
sock.send(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
print(sock.recv(512))
sock.close()

lte.stop_ppp()
