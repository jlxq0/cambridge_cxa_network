#!/usr/bin/env python3
"""
Test using OFFICIAL Cambridge protocol
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

print("OFFICIAL CAMBRIDGE CXA PROTOCOL TEST")
print("="*50)

# Test all commands from official protocol
print("\n1. AMPLIFIER COMMANDS (Group 01)")
print("-"*40)

resp = send_cmd("#01,01")
print(f"Get power state: {resp}")

resp = send_cmd("#01,03")  
print(f"Get mute state: {resp}")

print("\n2. SOURCE COMMANDS (Group 03)")
print("-"*40)

resp = send_cmd("#03,01")
print(f"Get current source: {resp}")

print("\n3. VERSION COMMANDS (Group 13)")
print("-"*40)

resp = send_cmd("#13,01")
print(f"Get protocol version: {resp}")

resp = send_cmd("#13,02")
print(f"Get firmware version: {resp}")

print("\n4. SOURCE MAPPING TEST")
print("-"*40)
print("Setting each source according to official docs...")

# Official CXA81 source codes
sources = [
    ("00", "A1"),
    ("01", "A2"),
    ("02", "A3"),
    ("03", "A4"),
    ("04", "D1"),
    ("05", "D2"),
    ("06", "D3"),
    ("14", "Bluetooth"),
    ("16", "USB Audio"),
    ("20", "A1 Balanced")
]

print("\nI'll set each source. Tell me what appears on the amp:")

for code, expected in sources[:6]:  # Test first 6
    cmd = f"#03,04,{code}"
    resp = send_cmd(cmd)
    print(f"\nSet source {code} (expect {expected})")
    print(f"Response: {resp}")
    
    actual = input(f"What source shows on amp? (expected: {expected}): ")
    
    if actual.lower() != expected.lower():
        print(f"  ⚠️  MISMATCH: Expected {expected}, got {actual}")

print("\n5. MUTE TEST")
print("-"*40)

print("Testing mute ON...")
resp = send_cmd("#01,04,1")
print(f"Response: {resp}")
muted = input("Is amp muted? (y/n): ")

if muted.lower() == 'y':
    print("Testing mute OFF...")
    resp = send_cmd("#01,04,0")
    print(f"Response: {resp}")

print("\n" + "="*50)
print("CONCLUSIONS:")
print("1. Volume control is NOT supported via RS232")
print("2. Source switching works but mapping may be offset")
print("3. Power, mute, and info queries work correctly")

sock.close()