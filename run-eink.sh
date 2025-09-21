#!/bin/bash
LOG_FILE="/home/pi/kiezbox-ha/eink.log"
export VIRTUAL_ENV=/home/pi/kiezbox-ha/.venv/
export PATH=/home/pi/kiezbox-ha/.venv/bin:/usr/bin:/bin
echo 'Using python: ' $(which python)
sudo python /home/pi/kiezbox-ha/start_script.py #  >> "$LOG_FILE" 2>&1
# sudo /bin/bash -c "python /home/pi/kiezbox-ha/start_script.py >> '$LOG_FILE' 2>&1"


# sudo /bin/sh -i -c "python /home/pi/kiezbox-ha/start_script.py" >> "$LOG_FILE" 2>&1
# sudo python /home/pi/kiezbox-ha/start_script.py >> "$LOG_FILE" 2>&1
