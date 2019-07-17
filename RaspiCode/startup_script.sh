#!/bin/bash
# To run on startup:
# sudo cp rover.service /etc/systemd/system/rover.service
# sudo systemctl enable rover.service
# reboot

# To see output:
# sudo journalctl -u rover.service

# everytime the files change copy to the systemd folder as described above
# then reboot or restart the service
while true; do
    if ping -c 1 192.168.4.1 > /dev/null; then
	break
    fi
done
echo "Network up"

# while true; do
    # cd /home/pi/Mars-Rover/RaspiCode && python3 start_rover.py 5560
# done

cd /home/pi/Mars-Rover/RaspiCode && python3 start_rover.py 5560
