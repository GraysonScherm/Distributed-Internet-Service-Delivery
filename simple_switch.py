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
from ryu.controller import dpset
from utils import *
'''
This file is edited from Ryu example which is located at  ryu/ryu/app/simple_switch.py.
According to its licecse(please don't trust my reading and read it), we can modify and use it as long as we keep the old license and state we've change the code. --Joe
'''

FLOW_HARD_TIMEOUT = 30
FLOW_IDLE_TIMEOUT = 10

class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    
    def add_flow(self, datapath, match, act, priority=0, idle_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
   
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, actions=act, idle_timeout=idle_timeout)
        datapath.send_msg(mod)


    def get_out_port(self,msg):

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        dst = eth.dst
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        return out_port

    def macLearningHandle(self, msg) :
        # learn a mac address to avoid FLOOD next time.
        datapath = msg.datapath
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        src = eth.src
        dpid = datapath.id	
        
        self.mac_to_port.setdefault(dpid, {})
        self.logger.info("mac table: in_port %s source %s dpid %s", msg.in_port, src, dpid)
	
        self.mac_to_port[dpid][src] = msg.in_port

    def forward_packet(self, msg, port_list) :

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
	if ipv4_pkt:
          self.logger.info("packet in %s %s %s %s", dpid, ipv4_pkt.src, ipv4_pkt.dst, msg.in_port)
	
	# if its ipv4_packet, install a flow with certain IDLE_TIME for the client to output to port N, given by the request to the scheduler.
	# Send the packet to that port. 

#	fd = os.open("/tmp/ryu/Distributed-Internet-Service-Delivery/controller.db", os.O_RDONLY)
#	conn = sqlite3.connect('/dev/fd/%d' % fd)
#	os.close(fd)
#        cursor = conn.cursor()
#        addressList = ('10.10.1.1', '10.10.1.2', '10.10.1.3') #filter client packets
#	pkt_arp = pkt.get_protocol(arp.arp)
#	if pkt_arp:
#         if pkt_arp.dst_ip in addressList: 
#	  print (pkt_arp)
#	  destination = (pkt_arp.dst_ip,) #get destination ip
#	  print (destination)
#	  cursor.execute("SELECT * from energyValues where id = (SELECT MAX(id) from energyValues where private_ip = ?)", destination)
#	  #	energyValue = cursor.fetchone()[1]
#	  recentInfo = cursor.fetchall()
#          print (recentInfo)
#	  print ("Energy value: " + str(recentInfo[0][1]))
#	  #	set.logger.info ("Last energy value: %s", str(energyValue))

#        self.macLearningHandle(msg)

#        out_port = self.get_out_port(msg)	

        #self.forward_packet(msg, [out_port])

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)

    
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def _event_switch_enter_handler(self, ev):
       dl_type_ipv4 = 0x0800
       dl_type_arp = 0x0806
       dp = ev.dp
       ofproto = dp.ofproto
       parser = dp.ofproto_parser
       self.logger.info("Wow! switch connected %s", dp)
       addressList = ('10.10.1.1', '10.10.1.2', '10.10.1.3') # process packets from servers normally
      # hwAddressList = ('02:71:2a:55:7f:98') #filter client packets
       actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
       for address in addressList:
         match = parser.OFPMatch(dl_type = dl_type_ipv4, nw_src = address)
         self.add_flow(dp, match, actions, 1, 100)     
#        self.logger.info("Added l2 flow for address %s", address)
       
       match = parser.OFPMatch(dl_type = dl_type_arp)#process arp packets normally
       self.add_flow(dp, match, actions, 1, 100)
	
       match = parser.OFPMatch ()
       actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
       self.add_flow(dp, match, actions, 0) #add miss flow
       self.logger.info("Added default rules and miss flow")
