#!/usr/bin/env python3
"""
Final volume discovery - check all responses
"""

import socket
import time

HOST = "10.0.0.24"
PORT = 8899

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect((HOST, PORT))

def send(cmd):
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
    try:
        sock.settimeout(1)
        resp = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        return resp
    except:
        return None

print("FINAL VOLUME DISCOVERY")
print("="*50)

# We know these commands:
# #11,02,XX sets volume
# #11,06 returns model
# #11,08 returns #12,08,1
# #13,01 returns #14,01,1.1 (firmware?)

print("\n1. Set different volumes and check what changes...")
print("-"*50)

# Set volume and check all query commands
test_volumes = [20, 40, 60]

for vol in test_volumes:
    print(f"\nSetting volume to {vol}...")
    send(f"#11,02,{vol:02d}")
    time.sleep(1)
    
    # Check all queries that gave responses
    queries = [
        ("#11,01", "11,01"),
        ("#11,03", "11,03"),
        ("#11,04", "11,04"), 
        ("#11,05", "11,05"),
        ("#11,07", "11,07"),
        ("#11,08", "11,08"),
        ("#11,09", "11,09"),
        ("#12,01", "12,01"),
        ("#13,01", "13,01"),
    ]
    
    for cmd, desc in queries:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"  {desc}: {resp}")

print("\n2. Try Cambridge Edge volume commands...")
print("-"*50)

# Edge uses different protocol
edge_patterns = [
    ("#2,5", "Edge vol query"),
    ("#1,5", "Edge vol query alt"),
    ("#11", "Simple 11"),
    ("#12", "Simple 12"),
]

for cmd, desc in edge_patterns:
    resp = send(cmd)
    if resp:
        print(f"{desc}: {cmd} -> {resp}")

print("\n3. Try increment with no parameters...")
print("-"*50)

# Some devices use parameterless inc/dec
inc_patterns = [
    ("#11,02", "Vol cmd no param"),
    ("#11,03", "Next after vol set"),
    ("#11,04", "Two after vol set"),
    ("#10,01", "Group 10 cmd 1"),
    ("#10,02", "Group 10 cmd 2"),
]

print("Current volume should be 60")
for cmd, desc in inc_patterns:
    resp = send(cmd)
    if resp and not resp.startswith("#00"):
        print(f"{desc}: {cmd} -> {resp}")
        print("  >> Check if volume changed")
        time.sleep(1)

print("\n4. WORKING PROTOCOL SUMMARY:")
print("-"*50)

summary = """
POWER:
  Query:    #01,01    -> #02,01,1 (on) or #02,01,0 (off)
  On:       #01,11    -> (power turns on)
  Off:      #01,12    -> (power turns off)

SOURCE:
  Query:    #03,01    -> #04,01,XX (XX=source code)
  Set:      #03,02,XX -> #04,01,XX (confirms new source)

VOLUME:
  Set:      #11,02,XX -> #12,02 (XX=00-96)
  Query:    ??? (not found yet)
  Up:       ??? (not found yet)
  Down:     ??? (not found yet)

MUTE:
  On:       #1,04,1   -> #02,03,1
  Off:      #1,04,0   -> #02,03,0

INFO:
  Model:    #11,06    -> #12,06,CXA81
  Unknown1: #11,08    -> #12,08,1
  Unknown2: #11,09    -> #12,09
  Firmware: #13,01    -> #14,01,1.1
"""

print(summary)

sock.close()