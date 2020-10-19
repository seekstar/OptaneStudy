echo size threads throughput\(MiB/s\) > summary.txt
awk -F , '{print $4, $3, $7}' repeatr1.summary.txt >> summary.txt
