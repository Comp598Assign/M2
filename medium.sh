#! /bin/bash
end=$((SECONDS+10))

echo 'start medium'
while [ $SECONDS -lt $end ]; do
   echo $SECONDS
   sleep 1
done
echo 'end'
echo '##################################'