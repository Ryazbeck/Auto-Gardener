# for testing
sudo ndsctl stop
sudo ifdown ap0
sudo systemctl disable hostapd.service dnsmasq.service
sudo systemctl stop hostapd.service dnsmasq.service
sudo rm /etc/udev/rules.d/70-persistent-net.rules
sudo udevadm trigger
sudo systemctl restart networking.service
