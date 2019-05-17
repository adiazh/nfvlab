echo "Starting OSM VM"
VBoxManage startvm "OSM Ubuntu 16:4 192.168.100.24" --type headless

sleep 5

echo "Starting devstack VM"
VBoxManage startvm "Ubuntu16:4 Devstack 192.168.100.23" --type headless
