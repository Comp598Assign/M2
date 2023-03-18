#! /bin/bash
end=$((SECONDS+100))

echo 'start heavy'
while [ $SECONDS -lt $end ]; do
   echo $SECONDS
   sleep 1
done
echo 'end heavy'
echo '##################################\n'