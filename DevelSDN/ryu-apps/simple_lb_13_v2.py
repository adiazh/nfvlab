
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
        self.mac_to_port = {}

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

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        if not vlanh:
            vid = 0
            self.logger.info (vlanh)
        else:
            vid = vlanh[0].vid
            self.logger.info (vid)

        # learn a mac address to avoid FLOOD next time.
        #self.mac_to_port[dpid][src] = in_port

        #if dst in self.mac_to_port[dpid]:
        #    out_port = self.mac_to_port[dpid][dst]
        #else:
        #    out_port = ofproto.OFPP_FLOOD

        if dpid == 1:
            if in_port == 2:
                out_port = 1
                self.logger.info("Soy S1 mando esto al S2 por que viene de mport")
            else:
                if in_port == 1:
                    if vid == 0:
                        self.logger.info("Soy S1 mando esto al mport viene no tageado")
                        out_port = 2
                    else:
                        if vid == 231:
                            out_port = 4
                        if vid == 232:
                            out_port = 5
                        if vid == 233:
                            out_port = 6
                        if vid == 234:
                            out_port = 7
                        self.logger.info("Soy %d mando al puerto %d por ser de vlan %d", dpid, out_port, vid )
                else:
                    if (in_port == 4 or in_port == 5 or in_port == 6 or in_port == 7):
                        self.logger.info("Soy el VM del puerto %d y me voy al S2", in_port)
                        out_port = 1
                    else:
                        out_port = ofproto.OFPP_FLOOD
        else:
            if (dpid ==2 and in_port == 1 and vid == 0):
                out_port = 2
            else:
                if (dpid == 2 and in_port ==2 and (eth.ethertype == ether_types.ETH_TYPE_ARP or eth.ethertype == ether_types.ETH_TYPE_IP)):
                    out_port = 1
                else:
                    if in_port==3:
                        out_vlan = 231
                        f = parser.OFPMatchField.make(ofproto.OXM_OF_VLAN_VID,out_vlan)
                        doPush = 1
                    if (in_port == 1 and vid != 0):
                        out_port = 3
                        doPop = 1
                    else:
                        out_port = ofproto.OFPP_FLOOD

        if doPush == 1:
            actions = [parser.OFPActionOutput(out_port), parser.OFPActionPushVlan(ether.ETH_TYPE_8021Q)]
        else:
            if doPop == 1:
                actions = [parser.OFPActionOutput(out_port), parser.OFPActionPopVlan()]
            else:
                actions = [parser.OFPActionOutput(out_port)]



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
