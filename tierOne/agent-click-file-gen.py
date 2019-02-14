#!/usr/bin/python

# This script creates a .cli file which can then be run using the Click modular router.
# http://read.cs.ucla.edu/click/click
# https://github.com/kohler/click
#
# it requires that you have installed the odinagent.cc module within your Click installation
# https://github.com/Wi5/odin-wi5-agent/tree/master/src
#
# it also requires that you have patched the ath9k driver.
# About the driver patch see:
# https://github.com/Wi5/odin-wi5/tree/master/odin-patch-driver-ath9k

import sys

if (len(sys.argv) != 22):
    print 'Usage:'
    print ''
    print '%s <AP_CHANNEL> <QUEUE_SIZE_IN> <QUEUE_SIZE_OUT> <MAC_ADDR_AP> <ODIN_MASTER_IP> <ODIN_MASTER_PORT> <DEBUGFS_FILE> <SSIDAGENT> <ODIN_AGENT_IP> <DEBUG_CLICK> <DEBUG_ODIN> <TX_RATE> <TX_POWER> <HIDDEN> <MULTICHANNEL_AGENTS> <DEFAULT_BEACON_INTERVAL> <BURST_BEACON_INTERVAL> <MEASUREMENT_BEACON_INTERVAL>' %(sys.argv[0])
    print ''
    print 'AP_CHANNEL: it must be the same where mon0 of the AP is placed. To avoid problems at init time, it MUST be the same channel specified in the /etc/config/wireless file of the AP'
    print 'QUEUE_SIZE_IN: you can use the size 500'
    print 'QUEUE_SIZE_OUT: you can use the size 500'
    print 'MAC_ADDR_AP: the MAC of the wireless interface mon0 of the AP. e.g. 60:E3:27:4F:C7:E1'
    print 'ODIN_MASTER_IP is the IP of the openflow controller where Odin master is running'
    print 'ODIN_MASTER_PORT should be 2819 by default'
    print 'DEBUGFS_FILE is the path of the bssid_extra file created by the ath9k patch'	
    print '             it can be /sys/kernel/debug/ieee80211/phy0/ath9k/bssid_extra'
    print 'SSIDAGENT is the name of the SSID of this Odin agent'
    print 'ODIN_AGENT_IP is the IP address of the AP where this script is running (the control plane ethernet IP, used for communicating with the controller)'
    print 'DEBUG_CLICK: "0" no info displayed; "1" only basic info displayed; "2" all the info displayed'
    print 'DEBUG_ODIN: "00" no info displayed; "01" only basic info displayed; "02" all the info displayed; "11" or "12": demo mode (more separators)'
    print 'TX_RATE: it is an integer, and the rate is obtained by its product with 500kbps. e.g. if it is 108, this means 108*500kbps = 54Mbps'
    print '         we are not able to send packets at different rates, so a single rate has to be specified'
    print 'TX_POWER: (in dBm). This is the power level of the main interface of the AP'
    print '          The value you put here does NOT modify the power level of the AP'
    print '          It just informs Odin Click module of the TX power value you have in the AP'
    print '          The AP will send this value to the controller as a part of the statistics'
    print '          For getting the value, use e.g. $# iw dev mon0 info, and put it here'
    print 'HIDDEN: If HIDDEN is 1, then the AP will only send responses to the active scans targetted to the SSID of Odin'
    print '        If HIDDEN is 0, then the AP will also send responses to active scans with an empty SSID'
    print 'MULTICHANNEL_AGENTS: If MULTICHANNEL_AGENTS is 1, it means that the APs can be in different channels'
    print '                     If MULTICHANNEL_AGENTS is 0, it means that all the APs are in the same channel'
    print 'DEFAULT_BEACON_INTERVAL: Time between beacons (in milliseconds). Recommended values: 20-100'
    print 'BURST_BEACON_INTERVAL: Time between beacons when a burst of CSAs is sent after a handoff (in milliseconds). Recommended values: 5-10'
    print 'BURST: Number of beacons to send after add_lvap and channel_assigment. Recommended values: 5-40'
    print 'MEASUREMENT_BEACON_INTERVAL: Time between measurement beacons (in milliseconds). Used for measuring the distance in dBs between APs. Recommended values: 20-100'
    print 'CAPTURE_MODE: If CAPTURE_MODE is 1, two files will be generated, one for each interface, storing radiotap statistics'
    print '              If CAPTURE_MODE is 0, no statistic is storaged'
    print 'MAC_CAPTURE: the MAC of the wireless interface in STA that will be monitorized. e.g. 60:E3:27:4F:C7:AA'
    print '              For capture all traffic: FF:FF:FF:FF:FF:FF'
    print ''
    print 'Example:'
    print '$ python %s 9 500 500 60:E3:27:4F:C7:E1 192.168.1.129 2819 /sys/kernel/debug/ieee80211/phy0/ath9k/bssid_extra wi5-demo 192.168.1.9 0 01 108 25 0 1 100 10 100 0 FF:FF:FF:FF:FF:FF > agent.cli' %(sys.argv[0])
    print ''
    print 'and then run the .cli file you have generated'
    print 'click$ ./bin/click agent.cli'
    sys.exit(0)

