#!/bin/bash

index=10
end=$((index))
echo $end

if  [ ${index} -eq ${end} ]; then
	echo "success"
fi

#while :
#do
#	nc -v -z -w 5 mail.tmax.co.kr 587
#	sleep 10
#done
