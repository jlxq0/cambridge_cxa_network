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

# Cambridge CXA Commands - CORRECTED PROTOCOL
# Power Commands
AMP_CMD_GET_PWSTATE = "#01,01,"     # Get power status
AMP_CMD_SET_PWR_ON = "#01,11"       # Power on  
AMP_CMD_SET_PWR_STANDBY = "#01,12"  # Power off

# Volume Commands
AMP_CMD_INCREASE_VOLUME = "#01,01"  # Volume UP by 1 step
AMP_CMD_DECREASE_VOLUME = "#01,02"  # Volume DOWN by 1 step
AMP_CMD_GET_VOLUME = "#03,01,"      # Get current volume level
AMP_CMD_SET_VOLUME = "#03,02,"      # Set volume to specific level (00-96)

# Mute Commands
AMP_CMD_SET_MUTE_ON = "#01,03"      # Mute ON
AMP_CMD_SET_MUTE_OFF = "#01,04"     # Mute OFF
AMP_CMD_GET_MUTE_STATE = "#03,05,"  # Query mute status

# Source Commands  
AMP_CMD_GET_CURRENT_SOURCE = "#03,03,"  # Get current source
AMP_CMD_SELECT_NEXT_SOURCE = "#03,02"   # Next source (might not be implemented)
AMP_CMD_SELECT_PREV_SOURCE = "#03,03"   # Prev source (might not be implemented)
AMP_CMD_SET_SOURCE = "#03,04,"          # Set source (add XX)

# Group 13 - Version Commands
AMP_CMD_GET_PROTOCOL_VERSION = "#13,01"
AMP_CMD_GET_FIRMWARE_VERSION = "#13,02"

# Reply codes - CORRECTED PROTOCOL
AMP_REPLY_PWR_STANDBY = "#04,01,00"  # Power is in standby
AMP_REPLY_PWR_ON = "#04,01,01"       # Power is on
AMP_REPLY_MUTE_OFF = "#05,05,00"     # Mute is off
AMP_REPLY_MUTE_ON = "#05,05,01"      # Mute is on
AMP_REPLY_SOURCE = "#05,03,"          # Followed by source code (00-16)
AMP_REPLY_VOLUME = "#05,01,"          # Followed by volume level (00-96)
AMP_REPLY_PROTOCOL_VERSION = "#14,01,"
AMP_REPLY_FIRMWARE_VERSION = "#14,02,"

# Error codes
ERROR_CMD_GROUP_UNKNOWN = "#00,01"
ERROR_CMD_NUMBER_UNKNOWN = "#00,02"
ERROR_CMD_DATA_ERROR = "#00,03"
ERROR_CMD_NOT_AVAILABLE = "#00,04"

# Input sources for CXA61
NORMAL_INPUTS_CXA61 = {
    "A1": "#03,04,01",
    "A2": "#03,04,02",
    "A3": "#03,04,03",
    "A4": "#03,04,04",
    "D1": "#03,04,05",
    "D2": "#03,04,06",
    "D3": "#03,04,07",
    "Bluetooth": "#03,04,14",
    "USB": "#03,04,16",
    "MP3": "#03,04,10"
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

# Response mappings for CXA61 - CORRECTED PROTOCOL
NORMAL_INPUTS_AMP_REPLY_CXA61 = {
    "#05,03,01": "A1",
    "#05,03,02": "A2", 
    "#05,03,03": "A3",
    "#05,03,04": "A4",
    "#05,03,05": "D1",
    "#05,03,06": "D2",
    "#05,03,07": "D3",
    "#05,03,14": "Bluetooth",
    "#05,03,16": "USB",
    "#05,03,10": "MP3"
}

# Response mappings for CXA81 - CORRECTED PROTOCOL
NORMAL_INPUTS_AMP_REPLY_CXA81 = {
    "#05,03,00": "XLR/A1 Balanced",
    "#05,03,01": "A1",
    "#05,03,02": "A2",
    "#05,03,03": "A3",
    "#05,03,04": "A4",
    "#05,03,05": "D1",
    "#05,03,06": "D2",
    "#05,03,07": "D3",
    "#05,03,14": "Bluetooth",
    "#05,03,16": "USB"
}

# Sound modes (speaker selection)
SOUND_MODES = {
    "A": "#1,25,0",
    "AB": "#1,25,1",
    "B": "#1,25,2"
}