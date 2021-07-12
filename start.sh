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
  echo "Awesome! We are almost ready to go!"
  echo "...one more thing before we take off, your street number, sir?"
  echo "...you know, people might try to contact you while you are away!"
  read -p "(Dr.Rosen's port) " ROSEN_PORT
  echo "All set! Buckle up, sir!"
  echo "python3 Rosen.py --host $EINSTEIN_IP --port $EINSTEIN_PORT --listen $ROSEN_PORT"
  python3 Rosen.py --host $EINSTEIN_IP --port $EINSTEIN_PORT --listen $ROSEN_PORT
else
  echo "Welcome, Dr.Einstein! I know you are busy, so let's get this done quickly!"
  DIR=$(pwd)
  ESCAPED_DIR=${DIR//\//\\/}
  sed -i -e "s/<DIR>/${ESCAPED_DIR}/" wormhole.service
  cp ./wormhole.service /etc/systemd/system
  systemctl start wormhole
  systemctl status wormhole
  echo "All set! Have a good one, sir!"
fi