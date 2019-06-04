echo "deploying descriptiors in OSM" 

osm --hostname 192.168.100.24 nsd-delete mono_VM_ns
 
sleep 3

osm --hostname 192.168.100.24 vnfd-delete webserver_vnf
#osm nsd-create multi-VM_ns.tar.gz
