#!/bin/bash
echo "Hello, Dr..."
read -p "(type 'rosen' or 'einstein') " NAME
if [ $NAME = 'rosen' ]
then
  echo "Welcome, Dr.Rosen! Visiting Dr.Einstein again? Which planet is it this time?"
  read -p "(Dr.Einstein's IP) " EINSTEIN_IP
  echo "...the address is 443 Einstein Dr., Princeton? Please correct me if I'm wrong!"
  read -p "(Dr.Einstein's port) [press RETURN to skip] " EINSTEIN_PORT
  EINSTEIN_PORT=${EINSTEIN_PORT:-443}
  echo "Now, can I have your street number, sir?"
  echo "...you know, in case people try to contact you while you are away!"
  read -p "(Dr.Rosen's port) " ROSEN_PORT
  echo "Awesome! We are almost ready to go!"
  echo "Before we take off, would you like me to open the window blinds for you?"
  echo "...the view inside the wormhole is quite something!"
  read -p "(yes/no) " OPEN_THE_WINDOW 
  echo "All set! Buckle up, sir!"
  if [ $OPEN_THE_WINDOW = "yes" ]
  then
    echo "python3 Rosen.py --host $EINSTEIN_IP --port $EINSTEIN_PORT --listen $ROSEN_PORT --verbose"
    python3 Rosen.py --host $EINSTEIN_IP --port $EINSTEIN_PORT --listen $ROSEN_PORT --verbose
  else
    echo "python3 Rosen.py --host $EINSTEIN_IP --port $EINSTEIN_PORT --listen $ROSEN_PORT"
    python3 Rosen.py --host $EINSTEIN_IP --port $EINSTEIN_PORT --listen $ROSEN_PORT
  fi
else
  echo "Welcome, Dr.Einstein! I know you are busy, so let's get this done quickly!"
  echo "Let's find a place to live ...could be anywhere. How about 443 Einstein Dr., sir?"
  read -p "(Dr.Einstein's port) " EINSTEIN_PORT
  DIR=$(pwd)
  ESCAPED_DIR=${DIR//\//\\/}
  echo "Printing your boarding pass..."
  sed -e "s/<DIR>/${ESCAPED_DIR}/; s/<PORT>/${EINSTEIN_PORT}/" BoardingPass > wormhole.service

  echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  cat wormhole.service
  echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

  cp ./wormhole.service /etc/systemd/system
  systemctl daemon-reload
  systemctl start wormhole
  systemctl status wormhole
  echo "All set! Have a good one, sir!"
fi