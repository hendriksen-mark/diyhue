#sh githubinstall.sh xxx.xxx.x.x allreadytoinstall master
#   $0               #1          $2                $3

curl -s $1/save
cd /
if [ $2 = allreadytoinstall ]; then
    echo "diyhue + ui update"
    curl -sL -o diyhue.zip https://github.com/diyhue/diyhue/archive/$3.zip
    #curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/master.zip
    unzip -qo diyhue.zip
    rm diyhue.zip
    cp -r diyHue-$3/BridgeEmulator/flaskUI /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/functions /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/lights /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/sensors /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/HueObjects /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/services /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/configManager /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/logManager /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/HueEmulator3.py /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/githubInstall.sh /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/genCert.sh /opt/hue-emulator/
    cp -r diyHue-$3/BridgeEmulator/openssl.conf /opt/hue-emulator/
    chmod +x /opt/hue-emulator/genCert.sh
    rm -r diyHue-$3
else
    echo "ui update"
fi

mkdir diyhueUI
curl -sL https://github.com/diyhue/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
#curl -sL https://github.com/hendriksen-mark/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
unzip -qo diyHueUI.zip -d diyhueUI
rm diyHueUI.zip
cp -r diyhueUI/index.html /opt/hue-emulator/flaskUI/templates/
cp -r diyhueUI/static /opt/hue-emulator/flaskUI/
rm -r diyhueUI

curl -s $1/restart
