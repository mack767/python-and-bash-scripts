#!/bin/bash

TARGET="127.0.0.1"
START_PORT=20
END_PORT=1024
RATE_LIMIT=0.1

echo "Scanning $TARGET"
echo "Reverse DNS:"
host $TARGET

for ((port=$START_PORT; port<=$END_PORT; port++))
do
    # TCP Scan
    timeout 1 bash -c "echo > /dev/tcp/$TARGET/$port" 2>/dev/null &&
        echo "[+] TCP Port $port OPEN"

    # UDP Scan
    timeout 1 nc -u -z $TARGET $port 2>/dev/null &&
        echo "[+] UDP Port $port OPEN|RESPONSIVE"

    # Banner grabbing (TCP only)
    banner=$(echo -e "HEAD / HTTP/1.0\r\n\r\n" | timeout 1 nc $TARGET $port 2>/dev/null)
    if [[ ! -z "$banner" ]]; then
        echo "[+] Banner on port $port:"
        echo "$banner"
    fi

    # SSL Detection
    echo | timeout 1 openssl s_client -connect $TARGET:$port 2>/dev/null | grep -q "BEGIN CERTIFICATE" &&
        echo "[+] SSL/TLS detected on port $port"

    sleep $RATE_LIMIT
done

echo "Scan complete."