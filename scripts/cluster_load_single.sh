#!/bin/bash
LC_ALL=C
export LC_ALL
freemem=`free -m | grep buffers/cache | awk '{ print \$4 }'`
load5=`uptime | awk '{print $10}' | sed -e 's/,//g'`

echo "Load: ${load5} - Mem: ${freemem}MB free"
