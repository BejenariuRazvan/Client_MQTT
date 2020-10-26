#!/bin/bash

# to be modified in the future when the publishers are implemented
# - eg: different output file for every topic of interest (Hard Drives, RAM, etc)

echo 'Hard Drives:' > info.txt
lsblk | grep sd >> info.txt
echo -e '\nRAM:' >> info.txt
free >> info.txt
echo -e '\nsensors (temperatures):' >> info.txt
sensors >> info.txt
echo -e '\nprocesses' >> info.txt
top -b -n 1 >> info.txt