"""Constants for Cambridge CXA Network integration."""

DOMAIN = "cambridge_cxa_network"
DEFAULT_NAME = "Cambridge Audio CXA"

# Network defaults - USR-W610 typically uses port 8899
DEFAULT_PORT = 8899
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_TIMEOUT = 2.0

# Configuration keys
CONF_CONNECTION_TYPE = "connection_type"
CONF_TCP_HOST = "tcp_host"
CONF_TCP_PORT = "tcp_port"
CONF_SERIAL_PORT = "serial_port"
CONF_AMP_TYPE = "amp_type"
CONF_CXN_IP = "cxn_ip"

CONNECTION_TCP = "tcp"
CONNECTION_SERIAL = "serial"

AMP_TYPES = ["CXA61", "CXA81"]

# Cambridge CXA Commands - TESTED AND WORKING
# Power Commands
AMP_CMD_GET_PWSTATE = "#01,01"      # Get power status -> #02,01,1 (on) or #02,01,0 (off)
AMP_CMD_SET_PWR_ON = "#01,11"       # Power on  
AMP_CMD_SET_PWR_STANDBY = "#01,12"  # Power off

# Volume Commands
AMP_CMD_SET_VOLUME = "#11,02,"      # Set volume (00-96) -> #12,02
# Note: No volume query or increment/decrement commands found in protocol

# Mute Commands  
AMP_CMD_SET_MUTE_ON = "#1,04,1"     # Mute ON -> #02,03,1
AMP_CMD_SET_MUTE_OFF = "#1,04,0"    # Mute OFF -> #02,03,0
# Note: Mute uses single digit group (#1, not #01)

# Source Commands
AMP_CMD_GET_CURRENT_SOURCE = "#03,01"   # Get source -> #04,01,XX
AMP_CMD_SET_SOURCE = "#03,02,"          # Set source XX -> #04,01,XX

# Info Commands
AMP_CMD_GET_MODEL = "#11,06"           # Get model -> #12,06,CXA81
AMP_CMD_GET_FIRMWARE_VERSION = "#13,01" # Get firmware -> #14,01,1.1

# Reply codes - TESTED RESPONSES
AMP_REPLY_PWR_STANDBY = "#02,01,0"     # Power is off/standby
AMP_REPLY_PWR_ON = "#02,01,1"          # Power is on
AMP_REPLY_MUTE_OFF = "#02,03,0"        # Mute is off  
AMP_REPLY_MUTE_ON = "#02,03,1"         # Mute is on
AMP_REPLY_SOURCE = "#04,01,"            # Source response (followed by source code)
AMP_REPLY_VOLUME_SET = "#12,02"        # Volume set confirmation
AMP_REPLY_MODEL = "#12,06,"            # Model response (followed by model name)
AMP_REPLY_FIRMWARE_VERSION = "#14,01,"  # Firmware (followed by version)

# Error codes
ERROR_CMD_GROUP_UNKNOWN = "#00,01"
ERROR_CMD_NUMBER_UNKNOWN = "#00,02"
ERROR_CMD_DATA_ERROR = "#00,03"
ERROR_CMD_NOT_AVAILABLE = "#00,04"

# Input sources for CXA61 - Using #03,02,XX pattern
NORMAL_INPUTS_CXA61 = {
    "A1": "#03,02,01",
    "A2": "#03,02,02",
    "A3": "#03,02,03",
    "A4": "#03,02,04",
    "D1": "#03,02,05",
    "D2": "#03,02,06",
    "D3": "#03,02,07",
    "Bluetooth": "#03,02,14",
    "USB": "#03,02,16",
    "MP3": "#03,02,10"
}

# Input sources for CXA81
NORMAL_INPUTS_CXA81 = {
    "XLR/A1 Balanced": "#03,04,00",
    "A1": "#03,04,01",
    "A2": "#03,04,02",
    "A3": "#03,04,03",
    "A4": "#03,04,04",
    "D1": "#03,04,05",
    "D2": "#03,04,06",
    "D3": "#03,04,07",
    "Bluetooth": "#03,04,14",
    "USB": "#03,04,16"
}

# Response mappings for CXA61 - TESTED
NORMAL_INPUTS_AMP_REPLY_CXA61 = {
    "#04,01,01": "A1",
    "#04,01,02": "A2", 
    "#04,01,03": "A3",
    "#04,01,04": "A4",
    "#04,01,05": "D1",
    "#04,01,06": "D2",
    "#04,01,07": "D3",
    "#04,01,14": "Bluetooth",
    "#04,01,16": "USB",
    "#04,01,10": "MP3"
}

# Response mappings for CXA81 - TESTED
NORMAL_INPUTS_AMP_REPLY_CXA81 = {
    "#04,01,00": "XLR/A1 Balanced",
    "#04,01,01": "A1",
    "#04,01,02": "A2",
    "#04,01,03": "A3",
    "#04,01,04": "A4",
    "#04,01,05": "D1",
    "#04,01,06": "D2",
    "#04,01,07": "D3",
    "#04,01,14": "Bluetooth",
    "#04,01,16": "USB"
}

# Sound modes (speaker selection)
SOUND_MODES = {
    "A": "#1,25,0",
    "AB": "#1,25,1",
    "B": "#1,25,2"
}