#!/usr/bin/env python3
"""
Test the Cambridge CXA integration commands
"""

import socket
import time

HOST = "10.0.0.24"
PORT = 8899

print("Cambridge CXA Integration Test")
print("="*40)

# Connect
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)

try:
    sock.connect((HOST, PORT))
    print(f"✓ Connected to {HOST}:{PORT}")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)

def send_cmd(cmd):
    """Send command and get response"""
    if not cmd.endswith('\r'):
        cmd += '\r'
    
    # Clear buffer
    sock.settimeout(0.1)
    try:
        while sock.recv(1024):
            pass
    except:
        pass
    
    # Send
    sock.send(cmd.encode())
    time.sleep(0.3)
    
    # Read response
    sock.settimeout(1)
    try:
        resp = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        return resp
    except:
        return None

print("\n1. Testing basic commands...")
print("-"*40)

# Test power status
resp = send_cmd("#01,01")
print(f"Power status: #01,01 -> {resp}")
if resp == "#02,01,1":
    print("  ✓ Power is ON")
elif resp == "#02,01,0":
    print("  ✓ Power is OFF/Standby")

# Test source query  
resp = send_cmd("#03,01")
print(f"Current source: #03,01 -> {resp}")
if resp and resp.startswith("#04,01,"):
    source_code = resp.split(",")[2]
    sources = {"01":"A1", "02":"A2", "03":"A3", "04":"A4", 
               "05":"D1", "06":"D2", "07":"D3", "14":"BT", "16":"USB"}
    print(f"  ✓ Source: {sources.get(source_code, 'Unknown')}")

# Test model query
resp = send_cmd("#11,06")
print(f"Model: #11,06 -> {resp}")
if resp and resp.startswith("#12,06,"):
    model = resp.split(",", 2)[2]
    print(f"  ✓ Model: {model}")

# Test firmware
resp = send_cmd("#13,01")
print(f"Firmware: #13,01 -> {resp}")
if resp and resp.startswith("#14,01,"):
    fw = resp.split(",", 2)[2]
    print(f"  ✓ Firmware: {fw}")

print("\n2. Testing control commands...")
print("-"*40)

# Set volume to 30
print("Setting volume to 30...")
resp = send_cmd("#11,02,30")
print(f"Volume set: #11,02,30 -> {resp}")
if resp == "#12,02":
    print("  ✓ Volume command accepted")

# Test mute
print("\nTesting mute...")
resp = send_cmd("#1,04,1")  # Mute on
print(f"Mute on: #1,04,1 -> {resp}")
time.sleep(1)

resp = send_cmd("#1,04,0")  # Mute off  
print(f"Mute off: #1,04,0 -> {resp}")

print("\n3. Integration command summary:")
print("-"*40)
print("Working commands for media_player.py:")
print("  Power query:  #01,01")
print("  Power on:     #01,11") 
print("  Power off:    #01,12")
print("  Source query: #03,01")
print("  Source set:   #03,02,XX")
print("  Volume set:   #11,02,XX (00-96)")
print("  Mute on:      #1,04,1")
print("  Mute off:     #1,04,0")
print("  Model query:  #11,06")
print("  Firmware:     #13,01")

sock.close()
print("\n✓ Test complete")