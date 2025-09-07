#!/usr/bin/env python3
"""
Test script for Cambridge CXA connection via USR-W610
Tests both basic TCP connection and CXA protocol commands
"""

import socket
import time
import sys

# USR-W610 Configuration
HOST = "10.0.0.24"
PORT = 8899
TIMEOUT = 5

# Cambridge CXA Commands
CMD_GET_POWER = "#01,01\r"
CMD_GET_SOURCE = "#03,01\r"
CMD_GET_MUTE = "#01,03\r"
CMD_POWER_ON = "#01,02,1\r"
CMD_POWER_OFF = "#01,02,0\r"

def test_tcp_connection():
    """Test basic TCP connectivity to USR-W610"""
    print(f"\n1. Testing TCP connection to {HOST}:{PORT}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((HOST, PORT))
        print(f"✓ Successfully connected to USR-W610 at {HOST}:{PORT}")
        return sock
    except socket.timeout:
        print(f"✗ Connection timed out - check if USR-W610 is reachable at {HOST}:{PORT}")
        return None
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def send_command(sock, command, description):
    """Send a command and read response"""
    print(f"\n  Sending: {description} ({command.strip()})")
    
    try:
        # Send command
        sock.send(command.encode('utf-8'))
        
        # Wait for response
        time.sleep(0.5)
        
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
        
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"  Response: {decoded}")
            return decoded
        else:
            print("  No response received")
            return None
            
    except Exception as e:
        print(f"  Error: {e}")
        return None

def test_cxa_communication(sock):
    """Test CXA protocol commands"""
    print("\n2. Testing Cambridge CXA communication...")
    
    # Test power status
    response = send_command(sock, CMD_GET_POWER, "Get power status")
    if response:
        if "#02,01,1" in response:
            print("  → Amplifier is ON")
        elif "#02,01,0" in response:
            print("  → Amplifier is in STANDBY")
        else:
            print(f"  → Unknown power status: {response}")
    
    # Test current source
    response = send_command(sock, CMD_GET_SOURCE, "Get current source")
    if response:
        sources = {
            "#04,01,00": "A1",
            "#04,01,01": "A2",
            "#04,01,02": "A3",
            "#04,01,03": "A4",
            "#04,01,04": "D1",
            "#04,01,05": "D2",
            "#04,01,06": "D3",
            "#04,01,14": "Bluetooth",
            "#04,01,16": "USB",
            "#04,01,10": "MP3",
            "#04,01,20": "XLR"
        }
        
        source_found = False
        for code, name in sources.items():
            if code in response:
                print(f"  → Current source: {name}")
                source_found = True
                break
        
        if not source_found:
            print(f"  → Unknown source: {response}")
    
    # Test mute status
    response = send_command(sock, CMD_GET_MUTE, "Get mute status")
    if response:
        if "#02,03,1" in response:
            print("  → Mute is ON")
        elif "#02,03,0" in response:
            print("  → Mute is OFF")
        else:
            print(f"  → Unknown mute status: {response}")

def interactive_test(sock):
    """Interactive command testing"""
    print("\n3. Interactive mode - send custom commands")
    print("   Enter commands without \\r (it will be added automatically)")
    print("   Type 'help' for command list, 'quit' to exit")
    
    commands = {
        "power on": "#01,02,1",
        "power off": "#01,02,0",
        "mute on": "#01,04,1",
        "mute off": "#01,04,0",
        "source a1": "#03,04,00",
        "source a2": "#03,04,01",
        "source a3": "#03,04,02",
        "source a4": "#03,04,03",
        "source d1": "#03,04,04",
        "source d2": "#03,04,05",
        "source d3": "#03,04,06",
        "source bluetooth": "#03,04,14",
        "source usb": "#03,04,16",
        "get power": "#01,01",
        "get source": "#03,01",
        "get mute": "#01,03"
    }
    
    while True:
        try:
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'help':
                print("\nAvailable commands:")
                for key in sorted(commands.keys()):
                    print(f"  {key:<20} → {commands[key]}")
            elif cmd in commands:
                send_command(sock, commands[cmd] + "\r", cmd)
            elif cmd.startswith('#'):
                # Allow raw command entry
                send_command(sock, cmd + "\r", "custom command")
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            break

def main():
    """Main test sequence"""
    print("Cambridge CXA Network Connection Tester")
    print("=" * 40)
    
    # Test connection
    sock = test_tcp_connection()
    if not sock:
        print("\nCannot proceed without connection")
        sys.exit(1)
    
    try:
        # Test CXA communication
        test_cxa_communication(sock)
        
        # Ask about interactive mode
        response = input("\nDo you want to enter interactive mode? (y/n): ")
        if response.lower() == 'y':
            interactive_test(sock)
            
    except Exception as e:
        print(f"\nError during testing: {e}")
    
    finally:
        # Clean up
        sock.close()
        print("\n✓ Connection closed")

if __name__ == "__main__":
    main()