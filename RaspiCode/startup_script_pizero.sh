#!/bin/bash
# sudo cp rover_pizero.service /etc/systemd/system/rover_pizero.service
# sudo systemctl enable rover_pizero.service
# reboot

# To see output:
# sudo journalctl -u rover_pizero.service

cd /home/pi/Mars-Rover/RaspiCode && python3 start_rover.py --as-unit pizero settings_depcam.xml
