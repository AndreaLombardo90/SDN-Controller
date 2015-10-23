from pox.core import core
from collections import defaultdict
import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree
from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os
import re
from switch import Switch
from net_graph import NetGraph
import signal
from edge import Edge
from path import Path
from usersmanager import UsersManager
from rule import Rule

log = core.getLogger()



class VideoSlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)
	signal.signal(signal.SIGINT, self.signal_handler)          
	#list of Switch objects
	self.switches = []
	#graph used for path computation
	self.net_graph = NetGraph()
	self.policies = {}
        self.usrmgr = UsersManager()
	#loading user-classes policies
	self.loadpolicies()
	#loading users (TODO: new thread, managing new users communicated by another user manager server)
	self.loadUsers()
	#list of possible hosts (to be cleaned in order to avoid hosts/switch possible mix) linked to their switch
	#tuple in the form of (host_mac, switch_mac)
	self.possible_hosts = []
	#list of rules
	self.rules = []
	self.loadrules()
	out = file("user_debug.txt", "w")
	out.write(self.usrmgr.print_users())
	out.close()	
  
    
    def loadrules(self):
	rules_config = file("rules.conf", "r")
	line = rules_config.readline()
	while len(line) != 0:
	  r = Rule(line)
	  self.rules.append(r)
	  line = rules_config.readline()
	
    def loadpolicies(self):
	#policies are specified in queues_policies.conf file according to the following grammar:
	#@class_name @bandwidth (bandwidth in Mbit)      
	queues_config = file("queues_policies.conf", "r")
	line = queues_config.readline().split()
	while len(line) != 0:
	  if (len(line) == 2):
	    if (type(line[0]) is str and line[1].isdigit()):
	      self.policies[line[0]] = line[1]        
	  line = queues_config.readline().split()
	
	self.usrmgr.set_policies(self.policies)	
    
    def loadUsers(self):
        #users are specificed in users_classes.conf file along with classes they belong according to the following grammar:
        #@class_name
        #@user_ip
	users_file = file("users_classes.conf", "r")
	pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
	
	line = users_file.readline()
	actual_class = line
	
	
	while line != "":
	  if (pat.match(line)):
	    self.usrmgr.addUser(actual_class, line, "")
	  else:
	    self.usrmgr.addClass(line)
	    actual_class = line	    

	  line = users_file.readline()
	
	
	users_file.close()

    
    
    def _handle_LinkEvent (self, event):
	#event raised each time a link between two switches goes up or down in the net.
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)
                   
        if (event.added):
	  self.net_graph.addEdge(sw1,sw2,1)
	  self.net_graph.addEdge(sw2,sw1,1)
	elif (event.removed):
	  self.net_graph.removeEdge(sw1,sw2)
	  self.net_graph.removeEdge(sw2,sw1)
	  for s in self.switches:
	    for key in s.ARPTable.keys():
	      s.ARPTable[key] = []
	  for s in self.switches:
	    s.ARPTable.clear()
	    
	    
	  

	
    def clean_hosts(self):
      #this method removes switches from possible hosts list
      to_be_removed = []
      
      for switch in self.switches:
	for host in self.possible_hosts:
	  if host[0] == switch.dpid:
	    to_be_removed.append(host)
      
      for h in to_be_removed:
	self.possible_hosts.remove(h)
      
      output = file("hosts.txt", "w")
      output.write("hosts:\n")
      for h in self.possible_hosts:
	output.write(h[0] + " " + h[1] + "\n")
	
      output.close()
      
    
    def printswitches(self):
      #debug method. it prints ARP table of each switch in the net
      output = file("rules.txt", "w")
      
      for r in self.rules:
	output.write(r.to_s())
	
      output.close()
    
    #every time a packet arrive to controller we'll update the graph according to the new
    #discovered hosts
    def update_graph(self):
      for host in self.possible_hosts:
	self.net_graph.addEdge(host[1], host[0], 0)
	self.net_graph.addEdge(host[0], host[1], 0)
    
    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """    
        packet = event.parsed
	self.printswitches()
	self.clean_hosts()
	self.update_graph()

	#check if this packet activates some rule
	check = False
	
	for r in self.rules:
	  if ((r.check_rule(event.parsed)) == 1):
	    #rule checked, must drop packet
	    check = True
	    break	 	
	
	
	def drop():
	    d = file("drop.txt", "w")
	    d.write("drop " + str(check) + " " + str(packet.src) + " " + str(packet.dst) + "\n")
	    d.close()
	    msg = of.ofp_flow_mod()
	    msg.match = of.ofp_match.from_packet(packet, event.port)
	    #TODO it seems that if one does not specify any action it will result in a drop by the switch
	    #msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	    msg.data = event.ofp
	    msg.in_port = event.port
	    event.connection.send(msg)	    
	
        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)
            
            
            forw = file("forw.txt", "w")
            forw.write("forwardo " + str(packet.src) + " " + str(packet.dst) + "\n")
            forw.close()
            
            if packet.dst.is_multicast:
                flood()
                return
            else:
                log.debug("Got unicast packet for %s at %s (input port %d):",
                          packet.dst, dpid_to_str(event.dpid), event.port)

		
                try:
		  
		    #TODO:forwarding of packets according to source/destination user and his class
		    #using Dijkstra
		  
		    #controllo il dpid dello switch.
		    #se nella sua arp table c'e' l'entry che mi serve (coppia dst MAC -> porta), inoltro senza problemi e
		    #eventualmente mi marco che su input ho connesso il MAC in src
		    
		    forwarded = False
		    #source may be an host (MAC first time seen by switch)
		    found_host = False
		    for h_tuple in self.possible_hosts:
		      if h_tuple[0] == str(packet.src):
			found_host = True
		    if found_host == False:
		      self.possible_hosts.append((str(packet.src), this_dpid))		    
		    
		    #forwardo se esiste, l'associazione (MAC -> porta output)
		    for s in self.switches:
		      if s.dpid == this_dpid:
			stringa = str(packet.src)
	
			
			
			
			if s.ARPTable.keys().__contains__(stringa) == False:
			  s.ARPTable[stringa] = []
			  s.ARPTable[stringa].append(event.port)				  
			elif s.ARPTable.keys().__contains__(stringa) == True and s.ARPTable[stringa].__contains__(event.port) == False:
			  s.ARPTable[stringa].append(event.port)
			
			for k in s.ARPTable.keys():
			  if k == packet.dst:
			    #entry disponibile, inoltro sulla porta corretta
			    msg = of.ofp_flow_mod()
			    #msg.idle_timeout = of.OFP_FLOW_PERMANENT
			    #msg.hard_timeout = of.OFP_FLOW_PERMANENT
			    msg.match = of.ofp_match.from_packet(packet, event.port)
			    for entry in s.ARPTable[k]:
			      msg.actions.append(of.ofp_action_output(port = int(entry)))
			      msg.data = event.ofp
			      #msg.in_port = event.port
			      event.connection.send(msg)
			    forwarded = True		    
			    '''
			    msg = of.ofp_packet_out()
			    msg.actions.append(of.ofp_action_output(port = int(s.ARPTable[k])))
			    msg.data = event.ofp
			    msg.in_port = event.port
			    event.connection.send(msg)			    
			    '''
			  
		    
		    if forwarded == False:
		      #non conosco su quale porta mandare il pacchetto. lo hubbifizzo.
		      msg = of.ofp_flow_mod()
		      #msg.idle_timeout = of.OFP_FLOW_PERMANENT
		      #msg.hard_timeout = of.OFP_FLOW_PERMANENT
		      msg.match = of.ofp_match.from_packet(packet, event.port)
		      msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
		      msg.data = event.ofp
		      msg.in_port = event.port
		      event.connection.send(msg)		      
                    
                    #prendo il pacchetto in ingresso
                    #controllo se nella mia mappa (MAC) -> input port ho la entry corrispondente a dove deve andare il pacchetto.
                    #se si, inoltro su quella porta
                    #senno', floodo su tutte le porte
                    #in ogni caso mi marco che i pacchetti da srcMAC arrivano da quella input port
                    #il dstMAC dev'essere in una delle altre porte, prima o poi lo scopriro'
		      correct = file("correct.txt", "w")
		      correct.write(str(forwarded))
		      correct.close()

                except AttributeError:
                    log.debug("packet type has no transport ports, flooding")

        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        if check == False:
	  forward()
	else:
	  drop()


    def _handle_ConnectionUp(self, event):
        #event raised each time a new switch goes up
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)
	
	#check if this switch is already known to the controller
	check = False
	
	for i in self.switches:
	  if (i.dpid == dpid):
	    check = True
	
	if check == False:
	  s = Switch(dpid)
	  self.switches.append(s)
	  for port in event.ofp.ports:
	    s.addPort(port.name, port.port_no, port.hw_addr)
	
	
	for s in self.switches:
	  for port in s.ports:
	    #insert all queues-policies for every port of this switch  
	    
	    #building the corresponding ovs-vsctl command
	    command = "ovs-vsctl set port " + port.ifname + " qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0"
	    queue_index = 1
	    for key in self.policies.keys():
	      command = command + "," + str(queue_index) + "=@q" + str(queue_index) 
	      queue_index = queue_index + 1
	      if queue_index == len(self.policies.keys()):
		break	      
            command = command + " -- "
            
            queue_index = 0
            for key in self.policies.keys():
	      command = command + "--id=@q" + str(queue_index) + " create queue other-config:min-rate=" + str(self.policies[key]) + " other-config:max-rate=" + str(self.policies[key]) + " -- "
	      queue_index = queue_index + 1
	      if queue_index == len(self.policies.keys()):
		break
	    os.system(command)
	    

	
	  
	  
	  
    def signal_handler(self, signal, frame):
	self.printswitches()
	self.net_graph.printGraph()
	exit(0)
	  

	  
	  
def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Video Slicing module
    '''
    core.registerNew(VideoSlice)
