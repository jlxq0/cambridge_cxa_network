#!/usr/bin/env python3
"""
Debug the integration issues
"""

import socket
import time

HOST = "10.0.0.24"
PORT = 8899

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect((HOST, PORT))

def send_cmd(cmd):
    if not cmd.endswith('\r'):
        cmd += '\r'
    sock.settimeout(0.1)
    try:
        while sock.recv(1024):
            pass
    except:
        pass
    sock.send(cmd.encode())
    time.sleep(0.3)
    sock.settimeout(1)
    try:
        return sock.recv(1024).decode('utf-8', errors='ignore').strip()
    except:
        return None

print("DEBUG: Cambridge CXA Integration Issues")
print("="*40)

# 1. Check actual source
print("\n1. Current source check:")
resp = send_cmd("#03,01")
print(f"Source query response: {resp}")
if resp and resp.startswith("#04,01,"):
    code = resp.split(",")[2] if len(resp.split(",")) > 2 else "??"
    print(f"Source code: {code}")

# 2. Test volume commands
print("\n2. Volume test:")
print("Setting volume to 25...")
resp = send_cmd("#11,02,25")
print(f"Response: {resp}")
time.sleep(1)

print("Setting volume to 35...")
resp = send_cmd("#11,02,35")
print(f"Response: {resp}")
time.sleep(1)

print("Setting volume to 30...")
resp = send_cmd("#11,02,30")
print(f"Response: {resp}")

# 3. Test source switching
print("\n3. Source switching test:")
sources = {
    "A1": "01",
    "A2": "02", 
    "D1": "05",
    "D2": "06"
}

current = send_cmd("#03,01")
print(f"Current source: {current}")

print("\nTrying to switch to A1...")
resp = send_cmd("#03,02,01")
print(f"Set source response: {resp}")
time.sleep(1)

new_source = send_cmd("#03,01")
print(f"New source: {new_source}")

# 4. Check the mappings
print("\n4. Source mapping check:")
print("CXA81 should use these mappings:")
print("  00 = XLR/A1 Balanced")
print("  01 = A1")
print("  02 = A2") 
print("  05 = D1")
print("  etc.")

sock.close()
print("\n✓ Debug complete")