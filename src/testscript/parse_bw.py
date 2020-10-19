#!/usr/bin/env python3
import os
import re
import sys
import datetime
import json
import math

# Parse output and upload to Google Cloud Datastore 
# ./parse_bw.py <TAG> <DURATION> <UPLOAD_DB?>
# E.g. ./parse_bw.py tag 5 0

kind = 'aepsweep'
kind_align = 'aepalign'
kind_flush = 'aepflush'

if len(sys.argv) >= 3:
    timer_stop = int(sys.argv[2])
else:
    timer_stop = 5

if len(sys.argv) == 4:
    updatedb = 1
    with open('config.json') as f:
        config = json.load(f)
else:
    updatedb = 0

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print('{0} [output.txt] <duration> <upload_db>'.format(sys.argv[0]))
    exit(0)

# Predefined data format (see config.example.json)
'''
{
  "media": "lpmem",
  "interleaving": "1",
  "local": "1",
  "avgpower": "15000",
  "peakpower": "20000",
  "emon": "1",
  "aepwatch": "1",
  "fence": "1",
  "baddata": "0",
  "rerun": "0"
}
'''

operation_dict = ['Load', 'NTStore', 'Store', 'Store+Flush']
task_dict = [None, None, None, 'StrideBW',
             'RandBW', None, None, None, 'AlignBW', 'ClwbFence']
version = os.popen('git rev-parse HEAD').read()

def _decode(o):
    if isinstance(o, str) or isinstance(o, unicode):
        try:
            return int(o)
        except ValueError:
            return o
    elif isinstance(o, dict):
        return {k: _decode(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_decode(v) for v in o]
    else:
        return o


timer = 0
with open(sys.argv[1], 'r') as f:
    task = ""
    throughput = []
    for line in f:
        line = re.sub('\[.*\] ', '', line)
        parts = line.split(' ')
        if parts[0] == 'LATTester_START:':
            assert timer == 0
            task = parts[1].strip('\n').strip('\r')
            throughput = []
        elif parts[0] == 'LATTester_END:':
            assert timer == timer_stop
            timer = 0
            taskparts = task.split('-')
            machine = taskparts[0]
            tasktype = taskparts[1]
            avg = sum(throughput) / float(len(throughput))
            if tasktype == '3':
                # - StrideBW: AEP1-3-TAG-64-256-1-300-2
                tag = taskparts[2]
                size = taskparts[3]
                stride = taskparts[4]
                parallel = taskparts[5]
                delay = taskparts[6]
                op = taskparts[7]
                a = [tag, op, parallel, size, stride, delay, avg]
                print(*a, sep=',')
            elif tasktype == '4':
                # - RandBW: AEP1-4-TAG-64-1-2
                stride = 0
                delay = 0
                tag = taskparts[2]
                align_size = int(math.pow(2, int(taskparts[3])))
# AEP1-4-unalign-7-128-2-0
                size = taskparts[4]
                parallel = taskparts[5]
                op = taskparts[6]
                a = [tag, op, parallel, size, align_size, avg]
                print(*a, sep=',')
            elif tasktype == '8':
                # Align: AEP1-8-9-6-2-2-TAG
                size = int(math.pow(2, int(taskparts[2])))
                parallel = taskparts[3]
                op = taskparts[4]
                alloc_type = taskparts[5]
                tag = taskparts[6]
                a = [tag, op, parallel, size, alloc_type, avg]
                print(*a, sep=',')
            elif tasktype == '9':
                # AEP2-9-flushfence-65536-64-8192-3-0
                tag = taskparts[2]
                size = taskparts[3]
                flush = taskparts[4]
                fence = taskparts[5]
                parallel = taskparts[6]
                op = taskparts[7]
                a = [task, parallel, size, flush, fence, avg]
                print(*a, sep=',')

        else:
            lineparts = parts[0].strip('\n').strip('\r').split('\t')
            if not re.match("\d+$", lineparts[0]) or int(lineparts[0]) != timer + 1:
                # sys.stderr.write('ignore line:' + line)
                continue
            second = lineparts[0]
            value = lineparts[1]
            throughput.append(int(value))
            timer += 1

