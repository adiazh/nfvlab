# export OSM_HOSTNAME=osm-r4
# export OSM_HOSTNAME=192.168.100.24
# export OS_AUTH_URL = TODO take it from OSM-rc.sh

# create VIM account With no floating IP addresses
sudo osm vim-create --name osm-group13 --user osm --password osm --tenant OSM --auth_url $OS_AUTH_URL --account_type openstack --config '{security_groups: default, keypair: osm-kp}'

osm vim-list
osm ns-list
osm vnfd-list
osm nsd-list

