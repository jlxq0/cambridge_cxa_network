#!/usr/bin/env python3
"""
Test script for Cambridge CXA connection via USR-W610
Tests both basic TCP connection and CXA protocol commands
WITH VOLUME CONTROL TESTING
"""

import socket
import time
import sys

# USR-W610 Configuration
HOST = "10.0.0.24"
PORT = 8899
TIMEOUT = 5

# Cambridge CXA Commands - CORRECTED PROTOCOL
CMD_GET_STATUS = "#01,01,\r"      # Get power status
CMD_POWER_ON = "#01,11\r"         # Power on
CMD_POWER_OFF = "#01,12\r"        # Power off

# Volume Commands
CMD_GET_VOLUME = "#03,01,\r"      # Get current volume (0-96)
CMD_SET_VOLUME = "#03,02,"        # Set volume (add XX\r where XX is 00-96)
CMD_VOLUME_UP = "#01,01\r"        # Volume up one step
CMD_VOLUME_DOWN = "#01,02\r"      # Volume down one step

# Source Commands
CMD_GET_SOURCE = "#03,03,\r"      # Get current source
CMD_SET_SOURCE = "#03,04,"        # Set source (add XX\r)

# Mute Commands
CMD_GET_MUTE = "#03,05,\r"        # Get mute status
CMD_MUTE_ON = "#01,03\r"          # Mute on
CMD_MUTE_OFF = "#01,04\r"         # Mute off

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
        # Clear any pending data first
        sock.settimeout(0.1)
        try:
            while sock.recv(1024):
                pass
        except:
            pass

        # Send command
        sock.send(command.encode('utf-8'))

        # Wait for response
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

def test_volume_control(sock):
    """Test volume control functions"""
    print("\n" + "="*50)
    print("VOLUME CONTROL TEST")
    print("="*50)

    # Step 1: Read current volume
    print("\n1. Reading current volume...")
    response = send_command(sock, CMD_GET_VOLUME, "Get volume")
    current_volume = None

    if response and "#05,01," in response:
        try:
            # Parse volume from response format: #05,01,XX
            parts = response.split(",")
            if len(parts) >= 3:
                vol_str = parts[2].strip()
                current_volume = int(vol_str)
                print(f"  → Current volume: {current_volume}/96 ({int(current_volume/96*100)}%)")
        except:
            print(f"  → Could not parse volume from: {response}")

    if current_volume is None:
        print("  → Unable to read current volume, trying to set to 40...")
        send_command(sock, "#03,02,40\r", "Set volume to 40")
        time.sleep(0.5)
        response = send_command(sock, CMD_GET_VOLUME, "Get volume")
        if response and "#05,01," in response:
            try:
                parts = response.split(",")
                if len(parts) >= 3:
                    current_volume = int(parts[2].strip())
                    print(f"  → Volume now at: {current_volume}/96")
            except:
                current_volume = 40  # Assume it worked

    # Step 2: Decrease volume by steps
    if current_volume is not None:
        print("\n2. Decreasing volume by 5 steps...")
        for i in range(5):
            response = send_command(sock, CMD_VOLUME_DOWN, f"Volume down (step {i+1})")
            time.sleep(0.2)

        # Step 3: Read new volume
        print("\n3. Reading volume after decrease...")
        response = send_command(sock, CMD_GET_VOLUME, "Get volume")
        if response and "#05,01," in response:
            try:
                parts = response.split(",")
                if len(parts) >= 3:
                    new_volume = int(parts[2].strip())
                    print(f"  → New volume: {new_volume}/96 ({int(new_volume/96*100)}%)")
                    print(f"  → Volume changed by: {new_volume - current_volume} steps")
            except:
                print(f"  → Could not parse volume from: {response}")

    # Step 4: Test absolute volume setting
    print("\n4. Testing absolute volume setting...")
    test_volumes = [30, 45, 35]  # Safe test volumes

    for vol in test_volumes:
        command = f"#03,02,{vol:02d}\r"
        response = send_command(sock, command, f"Set volume to {vol}")
        time.sleep(0.5)

        # Verify it worked
        response = send_command(sock, CMD_GET_VOLUME, "Verify volume")
        if response and "#05,01," in response:
            try:
                parts = response.split(",")
                if len(parts) >= 3:
                    actual_vol = int(parts[2].strip())
                    if actual_vol == vol:
                        print(f"  ✓ Volume successfully set to {vol}")
                    else:
                        print(f"  ⚠ Volume is {actual_vol}, expected {vol}")
            except:
                pass

    # Step 5: Test volume up
    print("\n5. Testing volume up...")
    for i in range(3):
        response = send_command(sock, CMD_VOLUME_UP, f"Volume up (step {i+1})")
        time.sleep(0.2)

    response = send_command(sock, CMD_GET_VOLUME, "Get final volume")
    if response and "#05,01," in response:
        try:
            parts = response.split(",")
            if len(parts) >= 3:
                final_volume = int(parts[2].strip())
                print(f"  → Final volume: {final_volume}/96 ({int(final_volume/96*100)}%)")
        except:
            pass

