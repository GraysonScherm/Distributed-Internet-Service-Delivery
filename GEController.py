# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An OpenFlow 1.0 L2 learning switch implementation.
"""

import logging
import struct

import sqlite3
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.controller import dpset
from netaddr import *
from utils import *
from ryu.lib.mac import haddr_to_bin
from PropFair import *

'''
This file is edited from Ryu example which is located at  ryu/ryu/app/simple_switch.py.
According to its licecse(please don't trust my reading and read it), we can modify and use it as long as we keep the old license and state we've change the code. --Joe
'''

FLOW_HARD_TIMEOUT = 30
FLOW_IDLE_TIMEOUT = 10

T = [1]*3 #previous scheduled memory


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
    
    servers = [0, [1, '10.10.1.1', '02:71:2a:55:7f:98'], [3, '10.10.1.2', '02:b4:9c:c8:84:42'], [4, '10.10.1.3', '02:51:94:52:e2:a7']]
    serverLoad = [0, 0, 0]


    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    
    def add_flow(self, datapath, match, act, priority=0, idle_timeout=0, flags=0, cookie=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
   
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, actions=act, flags=flags, idle_timeout=idle_timeout, cookie=cookie)
        datapath.send_msg(mod)

    def forward_packet(self, msg, port_list):

        datapath = msg.datapath
        ofproto = datapath.ofproto

        actions = []
        
        for p in port_list:
            actions.append( createOFAction(datapath, ofproto.OFPAT_OUTPUT, p) )

        # install a flow to avoid packet_in next time
        if ofproto.OFPP_FLOOD not in port_list:
            match = getFullMatch( msg )
            sendFlowMod(msg, match, actions, FLOW_HARD_TIMEOUT, FLOW_IDLE_TIMEOUT, msg.buffer_id)
        else :

            sendPacketOut(msg=msg, actions=actions, buffer_id=msg.buffer_id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        global T

        dl_type_ipv4 = 0x0800
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        dst = eth.dst
        src = eth.src
	ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        dpid = datapath.id

	tcp_sgm = pkt.get_protocol(tcp.tcp)	

	if tcp_sgm:
           self.logger.info("packet in %s %s %s %s; TCP ports: source= %s and dest=%s", dpid, ipv4_pkt.src, ipv4_pkt.dst, msg.in_port, tcp_sgm.src_port, tcp_sgm.dst_port)
           match = parser.OFPMatch (dl_type = dl_type_ipv4, nw_src=self.ipv4_to_int(ipv4_pkt.src), tp_src=tcp_sgm.src_port, nw_proto = 6)
          # self.logger.info("T: Server1 - %d, Server2 - %d, Server3 - %d ", self.T[0], self.T[1], self.T[2])           
           GEvector, lambdaList = fetchServerInfo()
#	   MAX, self.T = Propfair(GEvector,0,lambdaList, self.T)
	   self.logger.info("Calling Propfair")
	   self.logger.info("GEVector status: Server1 - %d, Server2 - %d, Server3 - %d ", GEvector[0], GEvector[1], GEvector[2])
	   MAX, T, T2 = Propfair(GEvector,T)

           print("T2")
           print(T2)
 	   serverID = MAX+1 #scheduler()

           actions = [parser.OFPActionSetNwDst(self.ipv4_to_int(self.servers[serverID][1])), 
                    parser.OFPActionSetDlDst(haddr_to_bin(self.servers[serverID][2])), parser.OFPActionOutput(self.servers[serverID][0])]
           self.serverLoad[serverID-1]+=1
	   self.add_flow(datapath, match, actions, 1, 60, ofproto.OFPFF_SEND_FLOW_REM, serverID)
           
           #rewriting response header
           match = parser.OFPMatch (dl_type = dl_type_ipv4, nw_src=self.ipv4_to_int(self.servers[serverID][1]), 
                                    nw_dst=self.ipv4_to_int(ipv4_pkt.src), tp_dst=tcp_sgm.src_port)
           actions = [ parser.OFPActionSetNwSrc (self.ipv4_to_int(ipv4_pkt.dst)), #REWRITE IP HEADER FOR TCP CONNECTION ESTABLISHMENT. rewriting eth is not needed parser.OFPActionSetDlSrc(haddr_to_bin(eth.dst)), 
                    parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
           self.add_flow(datapath, match, actions, 3, 20)

#           self.logger.info("Current number of users: Server1 - %d, Server2 - %d, Server3 - %d", lambdaList[0], lambdaList[1], lambdaList[2])
           self.logger.info("Flow installed for client %s and serverID %d", ipv4_pkt.src, serverID)
           self.logger.info("Current number of users: Server1 - %d, Server2 - %d, Server3 - %d", self.serverLoad[0], self.serverLoad[1], self.serverLoad[2])
           actions = []
           actions.append( createOFAction(datapath, ofproto.OFPAT_OUTPUT, self.servers[serverID][0]) ) 
           sendPacketOut(msg=msg, actions=actions, buffer_id=msg.buffer_id)

	
    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removal_handler(self, ev):
        msg = ev.msg
        match = msg.match
	reason = msg.reason
        self.logger.info("Client released serverID = %d", msg.cookie)
        serverId = msg.cookie - 1
	if self.serverLoad[serverId] > 0:
	 self.serverLoad[serverId]-=1



    def remove_table_flows(self, datapath, table_id, match, instructions):
        """Create OFP flow mod message to remove flows from table."""
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, match=match, command=ofproto.OFPFC_DELETE, 
                             cookie=0, idle_timeout=0,out_port=65535, buffer_id=4294967295, flags=0, hard_timeout=0,priority=0, actions=[])
        return flow_mod

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def _event_switch_enter_handler(self, ev):
       dl_type_ipv4 = 0x0800
       dl_type_arp = 0x0806
       dp = ev.dp
       ofproto = dp.ofproto
       parser = dp.ofproto_parser

       self.logger.info("Switch connected %s. Delete previous flows...", dp)
       
       empty_match = parser.OFPMatch()
       instructions = []
       flow_mod = self.remove_table_flows(dp, 0,empty_match, instructions)
       dp.send_msg(flow_mod)

       self.logger.info("Install the default flows...")

       addressList = ('10.10.1.1', '10.10.1.2', '10.10.1.3') # process packets from servers normally
      # hwAddressList = ('02:71:2a:55:7f:98') #filter client packets
       actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
       for address in addressList:
         match = parser.OFPMatch(dl_type = dl_type_ipv4, nw_src = address)
         self.add_flow(dp, match, actions, 2, 0)     
#        self.logger.info("Added l2 flow for address %s", address)
       
       match = parser.OFPMatch(dl_type = dl_type_arp)#process arp packets normally
       self.add_flow(dp, match, actions, 1, 0)

       match = parser.OFPMatch ()
       actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
       self.add_flow(dp, match, actions, 0, 0) #add miss flow

       self.logger.info("Added default rules for servers and miss-flow. Ready to work!")

    def ipv4_to_int(self, string):
       	ip = string.split('.')
       	assert len(ip) == 4
       	i = 0
       	for b in ip:
    		b = int(b)
        	i = (i << 8) | b
        return i

