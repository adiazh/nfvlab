
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import vlan
from ryu.ofproto import ether


class webLoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(webLoadBalancer, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def add_flow_send(self, in_port, out_port, msg, match=None, actions=None):
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # if there is a match rule, install it
        if match is not None:
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                # Buffered, install rule and return
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                # _Unbuffered, install rule and send packet
                self.add_flow(datapath, 1, match, actions)

        #Send Packet
        data=None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        doPush = 0
        doPop = 0

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        vlanh = pkt.get_protocols(vlan.vlan)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        #self.mac_to_port.setdefault(dpid, {})

        vlanid = 0

        if vlanh:
            vlanid = vlanh[0].vid


        #self.logger.info("packet in %s %s %s %s %s", dpid, src, dst, in_port, vlanid)

        out_port= ofproto.OFPP_FLOOD  # Flood packet if there isn't a further condition to deal with it
        vlanTagged2Port_in_s1 = {231: 4, 232: 5, 233: 6, 234: 7}
        vlanTagged2Port_out_s1 =  {231: 1, 232: 1, 233:1, 234: 1}


        if dpid == 1:         
        # Forwarding logic for S1
            if in_port == 2:  
                # Traffic from mport se envia al s2
                out_port = 1  
            if (in_port == 1 and vlanid == 0):
                # laptop sends traffic untagged
                out_port = 2
            if (in_port == 1 and vlanid != 0):  
                # Tagged traffic from S2
                out_port = vlanTagged2Port_in_s1[vlanid]
            if  in_port in [4,5,6,7]:
                # Tagged traffic from VMs to S2
                out_port = vlanTagged2Port_out_s1[vlanid]
            if in_port == 3:
                out_port = 1
            
        if dpid ==2:         
            # Forwarding logic for S2
            if (in_port == 1 and vlanid == 0):  
                # Untagged traffic in ISL to laptop
                out_port = 2
            if (in_port == 2 and (eth.ethertype == ether_types.ETH_TYPE_ARP or eth.ethertype == ether_types.ETH_TYPE_IP)):
                out_port = 1
            if in_port==3:
                out_vlan = 231
                doPush = 1
            if (in_port == 1 and vlanid != 0):
                out_port = 3
                doPop = 1
            if in_port == 4:
                out_port = 1
        
        self.logger.info("Sw=%s, InPort=%s, OutPort=%s, VlanId=%s, src=%s, dst=%s, ether:%s", dpid,in_port,out_port,vlanid,src,dst,eth.ethertype)
        actions = [parser.OFPActionOutput(out_port)]
        
        if doPush == 1:
            actions = [
                parser.OFPActionPushVlan(ether.ETH_TYPE_8021Q),
                parser.OFPActionSetField(vlan_vid=out_vlan),
                parser.OFPActionOutput(out_port)]
        if doPop == 1:
            actions = [
                parser.OFPActionPopVlan(),
                parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        match=None
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            #if msg.buffer_id != ofproto.OFP_NO_BUFFER:
            #    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
            #    return
            #else:
            #    self.add_flow(datapath, 1, match, actions)
        #data = None
        #if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        #    data = msg.data

        #out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
        #                          in_port=in_port, actions=actions, data=data)
        #datapath.send_msg(out)
        self.add_flow_send(in_port, out_port, msg, match=match, actions=actions)
