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
            # mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
            #                         priority=priority, match=match,
            #                         instructions=inst)
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=priority,
                                    match=match,
                                    instructions=inst,
                                    buffer_id=buffer_id,
                                    command=ofproto.OFPFC_ADD,
                                    cookie=0,
                                    cookie_mask=0,
                                    table_id=0,
                                    idle_timeout=0,
                                    hard_timeout =0
                                    )
        else:
            # mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
            #                        match=match, instructions=inst)
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=priority,
                                    match=match,
                                    instructions=inst,
                                    buffer_id=ofproto.OFP_NO_BUFFER,
                                    command=ofproto.OFPFC_ADD,
                                    cookie=0,
                                    cookie_mask=0,
                                    table_id=0,
                                    idle_timeout=0,
                                    hard_timeout =0
                                    )
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
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        vlan_header = pkt.get_protocols(vlan.vlan)    # If packet is tagged, it will have a null value

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        if eth.ethertype == 34525:
            # ignore IPv6
            return

        if eth.ethertype == ether_types.ETH_TYPE_8021Q:       #Checking for VLAN Tagged Packet
            vlan_header_present = 1
            src_vlan=vlan_header[0].vid
        else:
           vlan_header_present = 0 

        dst = eth.dst
        src = eth.src

        out_port = ofproto.OFPP_FLOOD
        actions = [ ]
        match=None
        
        #self.logger.info("packet in %s %s %s %s %s", dpid, src, dst, in_port, vlanid)

        # out_port= ofproto.OFPP_FLOOD  # Flood packet if there isn't a further condition to deal with it
        # vlanTagged2Port_in_s1 = {231: 4, 232: 5, 233: 6, 234: 7}
        # vlanTagged2Port_out_s1 =  {231: 1, 232: 1, 233:1, 234: 1}

        if dpid == 1:         
        # Forwarding logic for S1
            if (in_port == 1 and vlan_header_present == 1):
                out_port = 2
                #self.logger.info("From VM ... ")
                self.logger.info(dpid)
                self.logger.info(in_port)
                self.logger.info(eth)
                self.logger.info(vlan_header)
                actions.append(parser.OFPActionOutput(out_port))
                actions.append(parser.OFPActionPopVlan())
                match=parser.OFPMatch(in_port=in_port, eth_src=src)
                
            if (in_port == 2):  
                # Untagged traffic in ISL to laptop
                out_port = 1
                #self.logger.info("From client ... ")
                self.logger.info(dpid)
                self.logger.info(in_port)
                self.logger.info(eth)
                self.logger.info(vlan_header)
                #actions.append (parser.OFPActionPushVlan(ether.ETH_TYPE_8021Q)
                actions.append (parser.OFPActionPushVlan(ether_types.ETH_TYPE_8021Q))
                actions.append (parser.OFPActionSetField(vlan_vid=231))
                match=parser.OFPMatch(in_port=in_port, eth_src=src)

        # install a flow to avoid packet_in next time
        
        if match is None:
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
         
        self.add_flow_send(in_port, out_port, msg, match=match, actions=actions)  