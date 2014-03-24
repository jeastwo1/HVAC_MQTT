#!/bin/bash
ifconfig can0 up
echo "i 0x031C e" >/dev/pcanusb0
ifconfig can1 up

