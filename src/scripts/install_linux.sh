#!/bin/bash
# Install script for SpoofDPI on Linux

echo "Downloading SpoofDPI..."
curl -fsSL https://raw.githubusercontent.com/m-m-mohsen/spoof-dpi/main/install.sh | bash

echo "Checking installation..."
if command -v spoof-dpi &> /dev/null; then
    echo "SpoofDPI installed successfully!"
    echo "You can now run the Python application."
else
    echo "Installation might have failed or spoof-dpi is not in your PATH."
    echo "Please check ~/.spoof-dpi/bin"
fi
