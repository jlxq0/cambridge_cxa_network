#!/usr/bin/env python3
"""
Debug script for Cambridge CXA connection via USR-W610
Provides detailed debugging information about the connection
"""

import socket
import time
import sys
import select

# USR-W610 Configuration
HOST = "10.0.0.24"
PORT = 8899
TIMEOUT = 5

def test_raw_connection():
    """Test raw TCP connection and data flow"""
    print("\n=== RAW CONNECTION TEST ===")
    print(f"Connecting to {HOST}:{PORT}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((HOST, PORT))
        print("✓ TCP connection established")
        
        # Make socket non-blocking for better control
        sock.setblocking(0)
        
        return sock
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def send_and_receive(sock, command, wait_time=1.0):
    """Send command and capture all responses with detailed logging"""
    print(f"\n--- Testing command: {repr(command)} ---")
    
    # Flush any pending data first
    print("Flushing receive buffer...")
    try:
        while True:
            ready = select.select([sock], [], [], 0.1)
            if ready[0]:
                data = sock.recv(1024)
                print(f"Flushed: {repr(data)}")
            else:
                break
    except:
        pass
    
    # Send command
    try:
        print(f"Sending {len(command)} bytes: {repr(command)}")
        bytes_sent = sock.send(command)
        print(f"✓ Sent {bytes_sent} bytes")
    except Exception as e:
        print(f"✗ Send failed: {e}")
        return
    
    # Wait and collect responses
    print(f"Waiting {wait_time}s for response...")
    start_time = time.time()
    response_data = b""
    
    while (time.time() - start_time) < wait_time:
        try:
            ready = select.select([sock], [], [], 0.1)
            if ready[0]:
                chunk = sock.recv(1)  # Read one byte at a time for debugging
                if chunk:
                    response_data += chunk
                    # Print each byte as it arrives
                    print(f"  Received byte: {repr(chunk)} (hex: {chunk.hex()}, dec: {chunk[0] if chunk else 'empty'})")
        except Exception as e:
            print(f"  Read error: {e}")
            break
    
    if response_data:
        print(f"\nTotal response: {repr(response_data)}")
        print(f"Response (hex): {response_data.hex()}")
        print(f"Response (decoded): {response_data.decode('utf-8', errors='ignore')}")
    else:
        print("\n✗ No response received")

def test_different_formats(sock):
    """Test different command formats and line endings"""
    print("\n\n=== TESTING DIFFERENT COMMAND FORMATS ===")
    
    commands = [
        ("Command with CR", b"#01,01\r"),
        ("Command with LF", b"#01,01\n"),
        ("Command with CRLF", b"#01,01\r\n"),
        ("Command without terminator", b"#01,01"),
        ("Command with extra CR", b"#01,01\r\r"),
        ("Get source command", b"#03,01\r"),
        ("Get mute command", b"#01,03\r"),
    ]
    
    for description, cmd in commands:
        send_and_receive(sock, cmd, 1.0)
        time.sleep(0.5)  # Pause between commands

def test_usr_w610_echo():
    """Test if USR-W610 is in echo mode or has special settings"""
    print("\n\n=== TESTING USR-W610 SETTINGS ===")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    
    try:
        sock.connect((HOST, PORT))
        sock.setblocking(0)
        
        # Send a simple test string to see if it echoes
        test_string = b"TEST123\r"
        print(f"Sending test string: {repr(test_string)}")
        sock.send(test_string)
        
        time.sleep(0.5)
        
        # Check for echo or response
        response = b""
        try:
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                response = sock.recv(1024)
                print(f"Received: {repr(response)}")
                if test_string in response:
                    print("⚠️  USR-W610 appears to be echoing data back")
        except:
            pass
        
        if not response:
            print("✓ No echo detected")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def check_usr_w610_web():
    """Provide instructions for checking USR-W610 web interface"""
    print("\n\n=== USR-W610 WEB INTERFACE CHECK ===")
    print(f"Please verify these settings at http://{HOST}")
    print("\n1. Serial Port Settings:")
    print("   - Baud Rate: 9600")
    print("   - Data Bits: 8")
    print("   - Stop Bits: 1")
    print("   - Parity: None")
    print("   - Flow Control: None")
    print("\n2. Work Mode Settings:")
    print("   - Work Mode: TCP Server (not TCP Client)")
    print("   - TCP Server Port: 8899")
    print("   - Connection Type: TCP")
    print("\n3. Advanced Settings to check:")
    print("   - Serial packeting should be disabled")
    print("   - Timeout settings should be minimal or disabled")
    print("   - Register packet should be disabled")
    print("   - Heart beat packet should be disabled")
    
def test_manual_interaction():
    """Allow manual command entry with detailed feedback"""
    print("\n\n=== MANUAL COMMAND TEST ===")
    print("Enter commands to send (or 'quit' to exit)")
    print("Commands will be sent exactly as typed + \\r")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    
    try:
        sock.connect((HOST, PORT))
        sock.setblocking(0)
        
        while True:
            cmd = input("\nCommand: ")
            if cmd.lower() == 'quit':
                break
                
            if not cmd.startswith('#'):
                print("Warning: Cambridge commands usually start with #")
            
            send_and_receive(sock, cmd.encode() + b'\r', 2.0)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def main():
    print("Cambridge CXA / USR-W610 Debug Tool")
    print("=" * 50)
    
    # Test basic connection
    sock = test_raw_connection()
    if not sock:
        print("\n✗ Cannot establish TCP connection")
        print("\nPossible issues:")
        print("1. USR-W610 IP address is incorrect")
        print("2. USR-W610 is not powered on")
        print("3. Network/firewall issues")
        sys.exit(1)
    
    try:
        # Test different command formats
        test_different_formats(sock)
    finally:
        sock.close()
    
    # Test for echo
    test_usr_w610_echo()
    
    # Show web interface check instructions
    check_usr_w610_web()
    
    # Ask if user wants manual testing
    response = input("\n\nDo you want to test manual commands? (y/n): ")
    if response.lower() == 'y':
        test_manual_interaction()
    
    print("\n\n=== DEBUGGING TIPS ===")
    print("1. Check physical connections:")
    print("   - Is the RS232 cable properly connected?")
    print("   - TX→RX and RX→TX (crossed)?")
    print("   - Ground connected?")
    print("   - Is it a straight-through cable (not null modem)?")
    print("\n2. Check CXA amplifier:")
    print("   - Is the amplifier powered on?")
    print("   - Try power cycling the amplifier")
    print("   - Some CXA units need to be in standby (not fully off)")
    print("\n3. Test with serial terminal on USR-W610:")
    print("   - Connect a PC directly to USR-W610's serial port")
    print("   - Use a terminal program at 9600 8N1")
    print("   - Send #01,01<CR> and see if you get a response")

if __name__ == "__main__":
    main()