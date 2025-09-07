#!/usr/bin/env python3
"""
Fix script to ensure cambridge_cxa_network appears in Home Assistant UI
"""

import json
import os

print("Checking cambridge_cxa_network integration...")

# Check manifest
manifest_path = "custom_components/cambridge_cxa_network/manifest.json"
if os.path.exists(manifest_path):
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    print("\nCurrent manifest.json:")
    print(json.dumps(manifest, indent=2))
    
    # Ensure all required fields
    required = {
        "domain": "cambridge_cxa_network",
        "name": "Cambridge Audio CXA Network",
        "config_flow": True,
        "version": "2.0.0",
        "integration_type": "device",  # Changed from "entity"
        "iot_class": "local_polling"
    }
    
    updated = False
    for key, value in required.items():
        if manifest.get(key) != value:
            print(f"\nUpdating {key}: {manifest.get(key)} -> {value}")
            manifest[key] = value
            updated = True
    
    if updated:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print("\nmanifest.json updated!")
    else:
        print("\nmanifest.json looks correct")

# Check config_flow.py exists and has VERSION
if os.path.exists("custom_components/cambridge_cxa_network/config_flow.py"):
    print("\n✓ config_flow.py exists")
    with open("custom_components/cambridge_cxa_network/config_flow.py") as f:
        content = f.read()
        if "VERSION = 1" in content and "CambridgeCXAConfigFlow" in content:
            print("✓ Config flow class found with VERSION")
        else:
            print("✗ Config flow might be missing VERSION or class")
else:
    print("\n✗ config_flow.py NOT FOUND!")

print("\nTo fix in Home Assistant:")
print("1. Copy updated files to /config/custom_components/cambridge_cxa_network/")
print("2. Restart Home Assistant")
print("3. Clear browser cache")
print("4. Try adding integration again")