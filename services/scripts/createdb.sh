#!/bin/bash
SERVER_NAME=$1
echo "CREATE USER  $SERVER_NAME WITH PASSWORD '$SERVER_NAME' --createdb" | sudo -u postgres psql
sudo -u postgres createdb -T template_postgis -E utf8 -O $SERVER_NAME $SERVER_NAME

echo "GRANT ALL PRIVILEGES ON DATABASE $SERVER_NAME to $SERVER_NAME" | sudo -u postgres psql
