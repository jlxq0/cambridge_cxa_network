#!/bin/bash
# Script to check if cambridge_cxa_network is loaded in Home Assistant

echo "Checking for cambridge_cxa_network in Home Assistant logs..."
echo "================================================"

# Check for the warning that shows it loaded
echo -e "\n1. Checking if custom component was found:"
grep -i "cambridge_cxa_network" /config/home-assistant.log | grep "We found a custom integration"

# Check for any errors
echo -e "\n2. Checking for any errors:"
grep -i "cambridge_cxa_network" /config/home-assistant.log | grep -i error

# Check for successful setup
echo -e "\n3. Checking for setup messages:"
grep -i "cambridge_cxa_network" /config/home-assistant.log | grep -E "(Setting up|Setup of|Loaded)"

# Check if manifest was loaded
echo -e "\n4. Checking component registry:"
grep -i "cambridge_cxa_network" /config/.storage/core.config_entries 2>/dev/null

# List the files to confirm they're in the right place
echo -e "\n5. Checking file structure:"
ls -la /config/custom_components/cambridge_cxa_network/

echo -e "\n6. Checking if config_flow is set in manifest:"
grep -i "config_flow" /config/custom_components/cambridge_cxa_network/manifest.json