# Read the arguments
AP_CHANNEL = sys.argv[1]
QUEUE_SIZE_IN = sys.argv[2]
QUEUE_SIZE_OUT = sys.argv[3]
AP_UNIQUE_BSSID = sys.argv[4]		    # FIXME. It seems it does not matter. Remove this parameter?
ODIN_MASTER_IP = sys.argv[5]
ODIN_MASTER_PORT = sys.argv[6]
DEBUGFS_FILE = sys.argv[7]
SSIDAGENT = sys.argv[8]
DEFAULT_GW = sys.argv[9]
AP_UNIQUE_IP = sys.argv[9]		      # FIXME. It seems this parameter does not matter. Remove this line?
DEBUG_CLICK = int(sys.argv[10])
DEBUG_ODIN = int(sys.argv[11])
TX_RATE = int(sys.argv[12])
TX_POWER = int(sys.argv[13])
HIDDEN = int(sys.argv[14])
MULTICHANNEL_AGENTS = int(sys.argv[15])
DEFAULT_BEACON_INTERVAL = int(sys.argv[16])
BURST_BEACON_INTERVAL = int(sys.argv[17])
BURST = int(sys.argv[18])
MEASUREMENT_BEACON_INTERVAL = int(sys.argv[19])
CAPTURE_MODE = int(sys.argv[20])
MAC_CAPTURE = sys.argv[21]
  
# Set the value of some constants
NETWORK_INTERFACE_NAMES = "mon"		 # beginning of the network interface names in monitor mode. e.g. mon
TAP_INTERFACE_NAME = "ap"		       # name of the TAP device that Click will create in the Access Point
STA_IP = "192.168.1.11"			       # IP address of the STA in the LVAP tuple. It is only necessary for a single client without DHCP
STA_MAC = "74:F0:6D:20:D4:74"		   # MAC address of the STA in the LVAP tuple. It is only necessary for a single client without DHCP

print '''
// This is the scheme:
//
//            TAP interface 'ap' in the machine that runs Click
//                   | ^
// from host         | |      to host
//                   v |
//             --------------
//            |    click     |
//             --------------
//             | ^        | ^
// to device   | |        | | to device 
//             V |        V |
//            'mon0'     'mon1'    interfaces in the machine that runs Click. They must be in monitor mode
//'''

print '''
// call OdinAgent::configure to create and configure an Odin agent:
odinagent::OdinAgent(HWADDR %s, RT rates, CHANNEL %s, DEFAULT_GW %s, DEBUGFS %s, SSIDAGENT %s, DEBUG_ODIN %s, TX_RATE %s, TX_POWER %s, HIDDEN %s, MULTICHANNEL_AGENTS %s, DEFAULT_BEACON_INTERVAL %s, BURST_BEACON_INTERVAL %s, BURST %s, MEASUREMENT_BEACON_INTERVAL %s, CAPTURE_MODE %s, MAC_CAPTURE %s)
''' % (AP_UNIQUE_BSSID, AP_CHANNEL, DEFAULT_GW, DEBUGFS_FILE, SSIDAGENT, DEBUG_ODIN, TX_RATE, TX_POWER, HIDDEN, MULTICHANNEL_AGENTS, DEFAULT_BEACON_INTERVAL, BURST_BEACON_INTERVAL,BURST, MEASUREMENT_BEACON_INTERVAL, CAPTURE_MODE, MAC_CAPTURE)

