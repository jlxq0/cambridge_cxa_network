#!/usr/bin/env python3
"""
Automated protocol discovery for Cambridge CXA
Tests common command patterns to find volume controls
"""

import socket
import time

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
    time.sleep(0.2)
    
    # Read response
    sock.settimeout(1)
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

def main():
    print("CAMBRIDGE CXA AUTOMATED PROTOCOL DISCOVERY")
    print("="*50)
    
    sock = connect()
    print(f"Connected to {HOST}:{PORT}")
    
    # First, test all query commands (no parameters)
    print("\n1. Testing all query commands (format: #XX,YY)...")
    print("-"*50)
    
    working_queries = []
    
    for group in range(1, 10):
        for cmd in range(1, 20):
            command = f"#{group:02d},{cmd:02d}\r"
            response = send_command(sock, command)
            
            if response and not response.startswith("#00"):
                print(f"QUERY: {command.strip()} -> {response}")
                working_queries.append((command.strip(), response))
    
    print(f"\nFound {len(working_queries)} working queries")
    
    # Test volume-specific patterns
    print("\n2. Testing potential volume commands...")
    print("-"*50)
    
    # Common volume command patterns in AV equipment
    volume_patterns = [
        # Format: (group, command_base)
        (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
        (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
        (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
    ]
    
    print("\nTesting volume set commands (will try values 20, 30, 40)...")
    
    for group, cmd in volume_patterns:
        # Test setting volume to different levels
        test_volumes = [20, 30, 40]
        responses = []
        
        for vol in test_volumes:
            command = f"#{group:02d},{cmd:02d},{vol:02d}\r"
            response = send_command(sock, command)
            
            if response and not response.startswith("#00"):
                responses.append((vol, response))
        
        if len(responses) >= 2:
            print(f"\nPOSSIBLE VOLUME COMMAND: #{group:02d},{cmd:02d},XX")
            for vol, resp in responses:
                print(f"  Volume {vol}: {resp}")
    
    # Test increment/decrement patterns
    print("\n3. Testing increment/decrement commands...")
    print("-"*50)
    
    inc_dec_patterns = [
        # Single byte increments
        ("#01\r", "Increment pattern 1"),
        ("#02\r", "Decrement pattern 1"),
        ("#11\r", "Increment pattern 2"),
        ("#12\r", "Decrement pattern 2"),
        ("#21\r", "Increment pattern 3"),
        ("#22\r", "Decrement pattern 3"),
        # Two byte patterns
        ("#01,10\r", "Volume up variant"),
        ("#01,11\r", "Volume up variant 2"),
        ("#01,20\r", "Volume down variant"),
        ("#01,21\r", "Volume down variant 2"),
        ("#02,01\r", "Alt volume up"),
        ("#02,02\r", "Alt volume down"),
    ]
    
    for cmd, desc in inc_dec_patterns:
        response = send_command(sock, cmd)
        if response and not response.startswith("#00"):
            print(f"{desc}: {cmd.strip()} -> {response}")
    
    # Test mute patterns
    print("\n4. Testing mute query commands...")
    print("-"*50)
    
    mute_patterns = [
        "#01,03\r", "#01,04\r", "#01,05\r",
        "#02,03\r", "#02,04\r", "#02,05\r", 
        "#03,03\r", "#03,04\r", "#03,05\r",
        "#04,03\r", "#04,04\r", "#04,05\r",
        "#05,03\r", "#05,04\r", "#05,05\r",
    ]
    
    for cmd in mute_patterns:
        response = send_command(sock, cmd)
        if response and not response.startswith("#00") and "," in response:
            print(f"MUTE QUERY: {cmd.strip()} -> {response}")
    
    # Summary
    print("\n5. Summary of findings...")
    print("-"*50)
    
    print("\nWorking query commands:")
    for cmd, resp in working_queries[:10]:  # Show first 10
        print(f"  {cmd} -> {resp}")
    
    print("\nNOTE: Check the output above for POSSIBLE VOLUME COMMAND entries")
    print("These are commands where different parameter values gave different responses")
    
    sock.close()
    print("\nDiscovery complete!")

if __name__ == "__main__":
    main()