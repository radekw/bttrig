#!/bin/bash

DEVICE=$(echo $1 |tr '[:lower:]' '[:upper:]')
HCITOOLCMD="sudo /usr/local/bin/hcitool"

for s in $($HCITOOLCMD con); do
    if [ "$s" == "$DEVICE" ]; then
        echo "$DEVICE connected already"
        exit 0
    fi
done

if [ -z "$($HCITOOLCMD cc $DEVICE 2>&1)" ]; then
    echo "$DEVICE connected"
    $HCITOOLCMD rssi $DEVICE
    $HCITOOLCMD dc $DEVICE
    exit 0
fi

echo "$DEVICE not available"
exit 1

