#!/usr/bin/env python3
"""
Test all source codes to find correct mappings
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

print("SOURCE MAPPING TEST")
print("="*40)

# Get current source
current = send_cmd("#03,01")
print(f"Current source: {current}\n")

# Test setting each source and see what we get back
test_sources = [
    ("00", "XLR/A1?"),
    ("01", "A1?"),
    ("02", "A2?"),
    ("03", "A3?"),
    ("04", "A4?"),
    ("05", "D1?"),
    ("06", "D2?"),
    ("07", "D3?"),
    ("14", "Bluetooth?"),
    ("16", "USB?"),
    ("20", "Unknown?"),
]

print("Testing source switching...")
print("-"*40)

found_sources = {}

for code, name in test_sources:
    cmd = f"#03,02,{code}"
    resp = send_cmd(cmd)
    
    if resp and resp.startswith("#04,01,"):
        actual_code = resp.split(",")[2] if len(resp.split(",")) > 2 else "??"
        print(f"Set source {code} ({name}) -> Response: {resp}")
        print(f"  Actual code returned: {actual_code}")
        
        # Ask user what source this is
        print(f"  >> CHECK YOUR AMP: What source is displayed now?")
        time.sleep(2)
        
        found_sources[actual_code] = f"Code {actual_code}"

print("\n" + "="*40)
print("FOUND SOURCE CODES:")
for code, desc in sorted(found_sources.items()):
    print(f"  {code}: {desc}")

# Return to D2
print("\nReturning to D2...")
send_cmd("#03,02,06")

sock.close()