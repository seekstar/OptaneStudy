set -e

if [ ! $3 ]; then
	echo Usage: $0 testapp start_number end_number
	exit
fi

if [ $(whoami) != "root" ]; then
	echo Please run as root.
	exit
fi

nohup bash helper/run.sh $* &

