#!/usr/bin/env python3
"""
Find volume control commands for Cambridge CXA
"""

import socket
import time
import sys

HOST = "10.0.0.24"
PORT = 8899

def test():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((HOST, PORT))
    print("Connected to Cambridge CXA")
    
    def send(cmd):
        if not cmd.endswith('\r'):
            cmd += '\r'
        sock.send(cmd.encode())
        time.sleep(0.2)
        try:
            sock.settimeout(0.5)
            resp = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return resp
        except:
            return None
    
    print("\n1. Current status:")
    print(f"Power: {send('#01,01')}")
    print(f"Source: {send('#03,01')}")
    
    print("\n2. Testing volume patterns from other Cambridge products...")
    
    # Test Edge/CXN style commands
    patterns = [
        ("Edge style get volume", "#04,01"),
        ("Edge style set volume 30", "#04,02,30"),
        ("Edge style vol up", "#04,03"),
        ("Edge style vol down", "#04,04"),
        
        ("Alt pattern 1 get", "#05,01"), 
        ("Alt pattern 1 set 30", "#05,02,30"),
        
        ("Alt pattern 2 get", "#06,01"),
        ("Alt pattern 2 set 30", "#06,02,30"),
        
        ("Simple volume query", "#02"),
        ("Simple volume 30", "#02,30"),
        
        ("Direct volume 30", "#30"),
        ("Direct volume 40", "#40"),
    ]
    
    for desc, cmd in patterns:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"✓ {desc}: {cmd} -> {resp}")
        else:
            print(f"✗ {desc}: {cmd} -> {resp or 'timeout'}")
    
    print("\n3. Testing CXN documented commands...")
    
    # From CXN documentation
    cxn_patterns = [
        ("CXN get volume", "#1,01"),
        ("CXN set volume 30", "#1,05,30"),
        ("CXN vol up", "#1,02"), 
        ("CXN vol down", "#1,03"),
        ("CXN mute on", "#1,04,1"),
        ("CXN mute off", "#1,04,0"),
    ]
    
    for desc, cmd in cxn_patterns:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"✓ {desc}: {cmd} -> {resp}")
    
    print("\n4. Your test showed #01,01 returns #02,01,1 (power status)")
    print("   Let's test similar patterns...")
    
    # Test patterns similar to power query
    for group in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        for cmd in [1, 2, 3, 4, 5]:
            command = f"#{group:02d},{cmd:02d}"
            resp = send(command)
            
            if resp and not resp.startswith("#00"):
                # Check if response might be volume
                if resp and "," in resp:
                    parts = resp.split(",")
                    if len(parts) >= 3:
                        try:
                            value = int(parts[2])
                            if 0 <= value <= 96:
                                print(f"POSSIBLE VOLUME: {command} -> {resp} (value={value})")
                        except:
                            pass
    
    sock.close()

if __name__ == "__main__":
    test()