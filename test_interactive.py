#!/usr/bin/env python3
"""
Interactive test to discover the actual protocol
"""

import socket
import time
import sys

HOST = "10.0.0.24"
PORT = 8899

def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((HOST, PORT))
    return sock

def send_cmd(sock, cmd):
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

def ask_user(question):
    """Ask user a question and wait for response"""
    response = input(f"\n{question}\n> ")
    return response.strip()

print("CAMBRIDGE CXA INTERACTIVE PROTOCOL TEST")
print("="*50)
print("I will send commands and ask you what happens.")
print("Please watch your amplifier and answer accurately.")
print("="*50)

sock = connect()
print("✓ Connected to amplifier")

# Test 1: Current State
print("\n" + "="*50)
print("TEST 1: CURRENT STATE")
print("="*50)

resp = send_cmd(sock, "#03,01")
print(f"Source query response: {resp}")
source = ask_user("What source is displayed on your amp? (e.g., D1, D2, A1, USB, etc.)")

resp = send_cmd(sock, "#01,01")
print(f"Power query response: {resp}")
power = ask_user("Is the amp ON or in STANDBY?")

# Test 2: Source Switching
print("\n" + "="*50)
print("TEST 2: SOURCE SWITCHING")
print("="*50)
print("I'll try to change sources. Tell me what happens.")

sources_to_test = [
    ("01", "Trying source code 01"),
    ("02", "Trying source code 02"),
    ("03", "Trying source code 03"),
    ("04", "Trying source code 04"),
    ("05", "Trying source code 05"),
    ("06", "Trying source code 06"),
]

source_map = {}

for code, desc in sources_to_test:
    print(f"\n{desc}...")
    resp = send_cmd(sock, f"#03,02,{code}")
    print(f"Response: {resp}")
    
    actual_source = ask_user("What source is now displayed? (or 'nothing' if no change)")
    if actual_source.lower() != 'nothing':
        source_map[code] = actual_source
    
    cont = ask_user("Continue with more sources? (y/n)")
    if cont.lower() != 'y':
        break

# Test 3: Volume Control
print("\n" + "="*50)
print("TEST 3: VOLUME CONTROL")
print("="*50)

print("\nI'll try different volume commands. Tell me if you hear/see changes.")

# Test the known volume command
print("\nSetting volume to 20...")
resp = send_cmd(sock, "#11,02,20")
print(f"Response: {resp}")
vol_change = ask_user("Did the volume change? (y/n/number if you can see it)")

print("\nSetting volume to 30...")
resp = send_cmd(sock, "#11,02,30")
print(f"Response: {resp}")
vol_change2 = ask_user("Did the volume change to 30? (y/n/what you see)")

print("\nSetting volume to 25...")
resp = send_cmd(sock, "#11,02,25")
print(f"Response: {resp}")
vol_change3 = ask_user("Did the volume change to 25? (y/n/what you see)")

# Test 4: Try to find volume query
print("\n" + "="*50)
print("TEST 4: FINDING VOLUME QUERY")
print("="*50)
print("Trying to find a command that returns current volume...")

vol_queries = [
    "#11,01",
    "#11,03",
    "#11,04",
    "#11,05",
    "#10,01",
    "#10,02",
    "#12,01",
    "#12,02",
]

for cmd in vol_queries:
    resp = send_cmd(sock, cmd)
    if resp and not resp.startswith("#00"):
        print(f"\n{cmd} -> {resp}")
        is_volume = ask_user("Could this be volume info? (y/n/maybe)")
        if is_volume.lower() in ['y', 'yes', 'maybe']:
            print("  ✓ Possible volume query found!")
            break

# Test 5: Mute
print("\n" + "="*50)
print("TEST 5: MUTE CONTROL")
print("="*50)

print("\nTesting mute ON...")
resp = send_cmd(sock, "#1,04,1")
print(f"Response: {resp}")
muted = ask_user("Is the amp now MUTED? (y/n)")

if muted.lower() == 'y':
    print("\nTesting mute OFF...")
    resp = send_cmd(sock, "#1,04,0")
    print(f"Response: {resp}")
    unmuted = ask_user("Is the amp now UNMUTED? (y/n)")

# Summary
print("\n" + "="*50)
print("TEST SUMMARY")
print("="*50)

print("\nSource mappings found:")
for code, source in source_map.items():
    print(f"  Code {code} = {source}")

print("\nVolume control:")
print(f"  #11,02,XX command works: {vol_change}")

print("\nMute control:")
print(f"  Mute commands work: {muted}")

# Save results
save = ask_user("\nSave results to file? (y/n)")
if save.lower() == 'y':
    with open("protocol_results.txt", "w") as f:
        f.write("Cambridge CXA Protocol Test Results\n")
        f.write("="*40 + "\n\n")
        f.write("Source Mappings:\n")
        for code, source in source_map.items():
            f.write(f"  {code}: {source}\n")
        f.write("\nNotes:\n")
        f.write(f"Initial source: {source}\n")
        f.write(f"Volume control works: {vol_change}\n")
        f.write(f"Mute works: {muted}\n")
    print("✓ Results saved to protocol_results.txt")

sock.close()
print("\n✓ Test complete!")