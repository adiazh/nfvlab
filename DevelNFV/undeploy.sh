echo "deploying descriptiors in OSM" 

osm nsd-delete mono-VM_ns
 
sleep 3

osm vnfd-delete webserver_vnf
