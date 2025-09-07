#!/usr/bin/env python3
"""
Complete volume command discovery
"""

import socket
import time

HOST = "10.0.0.24"
PORT = 8899

def test():
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
    
    print("COMPLETE CAMBRIDGE CXA PROTOCOL TEST")
    print("="*50)
    
    # Set volume to known value
    print("\n1. Setting volume to 30 for baseline...")
    print(f"Set vol 30: #11,02,30 -> {send('#11,02,30')}")
    time.sleep(1)
    
    print("\n2. Finding volume QUERY command...")
    print("-"*50)
    
    # Try all possible query patterns
    for group in range(10, 15):
        for cmd in range(1, 10):
            command = f"#{group},{cmd:02d}"
            resp = send(command)
            
            if resp and not resp.startswith("#00"):
                # Check if response contains a number that could be volume
                if "," in resp:
                    parts = resp.split(",")
                    if len(parts) >= 3:
                        try:
                            val = int(parts[2])
                            if 20 <= val <= 40:  # Likely volume range
                                print(f"POSSIBLE VOL QUERY: {command} -> {resp} (value={val})")
                        except:
                            pass
                else:
                    print(f"Other: {command} -> {resp}")
    
    print("\n3. Finding volume UP/DOWN commands...")
    print("-"*50)
    
    # Set to 30 first
    send("#11,02,30")
    time.sleep(1)
    
    # Try single-byte vol up/down patterns
    single_patterns = [
        "#01", "#02", "#03", "#04", "#05",
        "#10", "#11", "#12", "#13", "#14",
        "#20", "#21", "#22", "#23", "#24",
    ]
    
    for cmd in single_patterns:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"Single: {cmd} -> {resp}")
            time.sleep(0.3)
    
    # Try two-byte patterns
    print("\nTrying two-byte increment patterns...")
    
    for group in [10, 11, 12, 13]:
        for cmd in [1, 3, 4, 5, 7, 8, 9, 10]:
            command = f"#{group},{cmd:02d}"
            resp = send(command)
            
            if resp and not resp.startswith("#00"):
                print(f"Pattern: {command} -> {resp}")
                time.sleep(0.5)
                # Check if volume changed by querying
                send("#11,02,31")  # Try setting to 31
                time.sleep(0.3)
                send("#11,02,30")  # Back to 30
                time.sleep(0.3)
    
    print("\n4. Testing BluOS style increment...")
    print("-"*50)
    
    # Try "+1" and "-1" style
    special = [
        ("#11,02,+1", "Increment by 1"),
        ("#11,02,-1", "Decrement by 1"),
        ("#11,+", "Simple plus"),
        ("#11,-", "Simple minus"),
        ("#11,UP", "Up command"),
        ("#11,DN", "Down command"),
    ]
    
    for cmd, desc in special:
        resp = send(cmd)
        if resp and not resp.startswith("#00"):
            print(f"{desc}: {cmd} -> {resp}")
    
    print("\n5. Summary of working commands...")
    print("-"*50)
    
    print("CONFIRMED WORKING:")
    print("  Power query:    #01,01 or #1,01")
    print("  Power on:       #01,11 or #1,11")  
    print("  Power off:      #01,12 or #1,12")
    print("  Source query:   #03,01")
    print("  Source set:     #03,02,XX")
    print("  Volume set:     #11,02,XX (00-96)")
    print("  Mute on:        #1,04,1")
    print("  Mute off:       #1,04,0")
    print("  Model query:    #11,06")
    
    print("\nNEED TO FIND:")
    print("  Volume query:   ???")
    print("  Volume up:      ???") 
    print("  Volume down:    ???")
    
    sock.close()

if __name__ == "__main__":
    test()