# Home Assistant Custom Component for controlling Cambridge Audio CXA 61/81 amplifiers

This component allows you to control your Cambridge Audio CXA amplifier through Home Assistant. It now supports both direct serial connections and network connections via WiFi-to-serial converters like the USR-W610.

## Features

- Power on/off control
- Input source selection
- Mute control
- Speaker output selection (A, AB, B)
- Volume control (when used with Cambridge CXN)
- **NEW**: Network connection support via USR-W610 WiFi-to-serial converter
- **NEW**: GUI-based configuration (no more YAML editing!)

## Installation

### HACS Installation (Recommended)

1. Add custom repository `lievencoghe/cambridge_cxa` to HACS
2. Install the "Cambridge Audio CXA Network" integration
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Cambridge CXA" and follow the configuration wizard

### Manual Installation

1. Copy the `cambridge_cxa` folder to your `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Cambridge CXA" and follow the configuration wizard

## Configuration

This integration now uses the Home Assistant UI for configuration. When you add the integration, you'll be guided through a setup wizard that will:

1. Ask whether you're using a network or serial connection
2. Configure the connection details
3. Test the connection
4. Select your amplifier model (CXA61 or CXA81)
5. Optionally configure CXN IP for volume control

### Network Connection Setup (USR-W610)

To use this integration with a USR-W610 WiFi-to-serial converter:

#### USR-W610 Configuration

1. Connect to your USR-W610's web interface
2. Configure the following settings:
   - **Work Mode**: TCP Server
   - **TCP Server Port**: 8899 (default)
   - **Serial Port Settings**:
     - Baud Rate: 9600
     - Data Bits: 8
     - Stop Bits: 1
     - Parity: None
   - **WiFi Settings**: Connect to your network

#### Wiring

Connect your USR-W610 to your Cambridge CXA amplifier:
- USR-W610 TX → CXA RS232 RX (pin 2)
- USR-W610 RX → CXA RS232 TX (pin 3)
- USR-W610 GND → CXA RS232 GND (pin 5)

Use a **straight-through** RS232 cable (not a null modem cable).

### Direct Serial Connection Setup

If you have a direct serial connection between your Home Assistant instance and your Cambridge CXA:

1. Connect your USB-to-serial adapter or serial cable
2. The integration will automatically detect available serial ports
3. Select the correct port from the dropdown during setup

## Remote Serial Connection (Legacy Method)

If you need to use ser2net/socat for a remote serial connection, you can still follow the original setup instructions below. However, we recommend using the USR-W610 for a simpler network setup.

### ser2net Configuration

For ser2net version 3.x, add to `/etc/ser2net.conf`:
```
5000:raw:600:/dev/serial/by-id/<insert id of USB to serial device here>:9600 8DATABITS NONE 1STOPBIT
```

For ser2net version 4.x, add to `/etc/ser2net.yaml`:
```yaml
connection: &cambridge
    accepter: tcp,5000
    enable: on
    options:
      kickolduser: true
      telnet-brk-on-sync: true
    connector: serialdev,
              /dev/serial/by-id/<insert id of USB to serial device here>,
              9600n81,local
```

### socat Configuration

Create `/etc/default/socat.conf`:
```
OPTIONS="pty,link=/dev/ttyCXA,raw,ignoreeof,echo=0 tcp:<IP address of the Raspberry Pi>:5000"
```

Then set up the systemd service as described in the original documentation.

## Usage

Once configured, your Cambridge CXA will appear as a media player entity in Home Assistant. You can:

- Turn it on/off
- Select input sources
- Mute/unmute
- Select speaker outputs (A, AB, or B)
- Control volume (if CXN IP is configured)

## Troubleshooting

### Connection Issues

- **Network**: Ensure your USR-W610 is on the same network and the IP/port are correct
- **Serial**: Check that the serial port permissions are correct and no other process is using it

### No Response

- Verify your RS232 cable is straight-through (not null modem)
- Check TX/RX connections are not reversed
- Ensure the amplifier is powered on

### Enable Debug Logging

Add to your `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.cambridge_cxa: debug
```

## Version History

- **v2.0.0**: Added network support via USR-W610, GUI configuration, async implementation
- **v0.5**: Original serial-only implementation

## Credits

- Original implementation by [@lievencoghe](https://github.com/lievencoghe)
- Network support added by the community

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/lievencoghe/cambridge_cxa/issues).