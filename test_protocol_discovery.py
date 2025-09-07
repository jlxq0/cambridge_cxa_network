#!/usr/bin/env python3
"""
Protocol discovery script for Cambridge CXA
Systematically tests commands to understand the actual protocol
"""

import socket
import time
import sys

# USR-W610 Configuration
HOST = "10.0.0.24"
PORT = 8899
TIMEOUT = 5

def connect():
    """Connect to amplifier"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    sock.connect((HOST, PORT))
    return sock

def send_command(sock, command):
    """Send command and get response"""
    # Clear buffer
    sock.settimeout(0.1)
    try:
        while sock.recv(1024):
            pass
    except:
        pass
    
    # Send command
    sock.send(command.encode('utf-8'))
    time.sleep(0.3)
    
    # Read response
    sock.settimeout(2)
    response = b""
    
    while True:
        try:
            data = sock.recv(1)
            if not data:
                break
            response += data
            if data == b'\r' or data == b'\n':
                break
        except socket.timeout:
            break
    
    return response.decode('utf-8', errors='ignore').strip()

def test_protocol_mapping():
    """Test various command patterns to understand protocol"""
    sock = connect()
    
    print("CAMBRIDGE CXA PROTOCOL DISCOVERY")
    print("="*50)
    
    # Test all group/command combinations for queries
    print("\n1. Testing query commands (no parameters)...")
    print("-"*50)
    
    for group in range(1, 10):
        for cmd in range(1, 10):
            command = f"#{group:02d},{cmd:02d}\r"
            response = send_command(sock, command)
            
            if response and not response.startswith("#00"):
                print(f"FOUND: {command.strip()} -> {response}")
                
                # If we get a response, try with different parameters
                if "," in response:
                    parts = response.split(",")
                    if len(parts) >= 3:
                        print(f"       Response format: Group {parts[0]}, Cmd {parts[1]}, Value {parts[2]}")
    
    print("\n2. Testing control commands with parameters...")
    print("-"*50)
    
    # Test commands that might control volume
    test_params = ["00", "10", "20", "30", "40", "50"]
    
    for group in range(1, 6):
        for cmd in range(1, 20):
            for param in test_params:
                command = f"#{group:02d},{cmd:02d},{param}\r"
                response = send_command(sock, command)
                
                if response and not response.startswith("#00"):
                    print(f"CONTROL: {command.strip()} -> {response}")
                    
                    # Wait a bit to hear if anything changed
                    time.sleep(0.5)
                    
                    # Ask user if they heard a change
                    user_input = input("Did you hear/see any change? (y/n/q to quit): ")
                    if user_input.lower() == 'y':
                        print(f"*** WORKING COMMAND: {command.strip()} ***")
                    elif user_input.lower() == 'q':
                        sock.close()
                        return
    
    sock.close()

def test_specific_patterns():
    """Test specific command patterns based on observations"""
    sock = connect()
    
    print("\n3. Testing observed patterns...")
    print("-"*50)
    
    # Based on your results, #04,01,XX seems to be source codes
    # Let's find what changes volume
    
    # Test all first-level commands
    print("\nTesting single-byte commands...")
    for i in range(1, 20):
        command = f"#{i:02d}\r"
        response = send_command(sock, command)
        if response:
            print(f"{command.strip()} -> {response}")
    
    # Test volume-like parameters on different groups
    print("\nTesting volume parameters on different groups...")
    volume_values = [20, 30, 40, 30, 20]  # Test pattern
    
    for group in [1, 2, 4, 5, 6, 7, 8, 9]:
        print(f"\nTesting group {group:02d}...")
        
        for cmd in range(1, 10):
            print(f"  Testing #{group:02d},{cmd:02d},XX...")
            
            for vol in volume_values:
                command = f"#{group:02d},{cmd:02d},{vol:02d}\r"
                response = send_command(sock, command)
                
                if response and not response.startswith("#00"):
                    print(f"    {command.strip()} -> {response}")
                    time.sleep(0.3)
                    
                    # Quick check
                    if input("    Volume changed? (y/n): ").lower() == 'y':
                        print(f"    *** VOLUME COMMAND FOUND: #{group:02d},{cmd:02d},XX ***")
                        sock.close()
                        return
    
    sock.close()

def interactive_discovery():
    """Interactive command discovery"""
    sock = connect()
    
    print("\n4. Interactive Discovery Mode")
    print("-"*50)
    print("Commands to try:")
    print("  scan <group>     - Scan all commands in a group")
    print("  test <cmd>       - Test a specific command") 
    print("  vol <value>      - Test volume setting patterns")
    print("  quit             - Exit")
    
    while True:
        cmd = input("\n> ").strip()
        
        if cmd == 'quit':
            break
        elif cmd.startswith('scan '):
            group = int(cmd.split()[1])
            print(f"\nScanning group {group:02d}...")
            
            for c in range(1, 30):
                command = f"#{group:02d},{c:02d}\r"
                response = send_command(sock, command)
                
                if response and not response.startswith("#00"):
                    print(f"  {command.strip()} -> {response}")
                    
        elif cmd.startswith('test '):
            command = cmd.split(' ', 1)[1]
            if not command.endswith('\r'):
                command += '\r'
            
            response = send_command(sock, command)
            print(f"Response: {response}")
            
        elif cmd.startswith('vol '):
            value = int(cmd.split()[1])
            
            # Try different patterns for volume
            patterns = [
                f"#01,{value:02d}\r",
                f"#02,{value:02d}\r", 
                f"#04,{value:02d}\r",
                f"#05,{value:02d}\r",
                f"#01,05,{value:02d}\r",
                f"#01,06,{value:02d}\r",
                f"#05,01,{value:02d}\r",
                f"#05,02,{value:02d}\r",
            ]
            
            for pattern in patterns:
                response = send_command(sock, pattern)
                print(f"  {pattern.strip()} -> {response}")
                time.sleep(0.5)
                
                if input("  Volume changed? (y/n): ").lower() == 'y':
                    print(f"  *** VOLUME PATTERN: {pattern.strip()} ***")
                    break
    
    sock.close()

if __name__ == "__main__":
    print("Cambridge CXA Protocol Discovery Tool")
    print("="*40)
    print("1. Full protocol mapping")
    print("2. Specific pattern testing")
    print("3. Interactive discovery")
    
    choice = input("\nSelect mode (1-3): ")
    
    if choice == '1':
        test_protocol_mapping()
    elif choice == '2':
        test_specific_patterns()
    elif choice == '3':
        interactive_discovery()