#!/bin/bash

echo 'Hard Drives:' > info.txt
lsblk | grep sd >> info.txt
echo 'RAM:' >> info.txt
free >> info.txt