print '''// send a ping to odinsocket every 2 seconds
TimedSource(2, "ping\n")->  odinsocket::Socket(UDP, %s, %s, CLIENT true)
''' % (ODIN_MASTER_IP, ODIN_MASTER_PORT)

# Create ControlSocket and ChatterSocket, which are Click's remote control elements.
#http://piotrjurkiewicz.pl/files/bsc-dissertation.pdf
#
# Controlsocket: Communication with the Click application at user level is provided by a 
#TCP/IP based protocol. The user declares it in a configuration file, just like any 
#other element. However, ControlSocket does not process packets itself, so it is not 
#connected with other elements. 
# ControlSocket opens a socket and starts listening for connections.
#When a connection is opened, the server responds by stating its protocol version
#number. After that client can send commands to the Click router. The "server"
#(that is, the ControlSocket element) speaks a relatively simple line-based protocol.
#Commands sent to the server are single lines of text; they consist of words separated
#by spaces
#
# ChatterSocket opens a chatter socket that allows clients to receive copies 
#of router chatter traffic. The "server" (that is, the ChatterSocket element) 
#simply echoes any messages generated by the router configuration to any 
#existing clients.
print '''// output 3 of odinagent goes to odinsocket
odinagent[3] -> odinsocket
rates :: AvailableRates(DEFAULT 12 18 24 36 48 72 96 108);	// wifi rates in multiples of 500kbps. This will be announced in the beacons sent by the AP
control :: ControlSocket("TCP", 6777);
chatter :: ChatterSocket("TCP", 6778);
'''

print '''
// ----------------Packets going down (AP to STA)
// I don't want the ARP requests from the AP to the stations to go to the network device
//so click is in the middle and answers the ARP to the host on behalf of the station
//'ap' is a Linux tap device which is instantiated by Click in the machine.
//FromHost reads packets from 'ap'
// The arp responder configuration here doesnt matter, odinagent.cc sets it according to clients
FromHost(%s, HEADROOM 50)
  -> fhcl :: Classifier(12/0806 20/0001, -)
				// 12 means the 12th byte of the eth frame (i.e. ethertype)
				// 0806 is the ARP ethertype, http://en.wikipedia.org/wiki/EtherType
				// 20 means the 20th byte of the eth frame, i.e. the 6th byte of the ARP packet: 
				// "Operation". It specifies the operation the sender is performing: 1 for request, 2 for reply.''' % (TAP_INTERFACE_NAME)

if (DEBUG_CLICK > 0):
    print '''  -> ARPPrint("[Click] ARP request from host to resolve STA's ARP")'''

print '''  -> fh_arpr :: ARPResponder(%s %s) 	// looking for an STA's ARP: Resolve STA's ARP''' % (STA_IP, STA_MAC)

if (DEBUG_CLICK > 0):
    print '''  -> ARPPrint("[Click] Resolving client's ARP by myself")'''

print '''  -> ToHost(%s)''' % (TAP_INTERFACE_NAME)

print '''
// Anything from host that is not an ARP request goes to the input 1 of Odin Agent
fhcl[1]'''

if (DEBUG_CLICK > 1):
    print '''  -> Print("[Click] Non-ARP request from host goes to Odin agent port 1")'''

print '''  -> [1]odinagent
'''

print '''// Not looking for an STA's ARP? Then let it pass.
fh_arpr[1]'''

if (DEBUG_CLICK > 0):
    print '''  -> Print("[Click] ARP request to another STA goes to Odin agent port 1")'''

print '''  -> [1]odinagent'''

print '''
// create a queue 'q' for transmission of packets by the primary interface (mon0) and connect it to SetTXRate-RadiotapEncap
q :: Queue(%s)
  -> SetTXRate (%s)	// e.g. if it is 108, this means 54Mbps=108*500kbps
  -> RadiotapEncap()
  -> to_dev :: ToDevice (%s0);
''' % (QUEUE_SIZE_OUT, TX_RATE, NETWORK_INTERFACE_NAMES )


