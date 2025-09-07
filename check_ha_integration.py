#!/usr/bin/env python3
"""
Check if the Cambridge CXA integration can be imported correctly
Run this in your Home Assistant config directory
"""

import sys
import os

# Add config directory to path
sys.path.insert(0, '/config')

print("Checking Cambridge CXA integration...")
print("=" * 50)

# Check if custom component exists
if os.path.exists('/config/custom_components/cambridge_cxa'):
    print("✓ Custom component directory exists")
else:
    print("✗ Custom component directory NOT FOUND at /config/custom_components/cambridge_cxa")
    sys.exit(1)

# Check manifest.json
manifest_path = '/config/custom_components/cambridge_cxa/manifest.json'
if os.path.exists(manifest_path):
    print("✓ manifest.json exists")
    import json
    with open(manifest_path) as f:
        manifest = json.load(f)
    print(f"  - Domain: {manifest.get('domain')}")
    print(f"  - Name: {manifest.get('name')}")
    print(f"  - Version: {manifest.get('version')}")
    print(f"  - Config flow: {manifest.get('config_flow', 'NOT SET!')}")
    
    if not manifest.get('config_flow'):
        print("\n✗ ERROR: config_flow is not set to true in manifest.json!")
        print("  This is why it's not showing in the GUI!")
else:
    print("✗ manifest.json NOT FOUND")

print("\nChecking Python imports...")

# Try importing the integration
try:
    from custom_components.cambridge_cxa import __init__
    print("✓ __init__.py imports successfully")
except Exception as e:
    print(f"✗ Error importing __init__.py: {e}")

try:
    from custom_components.cambridge_cxa import config_flow
    print("✓ config_flow.py imports successfully")
    
    # Check if config flow class exists
    if hasattr(config_flow, 'CambridgeCXAConfigFlow'):
        print("✓ CambridgeCXAConfigFlow class found")
    else:
        print("✗ CambridgeCXAConfigFlow class NOT FOUND")
        
except Exception as e:
    print(f"✗ Error importing config_flow.py: {e}")

try:
    from custom_components.cambridge_cxa import const
    print("✓ const.py imports successfully")
except Exception as e:
    print(f"✗ Error importing const.py: {e}")

try:
    from custom_components.cambridge_cxa import media_player
    print("✓ media_player.py imports successfully")
except Exception as e:
    print(f"✗ Error importing media_player.py: {e}")

# Check strings.json
strings_path = '/config/custom_components/cambridge_cxa/strings.json'
if os.path.exists(strings_path):
    print("\n✓ strings.json exists")
else:
    print("\n✗ strings.json NOT FOUND - this might prevent GUI config")

# Check translations
trans_dir = '/config/custom_components/cambridge_cxa/translations'
if os.path.exists(trans_dir):
    print("✓ translations directory exists")
    en_json = os.path.join(trans_dir, 'en.json')
    if os.path.exists(en_json):
        print("✓ translations/en.json exists")
    else:
        print("✗ translations/en.json NOT FOUND")
else:
    print("✗ translations directory NOT FOUND")

print("\n" + "=" * 50)
print("SUMMARY:")
print("If all checks pass but integration doesn't show in GUI:")
print("1. Restart Home Assistant again")
print("2. Clear browser cache")
print("3. Try in incognito/private browsing mode")
print("4. Check /config/home-assistant.log for errors")