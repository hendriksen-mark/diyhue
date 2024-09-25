#!/bin/bash

echo -e "\033[32m Updating repository.\033[0m"
opkg update
wait

echo -e "\033[32m Installing dependencies.\033[0m"
opkg install ca-bundle git git-http nano nmap python3 python3-pip python3-setuptools openssl-util curl unzip coap-client kmod-bluetooth bluez-daemon ca-certificates libustream-wolfssl libcurl coreutils-stat tar zoneinfo-all
wait

echo -e "\033[32m Creating directories.\033[0m"
mkdir -p /opt/tmp
mkdir -p /opt/hue-emulator

echo -e "\033[32m Updating python3-pip.\033[0m"
python3 -m pip install --upgrade pip
wait

### Choose Branch for Install
echo -e "\033[36mPlease choose a Branch to install\033[0m"
echo -e "\033[33mSelect Branch by entering the corresponding Number: [Default: $branchSelection]\033[0m  "
echo -e "[1] Master Branch - most stable Release "
echo -e "[2] Developer Branch - test latest features and fixes - Work in Progress!"
echo -e "\033[36mNote: Please report any Bugs or Errors with Logs to our GitHub, Discourse or Slack. Thank you!\033[0m"
echo -n "I go with Nr.: "

branchSelection=""
read userSelection
case $userSelection in
        1)
        branchSelection="master"
        echo -e "master selected"
        ;;
        2)
        branchSelection="dev"
        echo -e "Dev selected"
        ;;
				*)
        branchSelection="master"
        echo -e "master selected"
        ;;
esac

if [ -d "/opt/hue-emulator" ]; then

  systemctl stop hueemulatorWrt-service
  echo -e "\033[33m Existing installation found, performing upgrade.\033[0m"

  cp -r /opt/hue-emulator/config /tmp/diyhue_backup
  rm -rf /opt/hue-emulator/*
  cp -r /tmp/diyhue_backup /opt/hue-emulator/config

fi

cd /opt/tmp
curl -sL -o diyhue.zip https://github.com/diyhue/diyhue/archive/$branchSelection.zip
#curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/$branchSelection.zip
wait
unzip -qo diyhue.zip
wait
cp -r diyHue-$branchSelection/BridgeEmulator/flaskUI /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/functions /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/lights /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/sensors /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/HueObjects /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/services /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/configManager /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/logManager /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/HueEmulator3.py /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/githubInstall.sh /opt/hue-emulator/
cp -r diyHue-$branchSelection/BridgeEmulator/openssl.conf /opt/hue-emulator/
rm -Rf /opt/hue-emulator/BridgeEmulator/functions/network.py
mv diyHue-$branchSelection/BridgeEmulator/functions/network_OpenWrt.py /opt/hue-emulator/functions/network.py
sed 's/master/'$branchSelection'/g' diyHue-$branchSelection/BridgeEmulator/hueemulatorWrt-service
cp -r diyHue-$branchSelection/BridgeEmulator/hueemulatorWrt-service /etc/init.d/
python3 -m pip install -r diyHue-$branchSelection/requirements.txt
wait

echo -e "\033[32m Copy web interface files.\033[0m"
mkdir diyhueUI
curl -sL https://www.github.com/diyhue/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
wait
unzip -qo diyHueUI.zip -d diyhueUI
wait
mv diyhueUI/index.html /opt/hue-emulator/flaskUI/templates/
cp -r diyhueUI/static /opt/hue-emulator/flaskUI/

echo -e "\033[32m Creating certificate.\033[0m"
cd /opt/hue-emulator
mkdir -p /opt/hue-emulator/config
mac=`cat /sys/class/net/br-lan/address`
serial="${mac:0:2}${mac:3:2}${mac:6:2}fffe${mac:9:2}${mac:12:2}${mac:15:2}"
dec_serial=`python3 -c "print(int(\"$serial\", 16))"`
openssl req -new -days 3650 -config openssl.conf -nodes -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -pkeyopt ec_param_enc:named_curve -subj "/C=NL/O=Philips Hue/CN=$serial" -keyout private.key -out public.crt -set_serial $dec_serial
wait
touch /opt/hue-emulator/config/cert.pem
cat private.key > /opt/hue-emulator/config/cert.pem
cat public.crt >> /opt/hue-emulator/config/cert.pem
rm private.key public.crt

echo -e "\033[32m Changing permissions.\033[0m"
chmod +x /opt/hue-emulator/HueEmulator3.py
chmod +x /opt/hue-emulator/HueObjects
chmod +x /opt/hue-emulator/configManager
chmod +x /opt/hue-emulator/flaskUI
chmod +x /opt/hue-emulator/functions
chmod +x /opt/hue-emulator/lights
chmod +x /opt/hue-emulator/logManager
chmod +x /opt/hue-emulator/sensors
chmod +x /opt/hue-emulator/services
chmod +x /opt/hue-emulator/functions/network.py
chmod +x /opt/hue-emulator/config
chmod +x /etc/init.d/hueemulatorWrt-service

echo -e "\033[32m Enable startup service.\033[0m"
/etc/init.d/hueemulatorWrt-service enable
wait

echo -e "\033[32m Cleaning...\033[0m"
cd /opt/hue-emulator
rm -Rf /opt/tmp
wait

echo -e "\033[32m Installation completed. run: nano /etc/config/uhttpd and mod htpp port 80 for 82. For save changes ctrl +x, y, and enter..\033[0m"
sleep 15s
nano /etc/config/uhttpd

echo -e "\033[32m Installation completed.\033[0m"
wait
reboot 10
exit 0
