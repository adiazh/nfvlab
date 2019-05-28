#!/usr/bin/env python


from mininet.node import Host
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.log import error


class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        #intf.name = newName
        # add VLAN interface to host's name to intf map
        #self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }


# pylint: disable=arguments-differ

class LabSetup ( Topo ):
    def build (self, webip='10.13.1.3/24', mac='02:61:fb:eb:25:a2'):
        s1 = self.addSwitch('s1')
        vm1 = self.addHost ('w1', cls=VLANHost, vlan=231, ip=webip, mac=mac )
        client = self.addHost ('client', ip = '10.13.1.10/24')
        self.addLink( s1, vm1 )
        self.addLink( s1, client )
        

def createLabTopo():
    """ Creates Lab SDN"""

    from mininet.node import RemoteController

    net = Mininet( topo=LabSetup(), controller=partial( RemoteController, ip='127.0.0.1', port=6633 ))
    #net.addController(name='ryu', controller=cont)
    net.start()
    CLI( net )
    net.stop()


if __name__ == '__main__':
    import sys
    from functools import partial
    from mininet.net import Mininet
    from mininet.cli import CLI
    from mininet.topo import SingleSwitchTopo
    from mininet.log import setLogLevel


    setLogLevel( 'info' )

    createLabTopo()
