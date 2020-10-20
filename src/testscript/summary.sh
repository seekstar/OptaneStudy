if [ ! $1 ]; then
	srcfile=repeatr1.summary.txt
else
	srcfile=$1
fi
if [ ! $2 ]; then
	dstfile=summary.txt
else
	dstfile=$2
fi
echo size threads throughput\(MiB/s\) > $dstfile
awk -F , '{print $4, $3, $7}' $srcfile >> $dstfile

