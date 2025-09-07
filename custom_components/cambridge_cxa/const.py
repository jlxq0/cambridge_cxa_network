"""Constants for Cambridge CXA integration."""

DOMAIN = "cambridge_cxa"
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

# Cambridge Audio Protocol Commands (from existing implementation)
AMP_CMD_GET_PWSTATE = "#01,01"
AMP_CMD_GET_CURRENT_SOURCE = "#03,01"
AMP_CMD_GET_MUTE_STATE = "#01,03"

AMP_CMD_SET_MUTE_ON = "#01,04,1"
AMP_CMD_SET_MUTE_OFF = "#01,04,0"
AMP_CMD_SET_PWR_ON = "#01,02,1"
AMP_CMD_SET_PWR_OFF = "#01,02,0"

AMP_REPLY_PWR_ON = "#02,01,1"
AMP_REPLY_PWR_STANDBY = "#02,01,0"
AMP_REPLY_MUTE_ON = "#02,03,1"
AMP_REPLY_MUTE_OFF = "#02,03,0"

# Input sources for CXA61
NORMAL_INPUTS_CXA61 = {
    "A1": "#03,04,00",
    "A2": "#03,04,01",
    "A3": "#03,04,02",
    "A4": "#03,04,03",
    "D1": "#03,04,04",
    "D2": "#03,04,05",
    "D3": "#03,04,06",
    "Bluetooth": "#03,04,14",
    "USB": "#03,04,16",
    "MP3": "#03,04,10"
}

# Input sources for CXA81
NORMAL_INPUTS_CXA81 = {
    "A1": "#03,04,00",
    "A2": "#03,04,01",
    "A3": "#03,04,02",
    "A4": "#03,04,03",
    "D1": "#03,04,04",
    "D2": "#03,04,05",
    "D3": "#03,04,06",
    "Bluetooth": "#03,04,14",
    "USB": "#03,04,16",
    "XLR": "#03,04,20"
}

# Response mappings for CXA61
NORMAL_INPUTS_AMP_REPLY_CXA61 = {
    "#04,01,00": "A1",
    "#04,01,01": "A2",
    "#04,01,02": "A3",
    "#04,01,03": "A4",
    "#04,01,04": "D1",
    "#04,01,05": "D2",
    "#04,01,06": "D3",
    "#04,01,14": "Bluetooth",
    "#04,01,16": "USB",
    "#04,01,10": "MP3"
}

# Response mappings for CXA81
NORMAL_INPUTS_AMP_REPLY_CXA81 = {
    "#04,01,00": "A1",
    "#04,01,01": "A2",
    "#04,01,02": "A3",
    "#04,01,03": "A4",
    "#04,01,04": "D1",
    "#04,01,05": "D2",
    "#04,01,06": "D3",
    "#04,01,14": "Bluetooth",
    "#04,01,16": "USB",
    "#04,01,20": "XLR"
}

# Sound modes (speaker selection)
SOUND_MODES = {
    "A": "#1,25,0",
    "AB": "#1,25,1",
    "B": "#1,25,2"
}