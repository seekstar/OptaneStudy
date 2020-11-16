#!/bin/bash

# Sample run script

set -e

# Disable CPU Prefetching
sudo wrmsr -a 0x1a4 0xf

export GOOGLE_APPLICATION_CREDENTIALS=dbuser.json
export AEPWatch=1
export EMon=0

export PATH=$PATH:`pwd`/subtests/bin
testapp=./subtests/41_rand_ntstore.sh
repdev=`mount | grep ReportFS | awk {'print \$1'}`
testdev=`mount | grep LatencyFS | awk {'print \$1'}`
runtime=20

if [ -z $repdev ] || [ -z $testdev ]; then
	echo "Please run mount.sh first"
	exit 1
fi

for i in `seq $runtime`; do
  export TAG=repeatr$i
  echo =====Workload description====
  echo Run: $testapp
  echo Tag: $TAG
  echo LatFS on: $testdev
  echo RepFS on: $repdev
  echo Config:
  cat config.json
  echo Press any key to continue...
  read

  $testapp $repdev $testdev
  mv output.txt ./$TAG.output.txt
  mv summary.txt ./$TAG.summary.txt

done

sudo wrmsr -a 0x1a4 0x0

aeprelease
