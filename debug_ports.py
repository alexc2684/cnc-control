import serial.tools.list_ports
import os

print(f"OS: {os.name}")
ports = list(serial.tools.list_ports.comports())
print(f"Found {len(ports)} ports:")
for p in ports:
    print(f"  {p.device} - {p.description} - {p.hwid}")

print("\nPorts matching 'ttyUSB':")
usb_ports = list(serial.tools.list_ports.grep("ttyUSB"))
for p in usb_ports:
    print(f"  {p.device}")
