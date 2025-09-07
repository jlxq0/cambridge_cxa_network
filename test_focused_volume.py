#!/usr/bin/env python3
"""
Focused volume testing based on findings
"""

import socket
import time

HOST = "10.0.0.24"
PORT = 8899

def test():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((HOST, PORT))
    print("Connected - Testing CXA volume commands\n")
    
    def send(cmd):
        if not cmd.endswith('\r'):
            cmd += '\r'
        sock.send(cmd.encode())
        time.sleep(0.3)
        try:
            sock.settimeout(1)
            resp = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return resp
        except:
            return None
    
    print("1. Testing #1,XX commands (CXN style)...")
    print("-" * 50)
    
    # Test all #1,XX commands to map functionality
    for cmd in range(1, 30):
        command = f"#1,{cmd:02d}"
        resp = send(command)
        if resp and not resp.startswith("#00"):
            print(f"#1,{cmd:02d} -> {resp}")
    
    print("\n2. Testing volume set commands...")
    print("-" * 50)
    
    # Try different volume set patterns
    volume_patterns = [
        "Volume 20 - Pattern #1,05,20:",
        "Volume 30 - Pattern #1,05,30:", 
        "Volume 40 - Pattern #1,05,40:",
        "Volume 20 - Pattern #1,06,20:",
        "Volume 30 - Pattern #1,06,30:",
        "Volume 20 - Pattern #1,07,20:",
        "Volume 30 - Pattern #1,07,30:",
        "Volume 20 - Pattern #1,08,20:",
        "Volume 30 - Pattern #1,08,30:",
    ]
    
    for i in range(5, 15):
        for vol in [20, 30]:
            cmd = f"#1,{i:02d},{vol}"
            resp = send(cmd)
            if resp and not resp.startswith("#00"):
                print(f"✓ VOLUME SET: {cmd} -> {resp}")
                time.sleep(1)  # Wait to hear if volume changed
    
    print("\n3. Testing #2,XX group commands...")
    print("-" * 50)
    
    # Test group 2 which might be volume
    for cmd in range(1, 10):
        command = f"#2,{cmd:02d}"
        resp = send(command)
        if resp and not resp.startswith("#00"):
            print(f"#2,{cmd:02d} -> {resp}")
    
    print("\n4. Testing increment/decrement...")
    print("-" * 50)
    
    # We know #1,01 is power query, but let's test #1,02
    inc_dec = [
        ("#1,02", "Try #1,02"),
        ("#2,01", "Try #2,01"),
        ("#2,02", "Try #2,02"),
        ("#1,10", "Try #1,10"),
        ("#1,11", "Power on"), 
        ("#1,12", "Power off"),
    ]
    
    for cmd, desc in inc_dec:
        resp = send(cmd)
        print(f"{desc}: {cmd} -> {resp}")
    
    print("\n5. Testing Cambridge Audio BluOS commands...")
    print("-" * 50)
    
    # Some Cambridge products use these
    bluos_patterns = [
        ("#99", "Query all"),
        ("#11,01", "Alt vol query"),
        ("#11,02,30", "Alt vol set 30"),
        ("#12,01", "Alt pattern"),
    ]
    
    for cmd, desc in bluos_patterns:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"{desc}: {cmd} -> {resp}")
    
    sock.close()
    print("\nTest complete!")

if __name__ == "__main__":
    test()