#!/bin/bash


USERNAME=sandip
DEST=$1

if [[ $DEST == "local"  ]]; then
	echo "copying into /home/sandip/shared"
	rsync -av -e --exclude='.git/*' --exclude='copy.sh' --exclude='run.sh' --exclude='input/' --exclude='log/' /home/sandip/MEGA/python/contractgenerator/* /home/sandip/shared/cogent
elif [[ $DEST == "remote"  ]]; then
	echo "copying into labmachine:/home/sandip/python"
	rsync -av -e ssh --exclude='.git/*' --exclude='copy.sh' /home/sandip/MEGA/python/contractgenerator ${USERNAME}@labmachine:/home/sandip/python
else
	echo "give input: local or remote"
fi


#DEST="local, labmachine"
#for HOSTNAME in ${HOSTS} ; do
#	if [[ $HOSTNAME == "local"  ]]; then
#		#rsync -av -e --exclude='.git/*' /home/sandip/MEGA/python/contractgenerator /home/sandip/shared
#		echo "local"
#	elif [[ $HOSTNAME == "labmachine"  ]]; then
#		#rsync -av -e ssh --exclude='.git/*' /home/sandip/MEGA/python/contractgenerator ${USERNAME}@labmachine:/home/sandip/python
#		echo "remote"
#	else
#		echo "bad input"
#	fi
#done
