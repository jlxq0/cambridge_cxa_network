#!/usr/bin/env python3
"""
Find the volume control command
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
    time.sleep(0.5)
    sock.settimeout(1)
    try:
        return sock.recv(1024).decode('utf-8', errors='ignore').strip()
    except:
        return None

print("VOLUME COMMAND DISCOVERY")
print("="*50)
print("Listen to your amplifier - I'll try different volume commands")
print("Tell me if you hear the volume change!")
print("="*50)

# Set a baseline
print("\nFirst, let me set volume using different patterns...")
print("Listen carefully for volume changes!")

# Try different command patterns for volume
test_patterns = [
    # Pattern 1: Different groups
    ("#01,05,30", "Pattern 1: #01,05,30"),
    ("#02,05,30", "Pattern 2: #02,05,30"), 
    ("#03,05,30", "Pattern 3: #03,05,30"),
    ("#04,05,30", "Pattern 4: #04,05,30"),
    ("#05,02,30", "Pattern 5: #05,02,30"),
    
    # Pattern 2: CXN style
    ("#1,05,30", "CXN style: #1,05,30"),
    ("#1,06,30", "CXN alt: #1,06,30"),
    
    # Pattern 3: Simple volume
    ("#30", "Simple: #30"),
    ("#40", "Simple: #40"),
    
    # Pattern 4: Other groups
    ("#10,02,30", "Group 10: #10,02,30"),
    ("#12,02,30", "Group 12: #12,02,30"),
    ("#13,02,30", "Group 13: #13,02,30"),
    
    # Pattern 5: Try the failing one again
    ("#11,02,20", "Original (20): #11,02,20"),
    ("#11,02,40", "Original (40): #11,02,40"),
]

found_volume_cmd = None

for cmd, desc in test_patterns:
    print(f"\n{desc}")
    resp = send_cmd(cmd)
    print(f"Response: {resp}")
    
    change = input("Did volume change? (y/n/q to quit): ")
    if change.lower() == 'y':
        print("✓ FOUND VOLUME COMMAND!")
        found_volume_cmd = cmd.split(',')[0] + ',' + cmd.split(',')[1] + ','
        
        # Test different levels
        print("\nTesting different volume levels...")
        for vol in [20, 30, 40, 30]:
            test_cmd = found_volume_cmd + f"{vol:02d}"
            print(f"Setting volume to {vol}: {test_cmd}")
            resp = send_cmd(test_cmd)
            print(f"Response: {resp}")
            time.sleep(1)
        
        break
    elif change.lower() == 'q':
        break

if not found_volume_cmd:
    print("\n" + "="*50)
    print("TRYING VOLUME UP/DOWN COMMANDS")
    print("="*50)
    
    up_down_patterns = [
        ("#01,+", "Up pattern 1"),
        ("#01,-", "Down pattern 1"),
        ("#02,+", "Up pattern 2"),
        ("#02,-", "Down pattern 2"),
        ("#1,02", "CXN up"),
        ("#1,03", "CXN down"),
        ("#11,03", "Alt up"),
        ("#11,04", "Alt down"),
        ("#+", "Simple up"),
        ("#-", "Simple down"),
    ]
    
    for cmd, desc in up_down_patterns:
        print(f"\n{desc}: {cmd}")
        resp = send_cmd(cmd)
        print(f"Response: {resp}")
        
        change = input("Did volume change? (y/n): ")
        if change.lower() == 'y':
            print("✓ Found volume up/down command!")

print("\n" + "="*50)
if found_volume_cmd:
    print(f"VOLUME COMMAND FOUND: {found_volume_cmd}XX")
else:
    print("No volume command found yet")

sock.close()