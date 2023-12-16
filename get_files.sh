#! /bin/bash
#

# Define the shell functions
#
usage(){
        echo "Usage: $0 [-h]" >&2
        exit 0
}

die()
{
        echo $1 >&2
        exit 1

}

# Configure the kill actions to take
trap "echo $0: killed @ $(date) ; exit 99" SIGHUP SIGINT SIGTERM

#
# cd to /srv/chain directory
#
export BC="tendermint"
#echo $BC
export H=srv/$BC
echo $H
cd $H || { echo "Error----> Cannot change to $H directory." >&2; exit 2; }

touch xx || { echo "Error----> Cannot write to $H directory." >&2; exit 2; }
rm xx || { echo "Error----> Cannot remove file xx in $H directory." >&2; exit 2; }

export NB=$(cat checkpoint.txt)
#export NB=4191200
#export NB=$(ls -l 4* | awk  '{print $9;}' | tail -1)
echo $NB
export NB="$(echo  $NB | awk '{print $1-1;}')"
#echo $NB
#exit 0

for i in 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 \
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 \
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 \
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 
do 
	export NB=$(echo $NB | awk '{print $1+1;}')
	#echo $NB
	curl --connect-timeout 6 --request GET --url http://116.202.143.93:1317/cosmos/base/tendermint/v1beta1/blocks/$NB  >$NB 2>/dev/null
	grep '"code": 3' $NB >/dev/null 2>/dev/null
	if [  "$?" -eq 0 ]
	then
		exit 0
	fi
	echo $NB > checkpoint.txt
	echo $NB
	#sleep 1
done

exit 0

export BN=4143887
echo "curl --request GET --url http://116.202.143.93:1317/cosmos/base/tendermint/v1beta1/blocks/$BN"

exit 0
