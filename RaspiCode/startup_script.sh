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
    if ping -c 1 172.24.1.1 > /dev/null; then
	break
    fi
done
echo "Network up"

while true; do
    if python3 /home/pi/RaspiCode/start_rover.py 5560; then
	break
    fi
done