def test_cxa_communication(sock):
    """Test CXA protocol commands"""
    print("\n2. Testing Cambridge CXA basic communication...")

    # Test power status
    response = send_command(sock, CMD_GET_STATUS, "Get power status")
    if response:
        if "#04,01,01" in response:
            print("  → Amplifier is ON")
        elif "#04,01,00" in response:
            print("  → Amplifier is in STANDBY")
        else:
            print(f"  → Power status response: {response}")

    # Test current source
    response = send_command(sock, CMD_GET_SOURCE, "Get current source")
    if response and "#05,03," in response:
        sources = {
            "00": "XLR/A1 Balanced",
            "01": "A1",
            "02": "A2",
            "03": "A3",
            "04": "A4",
            "05": "D1",
            "06": "D2",
            "07": "D3",
            "14": "Bluetooth",
            "16": "USB"
        }

        try:
            parts = response.split(",")
            if len(parts) >= 3:
                source_code = parts[2].strip()
                source_name = sources.get(source_code, f"Unknown ({source_code})")
                print(f"  → Current source: {source_name}")
        except:
            print(f"  → Source response: {response}")

    # Test mute status
    response = send_command(sock, CMD_GET_MUTE, "Get mute status")
    if response and "#05,05," in response:
        if ",01" in response:
            print("  → Mute is ON")
        elif ",00" in response:
            print("  → Mute is OFF")
        else:
            print(f"  → Mute response: {response}")

def interactive_test(sock):
    """Interactive command testing"""
    print("\n3. Interactive mode - send custom commands")
    print("   Enter commands without \\r (it will be added automatically)")
    print("   Type 'help' for command list, 'quit' to exit")

    commands = {
        "power on": "#01,11",
        "power off": "#01,12",
        "mute on": "#01,03",
        "mute off": "#01,04",
        "vol up": "#01,01",
        "vol down": "#01,02",
        "vol 30": "#03,02,30",
        "vol 40": "#03,02,40",
        "vol 50": "#03,02,50",
        "source a1": "#03,04,01",
        "source a2": "#03,04,02",
        "source a3": "#03,04,03",
        "source a4": "#03,04,04",
        "source d1": "#03,04,05",
        "source d2": "#03,04,06",
        "source d3": "#03,04,07",
        "source bt": "#03,04,14",
        "source usb": "#03,04,16",
        "source xlr": "#03,04,00",
        "get power": "#01,01,",
        "get volume": "#03,01,",
        "get source": "#03,03,",
        "get mute": "#03,05,"
    }

    while True:
        try:
            cmd = input("\nEnter command: ").strip().lower()

            if cmd == 'quit':
                break
            elif cmd == 'help':
                print("\nAvailable commands:")
                print("\nPower:")
                print("  power on/off       - Control power")
                print("  get power          - Get power status")
                print("\nVolume:")
                print("  vol up/down        - Step volume")
                print("  vol 30/40/50       - Set volume (0-96)")
                print("  get volume         - Get current volume")
                print("\nMute:")
                print("  mute on/off        - Control mute")
                print("  get mute           - Get mute status")
                print("\nSources:")
                print("  source a1/a2/a3/a4 - Select analog input")
                print("  source d1/d2/d3    - Select digital input")
                print("  source bt/usb/xlr  - Select BT/USB/XLR")
                print("  get source         - Get current source")
            elif cmd in commands:
                send_command(sock, commands[cmd] + "\r", cmd)
            elif cmd.startswith('#'):
                # Allow raw command entry
                send_command(sock, cmd + "\r", "custom command")
            elif cmd.startswith('vol '):
                # Allow custom volume setting
                try:
                    vol = int(cmd.split()[1])
                    if 0 <= vol <= 96:
                        send_command(sock, f"#03,02,{vol:02d}\r", f"Set volume to {vol}")
                    else:
                        print("Volume must be between 0 and 96")
                except:
                    print("Invalid volume format. Use: vol 40")
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

        # Test volume control
        response = input("\nDo you want to test volume control? (y/n): ")
        if response.lower() == 'y':
            test_volume_control(sock)

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
