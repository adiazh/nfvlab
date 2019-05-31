
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
           #                         command=ofproto.OFPFC_ADD,
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
            #                        command=ofproto.OFPFC_ADD,
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
        vlan_header = pkt.get_protocols(vlan.vlan)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        if eth.ethertype == 34525:
            # ignore IPv6
            return

        dst = eth.dst
        src = eth.src

        vlan_dstPort_in_s1 = {513:3, 231:4, 232:5, 233:6, 234:7}
        juju_vlan = 513

        if eth.ethertype == ether_types.ETH_TYPE_8021Q:       #Checking for VLAN Tagged Packet
            vlan_header_present = 1
            src_vlan=vlan_header[0].vid
        else:
           vlan_header_present = 0
           dst_vlan = 231
           src_vlan = 0

        if dpid == 1:
        # Forwarding logic for S1
            if in_port == 2:
                # Traffic from mport se envia al s2
                out_port = 1
                match = parser.OFPMatch(in_port=in_port)
                actions=[parser.OFPActionOutput(out_port)]

            if (in_port == 1 and vlan_header_present == 0):
                # laptop sends traffic untagged
                out_port = 2
                match = parser.OFPMatch(in_port=in_port, vlan_vid=0x0000)
                actions=[parser.OFPActionOutput(out_port)]

            if (in_port == 1 and vlan_header_present == 1):
                # Tagged traffic from S2
                out_port = vlan_dstPort_in_s1[src_vlan]
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | src_vlan))
                self.logger.info(match)
                actions=[parser.OFPActionOutput(out_port)]

            if  in_port == 4:
                # Tagged traffic from VMs to S2
                out_port = 1
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | src_vlan))
                actions=[parser.OFPActionOutput(out_port)]

            if  in_port == 5:
                # Tagged traffic from VMs to S2
                out_port = 1
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | src_vlan))
                actions=[parser.OFPActionOutput(out_port)]

            if  in_port == 6:
                # Tagged traffic from VMs to S2
                out_port = 1
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | src_vlan))
                actions=[parser.OFPActionOutput(out_port)]

            if  in_port == 7:
                # Tagged traffic from VMs to S2
                out_port = 1
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | src_vlan))
                actions=[parser.OFPActionOutput(out_port)]

            if in_port == 3:
                out_port = 1
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | juju_vlan))
                actions=[parser.OFPActionOutput(out_port)]

        if dpid == 2:
            # Forwarding logic for S2
            if (in_port == 1 and vlan_header_present == 0):
                # Untagged traffic in ISL to laptop
                out_port = 2
                match = parser.OFPMatch(in_port=in_port, vlan_vid=0x0000)
                actions=[parser.OFPActionOutput(out_port)]

            if (in_port == 2 and (eth.ethertype == ether_types.ETH_TYPE_ARP or eth.ethertype == ether_types.ETH_TYPE_IP)):
                out_port = 1
                match = parser.OFPMatch(in_port=in_port, vlan_vid=0x0000)
                actions=[parser.OFPActionOutput(out_port)]

            if in_port == 3:
                out_port = 1
                match=parser.OFPMatch(in_port=in_port)
                actions = [parser.OFPActionPushVlan(ether_types.ETH_TYPE_8021Q), parser.OFPActionSetField(vlan_vid=(0x1000 | dst_vlan)), parser.OFPActionOutput(out_port)]

            if (in_port == 1 and vlan_header_present == 1):
                if src_vlan == juju_vlan:
                    out_port = 4
                    match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | juju_vlan))
                    actions=[parser.OFPActionOutput(out_port)]
                else:
                    out_port = 3
                    match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | src_vlan))
                    actions=[parser.OFPActionPopVlan(),parser.OFPActionOutput(out_port)]

            if in_port == 4:
                out_port = 1
                match = parser.OFPMatch(in_port=in_port,vlan_vid=(0x1000 | juju_vlan))
                actions=[parser.OFPActionOutput(out_port)]

        self.logger.info("Sw=%s, InPort=%s, OutPort=%s, VlanId=%s, src=%s, dst=%s, ether:%s", dpid,in_port,out_port,src_vlan,src,dst,eth.ethertype)

        if match is None:
            self.logger.info('no match')
            match = parser.OFPMatch(in_port=in_port)
            return

        self.add_flow_send(in_port, out_port, msg, match=match, actions=actions)
