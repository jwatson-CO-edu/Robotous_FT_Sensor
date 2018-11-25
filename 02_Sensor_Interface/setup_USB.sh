#!/bin/bash
# setup_USB.sh
# James Watson, 2018 November
# Give permission to the USB ports

# NOTE: This script must be run as root , Ex: sudo su

chmod u+x setup_USB.sh
clear

echo "Setting permission for ttyS0 ..."
chmod a+rw /dev/ttyS0

echo "Setting permission for ttyUSB0 ..."
chmod a+rw /dev/ttyUSB0

echo "COMPLETE!"
