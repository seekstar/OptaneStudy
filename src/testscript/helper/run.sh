#!/bin/bash

set -e

if [ ! $3 ]; then
	echo Usage: $0 testapp start_number end_number
	exit
fi

# Disable CPU Prefetching
# Dangerous
sudo wrmsr -a 0x1a4 0xf

export GOOGLE_APPLICATION_CREDENTIALS=dbuser.json
export AEPWatch=1
export EMon=0

export PATH=$PATH:`pwd`/subtests/bin
repdev=`mount | grep ReportFS | awk {'print \$1'}`
testdev=`mount | grep LatencyFS | awk {'print \$1'}`

if [ -z $repdev ] || [ -z $testdev ]; then
	echo "Please run mount.sh first"
	exit 1
fi

for i in `seq $2 $3`; do
  export TAG=repeatr$i
  echo =====Workload description====
  echo Run: $1
  echo Tag: $TAG
  echo LatFS on: $testdev
  echo RepFS on: $repdev
  echo Config:
  cat config.json

  $1 $repdev $testdev
  mv output.txt ./$TAG.output.txt
  mv summary.txt ./$TAG.summary.txt
  if [ -f stop ]; then
	  rm stop
	  break
  fi
done

# Dangerous
sudo wrmsr -a 0x1a4 0x0

aeprelease