print '''  odinagent[2]
  -> q'''



print '''
// create a queue 'q2' for transmission of packets by the secondary interface (mon1) and connect it to SetTXRate-RadiotapEncap
q2 :: Queue(%s)
  -> SetTXRate (%s)	// e.g. if it is 108, this means 54Mbps=108*500kbps
  -> RadiotapEncap()
  -> to_dev2 :: ToDevice (%s1);
''' % (QUEUE_SIZE_OUT, TX_RATE, NETWORK_INTERFACE_NAMES )

print '''
odinagent[4]
  -> q2'''


print '''
// ----------------Packets coming up (from the STA to the AP) go to the input 0 of the Odin Agent
from_dev :: FromDevice(%s0, HEADROOM %s)
  -> RadiotapDecap()
  -> ExtraDecap()
  -> phyerr_filter :: FilterPhyErr()
  -> tx_filter :: FilterTX()
  -> dupe :: WifiDupeFilter()	// Filters out duplicate 802.11 packets based on their sequence number
								// click/elements/wifi/wifidupefilter.hh
  -> [0]odinagent''' % ( NETWORK_INTERFACE_NAMES, QUEUE_SIZE_IN )

print '''
// ----------------Packets coming up (from the STA to the AP) go to the input 0 of the Odin Agent
from_dev1 :: FromDevice(%s1, HEADROOM %s)
  -> RadiotapDecap()
  -> ExtraDecap()
  -> phyerr_filter1 :: FilterPhyErr()
  -> tx_filter1 :: FilterTX()
  -> dupe1 :: WifiDupeFilter()	// Filters out duplicate 802.11 packets based on their sequence number
								// click/elements/wifi/wifidupefilter.hh
  -> [2]odinagent''' % ( NETWORK_INTERFACE_NAMES, QUEUE_SIZE_IN )

print '''odinagent[0]
  -> q''' 

print '''
// Data frames
// The arp responder configuration here does not matter, odinagent.cc sets it according to clients
odinagent[1]
  -> decap :: WifiDecap()	// Turns 802.11 packets into ethernet packets. click/elements/wifi/wifidecap.hh
  -> RXStats				// Track RSSI for each ethernet source.
							// Accumulate RSSI, noise for each ethernet source you hear a packet from.
							// click/elements/wifi/rxstats.hh
  -> arp_c :: Classifier(12/0806 20/0001, -)
				// 12 means the 12th byte of the eth frame (i.e. ethertype)
				// 0806 is the ARP ethertype, http://en.wikipedia.org/wiki/EtherType
				// 20 means the 20th byte of the eth frame, i.e. the 6th byte of the ARP packet: 
				// "Operation". It specifies the operation the sender is performing: 1 for request'''

if (DEBUG_CLICK > 0):
    print '''  -> Print("[Click] ARP request from the STA") //debug level 1''' 

print '''  -> arp_resp::ARPResponder (%s %s) // ARP fast path for STA
									// the STA is asking for the MAC address of the AP
									// add the IP of the AP and the BSSID of the LVAP corresponding to this STA''' % ( AP_UNIQUE_IP, AP_UNIQUE_BSSID )

if (DEBUG_CLICK > 0):
    print '''  -> Print("[Click] ARP fast path for STA: the STA is asking for the MAC address of the AP")'''

print '''  -> [1]odinagent''' 
# it seems that AP_UNIQUE_IP and AP_UNIQUE_BSSID do not matter

print '''
// Non ARP packets. Re-write MAC address to
// reflect datapath or learning switch will drop it
arp_c[1]'''

if (DEBUG_CLICK > 1):
    print '''  -> Print("[Click] Non-ARP packet in arp_c classifier")''' 

print '''  -> ToHost(%s)''' % ( TAP_INTERFACE_NAME )

print '''
// Click is receiving an ARP request from a STA different from its own STAs
// I have to forward the ARP request to the host without modification
// ARP Fast path fail. Re-write MAC address (without modification)
// to reflect datapath or learning switch will drop it
arp_resp[1]'''

if (DEBUG_CLICK > 0):
    print '''  -> Print("[Click] ARP Fast path fail")''' 

print '''  -> ToHost(%s)''' % ( TAP_INTERFACE_NAME )
