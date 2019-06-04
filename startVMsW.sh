echo "Starting OSM VM"
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "OSM.24" --type headless

sleep 5

echo "Starting devstack VM"
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "Devstack.23" --type headless
