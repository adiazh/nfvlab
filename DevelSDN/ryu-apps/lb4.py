
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import vlan

class webLoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    port_to_tag = {3:513, 4:231, 5:232, 6:233, 7:234}
    drop_actions=[]

    def __init__(self, *args, **kwargs):
        super(webLoadBalancer, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        
        datapath = ev.msg.datapath

        if datapath.id == 1:
            self.logger.info("Configuring datapath %s", datapath.id)
            self.switch1_features_handler(ev)
        else:
            self.logger.info("Configuring datapath %s", datapath.id)
            self.switch2_features_handler(ev)

    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        #ofproto = datapath.ofproto
        #parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = msg.datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        #self.logger.info("Ignoring Packet %s %s %s %s", dpid,in_port,eth.src,eth.dst)
    
    def add_flow(self, datapath, priority, match=None, actions=None, table_id=0, instructions=None, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        ##
        ## When actions and instructions are mixed, actions need to come before instruction
        ##
        if instructions is None:
            instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        elif actions is not None:
            instructions.insert(0,parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions))


        #inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]

        if buffer_id:
            # mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
            #                         priority=priority, match=match,
            #                         instructions=inst)
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=priority,
                                    match=match,
                                    instructions=instructions,
                                    buffer_id=buffer_id,
           #                         command=ofproto.OFPFC_ADD,
                                    cookie=0,
                                    cookie_mask=0,
                                    table_id=table_id,
                                    idle_timeout=0,
                                    hard_timeout =0
                                    )
        else:
            # mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
            #                        match=match, instructions=inst)
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=priority,
                                    match=match,
                                    instructions=instructions,
                                    buffer_id=ofproto.OFP_NO_BUFFER,
            #                        command=ofproto.OFPFC_ADD,
                                    cookie=0,
                                    cookie_mask=0,
                                    table_id=table_id,
                                    idle_timeout=0,
                                    hard_timeout =0
                                    )
        datapath.send_msg(mod)
    
    def send_actions(self,out_port,parser,pop=0,push=0,vlan=0):
        actions=[]
        if pop == 1:
            actions.append(parser.OFPActionPopVlan())
        if (push == 1 and vlan !=0):
            actions.append(parser.OFPActionPushVlan(ether_types.ETH_TYPE_8021Q))
            actions.append(parser.OFPActionSetField(vlan_vid=(0x1000 | vlan)))
        actions.append(parser.OFPActionOutput(out_port))
        return actions
    
    @staticmethod
    def goto_table(table_id, parser):
        return [parser.OFPInstructionGotoTable(table_id)]

    def switch1_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly. The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match=match, actions=actions)
        # Drop LLDP
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_LLDP)
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        # Drop STDP BPDU
        match = parser.OFPMatch(eth_dst="01:80:c2:00:00:00")
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        match = parser.OFPMatch(eth_dst="01:00:0c:cc:cc:cd")
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        # Drop Broadcast Sources
        match = parser.OFPMatch(eth_src="ff:ff:ff:ff:ff:ff")
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        # untagged traffic to mport
        match = parser.OFPMatch(in_port=1, vlan_vid=0x00000)
        actions = self.send_actions(2,parser)
        self.add_flow(datapath, 900, match=match, actions=actions)
        # all traffic from mport
        match = parser.OFPMatch(in_port=2)
        actions = self.send_actions(1,parser)
        self.add_flow(datapath, 900, match=match, actions=actions)
        for port in self.port_to_tag.keys():
            # tagged traffic from vm1
            match = parser.OFPMatch(in_port=port)
            actions = self.send_actions(1, parser)
            self.add_flow(datapath, 950, match=match, actions=actions)
            # tagged traffic to vm1
            match = parser.OFPMatch(in_port = 1,vlan_vid = (0x1000 | self.port_to_tag[port]))
            actions = self.send_actions(port, parser)
            self.add_flow(datapath, 950, match=match, actions=actions)
    


    def switch2_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match=match, actions=actions)
        # Drop LLDP
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_LLDP)
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        # Drop STDP BPDU
        match = parser.OFPMatch(eth_dst="01:80:c2:00:00:00")
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        match = parser.OFPMatch(eth_dst="01:00:0c:cc:cc:cd")
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        # Drop Broadcast Sources
        match = parser.OFPMatch(eth_src="ff:ff:ff:ff:ff:ff")
        self.add_flow(datapath, 1000, match=match, actions=self.drop_actions)
        # TODO:
        # Untagged traffic from in_port=1 to out_port=2
        match = parser.OFPMatch(in_port=1, vlan_vid=0x0000)
        actions = self.send_actions(2,parser)
        self.add_flow(datapath, 1000, match=match, actions=actions)
        # Tagged traffic juju backplane 
        match = parser.OFPMatch(in_port=1,vlan_vid=(0x1000 | 513))
        actions = self.send_actions(4, parser)
        self.add_flow(datapath, 1000, match=match, actions=actions)
        match = parser.OFPMatch(in_port=4,vlan_vid=(0x1000 | 513))
        actions = self.send_actions(1, parser)
        self.add_flow(datapath, 1000, match=match, actions=actions)
        # Any traffic from in_port=2 to out_port=1 
        match = parser.OFPMatch(in_port=2)
        actions = self.send_actions(1, parser)
        self.add_flow(datapath, 1000, match=match, actions=actions)
        # Handle tagged traffic from VMs and untagged it before sending it to client (out_port=3)
        for port in [4,5,6,7]:
            match = parser.OFPMatch(in_port=1,vlan_vid=(0x1000 | self.port_to_tag[port]))
            actions = [parser.OFPActionPopVlan()]
            inst = [parser.OFPInstructionGotoTable(self.port_to_tag[port])]
            self.add_flow(datapath, 998, match=match, actions=actions, table_id=0, instructions=inst)
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 1000,  match=match, actions=actions, table_id=self.port_to_tag[port], instructions=None)
            # Create tables 236, 237, 238, 239 with pushVlan and outport to tag back client's traffic
            match = parser.OFPMatch(in_port=3,vlan_vid=0x0000)
            if port == 4:
                inst = [parser.OFPInstructionGotoTable(self.port_to_tag[port]+5)]
                self.add_flow(datapath, 1000, match=match, actions=None, table_id=0, instructions=inst)
            actions = [parser.OFPActionPushVlan(ether_types.ETH_TYPE_8021Q), parser.OFPActionSetField(vlan_vid=(0x1000 | self.port_to_tag[port])), parser.OFPActionOutput(1)]
            self.add_flow(datapath, 1000, match=match, actions=actions, table_id=(self.port_to_tag[port]+5), instructions=None)

        # Push VM! vlan tagged to client's incoming   
        #match = parser.OFPMatch(in_port=3,vlan_vid=0x0000)
        #actions = self.send_actions(1, parser,pop=0,push=1,vlan=231)
        #self.add_flow(datapath, 1000, match=match, actions=actions)
