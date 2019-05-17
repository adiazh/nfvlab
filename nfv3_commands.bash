source OSM-openrc.sh 
export PATH=$PATH:/usr/share/osm-devops/descriptor-packages/tools/


neutron net-create mgmt --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=513 --shared 
neutron subnet-create --name subnet-mgmt mgmt 10.208.0.0/24 --allocation_pool start=10.208.0.2,end=10.208.0.254

sudo osm --hostname 192.168.100.24 vim-create --name osm-group13 --user osm --password osm --tenant OSM --auth_url $OS_AUTH_URL --account_type openstack --config '{security_groups: default, keypair: osm-kp}'
osm vim-list
osm ns-list
osm vnfd-list
osm nsd-list

###### Miles

export JUJU_REPOSITORY=$HOME/charms

cd $JUJU_REPOSITORY/layers
charm create simple

cd $HOME/charms/layers
charm create ffmpeg



mkdir ffmpeg/actions; for action in apt load server feed; do cp simple/actions/touch ffmpeg/actions/$action; done



osm ns-create --ns_name group13_server --nsd_name ubuntu_transcoder_ns --vim_account osm-group13 --config '{
        vnf: [ {
                member-vnf-index: "1", 
                vdu: [{
                    id: ubuntu_vnfd-VM, 
                    interface: [ {name: eth0, floating-ip-required: True } ]
                    }] 
            }, 
            {
                member-vnf-index: "2", 
                vdu: [ {
                    id: ubuntu_ffserver_vnfd-VM, 
                    interface: [ {name: eth0, floating-ip-required: True } ]
                        }
                    ] 
                } 
            ] 
        }'


        JointLab

neutron net-create mgmt --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=513 --shared 
neutron subnet-create --name subnet-mgmt mgmt 10.208.0.0/24 --allocation_pool start=10.208.0.2,end=10.208.0.254

neutron net-create tag1 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=231 --shared 
neutron subnet-create --name subnet-tag1 tag1 10.13.1.0/24 --allocation_pool start=10.13.1.2,end=10.13.1.254

neutron net-create tag2 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=232 --shared 
neutron subnet-create --name subnet-tag2 tag2 10.13.2.0/24 --allocation_pool start=10.13.2.2,end=10.13.2.254

neutron net-create tag3 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=233 --shared 
neutron subnet-create --name subnet-tag3 tag3 10.13.3.0/24 --allocation_pool start=10.13.3.2,end=10.13.3.254

neutron net-create tag4 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=234 --shared 
neutron subnet-create --name subnet-tag4 tag4 10.13.4.0/24 --allocation_pool start=10.13.4.2,end=10.13.4.254