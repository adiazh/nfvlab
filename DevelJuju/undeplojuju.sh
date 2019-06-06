echo "deploying descriptiors in OSM" 

osm nsd-delete monojuju-VM_ns
 
sleep 3

osm vnfd-delete web_juju_vnf
