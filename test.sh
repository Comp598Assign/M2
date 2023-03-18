#! /bin/bash
end=$((SECONDS+30))

echo 'start'
while [ $SECONDS -lt $end ]; do
   echo $SECONDS
   sleep 1
done
echo 'end'
echo '##################################'