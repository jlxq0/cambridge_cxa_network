#!/usr/bin/env python3
"""
Test the discovered volume command pattern
"""

import socket
import time

HOST = "10.0.0.24"
PORT = 8899

def test():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((HOST, PORT))
    print("Testing volume command #11,02,XX\n")
    
    def send(cmd):
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
        try:
            sock.settimeout(1)
            resp = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return resp
        except:
            return None
    
    print("1. Testing volume set commands with #11,02,XX pattern...")
    print("-" * 50)
    
    volumes = [10, 20, 30, 40, 50, 40, 30, 20]
    
    for vol in volumes:
        cmd = f"#11,02,{vol:02d}"
        resp = send(cmd)
        print(f"Set volume {vol:2d}: {cmd} -> {resp}")
        print("  >> Listen for volume change!")
        time.sleep(1.5)
    
    print("\n2. Testing volume query commands...")
    print("-" * 50)
    
    # Try to find volume query
    queries = [
        "#11,01",
        "#11,02", 
        "#11,03",
        "#11,00",
        "#12,01",
        "#12,02",
        "#10,01",
        "#10,02",
    ]
    
    for cmd in queries:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"Query {cmd} -> {resp}")
    
    print("\n3. Testing volume increment/decrement...")
    print("-" * 50)
    
    # Try increment/decrement patterns
    inc_dec = [
        ("#11,03", "Vol up?"),
        ("#11,04", "Vol down?"),
        ("#11,05", "Vol up alt?"),
        ("#11,06", "Vol down alt?"),
        ("#11,10", "Increment?"),
        ("#11,11", "Decrement?"),
        ("#10,01", "Alt up?"),
        ("#10,02", "Alt down?"),
        ("#12,03", "Pattern 3?"),
        ("#12,04", "Pattern 4?"),
    ]
    
    print("Current volume should be 20 from previous test")
    
    for cmd, desc in inc_dec:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"{desc}: {cmd} -> {resp}")
            time.sleep(0.5)
    
    print("\n4. Setting specific test volumes...")
    print("-" * 50)
    
    # Set to known values
    test_sequence = [
        (25, "Set to 25"),
        (35, "Set to 35"), 
        (30, "Set to 30"),
    ]
    
    for vol, desc in test_sequence:
        cmd = f"#11,02,{vol:02d}"
        resp = send(cmd)
        print(f"{desc}: {cmd} -> {resp}")
        time.sleep(1)
    
    print("\n5. Test mute with known commands...")
    print("-" * 50)
    
    print("Mute on: #1,04,1 ->", send("#1,04,1"))
    time.sleep(2)
    print("Mute off: #1,04,0 ->", send("#1,04,0"))
    
    sock.close()
    print("\nIf you heard volume changes with #11,02,XX commands, we found it!")

if __name__ == "__main__":
    test()