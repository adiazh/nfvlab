source OSM-openrc.sh 
export PATH=$PATH:/usr/share/osm-devops/descriptor-packages/tools/

sudo osm --hostname 192.168.100.24 vim-create --name osm-group13 --user osm --password osm --tenant OSM --auth_url $OS_AUTH_URL --account_type openstack --config '{security_groups: default, keypair: osm-kp}'

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


neutron net-create mgmt --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=513 --shared 
neutron subnet-create --name subnet-mgmt mgmt 10.208.0.0/24 --allocation_pool start=10.208.0.2,end=10.208.0.254

