#!/bin/sh
cd `dirname $0`/../src

OLD=`cat ./addon.xml | grep '<addon' | grep 'version="' | grep -E -o 'version="[0-9\.]+"' |  grep -E -o '[0-9\.]+'`
echo "Old version: $OLD"
echo -n 'New version: '
read NEW

sed -e "s/version=\"$OLD\"/version=\"$NEW\"/g" ./addon.xml > ./addon2.xml
mv ./addon2.xml ./addon.xml


sed -e "s/script.module.delugestream\" version=\"[^\"]*\"/script\.module\.delugestream\" version=\"$NEW\"/g" ../../plugin.rutracker/src/addon.xml > ../../plugin.rutracker/src/addon2.xml
mv ../../plugin.rutracker/src/addon2.xml ../../plugin.rutracker/src/addon.xml


rm -rf ../script.module.delugestream
rm -f ./script.module.delugestream.zip
mkdir ../script.module.delugestream
cp -r ./* ../script.module.delugestream/

cd ../
zip -rq ./script.module.delugestream.zip ./script.module.delugestream

cp ./script.module.delugestream.zip ../repository.hal9000/repo/script.module.delugestream/script.module.delugestream-$NEW.zip

rm -rf ./script.module.delugestream
rm -f ./script.module.delugestream.zip

#`../repository.hal9000/build/build.sh`
