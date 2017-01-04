# Malay Keshav, Rahul Upadhyaya and Khushal Sagar

import binascii, urllib, socket, random, struct
from bcode import bdecode
from urlparse import urlparse, urlunsplit
import logging as Logger
from Constants import *
from time import sleep

from twisted.internet.protocol import DatagramProtocol

#class UDPTools(object):
def udp_get_transaction_id():
    return int(random.randrange(0, 255))

def udp_create_announce_request(connection_id, payload, s_port):
        action = 0x1 #action (1 = announce)
        transaction_id = udp_get_transaction_id()
        buf = struct.pack("!q", connection_id)                                     #first 8 bytes is connection id
#        buf += struct.pack("!i", action)                                         #next 4 bytes is action
        buf += struct.pack("!i", transaction_id)                                 #followed by 4 byte transaction id
        buf += struct.pack("!20s", urllib.unquote(payload['info_hash']))         #the info hash of the torrent we announce ourselves in
        buf += struct.pack("!20s", urllib.unquote(payload['peer_id']))             #the peer_id we announce
        buf += struct.pack("!q", int(urllib.unquote(payload['downloaded'])))     #number of bytes downloaded
        buf += struct.pack("!q", int(urllib.unquote(payload['left'])))             #number of bytes left
        buf += struct.pack("!q", int(urllib.unquote(payload['uploaded'])))         #number of bytes uploaded
        buf += struct.pack("!i", 0x2)                                             #event 2 denotes start of downloading
        buf += struct.pack("!i", 0x0)                                             #IP address set to 0. Response received to the sender of this packet
        key = udp_get_transaction_id()                                             #Unique key randomized by client
        buf += struct.pack("!i", key)
    #    buf += struct.pack("!i", TRACKER_PEER_COUNT)                             #Number of peers required. Set to -1 for default
        buf += struct.pack("!i", int(urllib.unquote(payload['port'])))              #port on which response will be sent
        # buf += struct.pack("!i", int(s_port))                                  #port on which response will be sent
        return (buf, transaction_id)



def udp_create_connection_request(connection_id,info):
    buf = struct.pack("!q", connection_id) 					#first 8 bytes is connection id
    key = udp_get_transaction_id()                                  #next 4 bytes is transaction id. Unique key randomized by client
    buf += struct.pack("!i", key)
    buf += struct.pack("!36s", info['client_id'])
    buf += struct.pack("!5s", info['client_version'])
    buf += struct.pack("!20s", info['os_info'])
    return (buf, key)


class UDPAnnouncerProtocol(DatagramProtocol):
    def __init__(self, tracker,clientInfo):
        self.tracker = tracker
        self.clientInfo=clientInfo
        self.connection_id = 0x89037900291
        # Teporarly Change udp:// to http:// to get hostname and portnumbe
        #url = parsed.geturl()[3:]           ##??
        #url = "http" + url
        #try:
        #    self.host         = socket.gethostbyname(urlparse(url).hostname)
        #except Exception, e:
        #    self.host         = '127.0.0.1'
        #    self.stopProtocol()
        #self.port         = urlparse(url).port
        #self.torrent     = torrent
        self.isConnected= False
        #if self.host != 'localhost':
        #    self.torrent.trackerObjects.append(self)


    def startProtocol(self):
        host = self.tracker[0]
        port = self.tracker[1]
        self.transport.connect(host, port)
        self.connection_request=udp_create_connection_request(self.connection_id,self.clientInfo)
       # udp_create_announce_request()
        print(("now we can only send to host %s port %d" % (host, port)))
        self.transport.write(self.connection_request[0])  # no need for address
        #sleep(5)
        #self.transport.write(self.connect_transaction[0])  # no need for address

    def datagramReceived(self, data, addr):
        print("received %r from %s" % (data, addr))
        #self.transport.write(data)
        self.isConnected= True

    def stopProtocol(self):
        print("Protocol stopped")

    # Possibly invoked if there is no server listening on the
    # address to which we are sending.
    def connectionRefused(self):
        print("No one listening")
        self.isConnected= False

    def announcerHandshake(self):
        pass

    def checkTorrentInfo(self):
        pass

    def keepMeAlive(self):
        pass





'''
    def startProtocol(self):
       # Called when transport is connected
       self.transport.connect(self.host, self.port)
       Logger.info("Connecting To Tracker :" + self.tracker)
       self.startConnect()

    def startConnect(self):
        req, self.transaction_id = udp_create_connection_request()
        self.transport.write(req)

    def stopProtocol(self):
        try:
            Logger.info("Connection To Tracker Lost :" + str(self.host))
        except:
            pass

    def sendTrackerAnnounceRequest(self):
        if self.isConnected == True:
            req, self.transaction_id = udp_create_announce_request(self.connection_id, self.torrent.updatePayload(), self.port)
            self.transport.write(req)
        else :
            self.startConnect()

    def datagramReceived(self, datagram, host):
        if self.isConnected == False:
            self.connection_id = udp_parse_connection_response(datagram, self.transaction_id)
            self.isConnected = True
            self.sendTrackerAnnounceRequest()
        else:
            trackerResponse, peers = udp_parse_announce_response(datagram, self.transaction_id)
            interval = int(trackerResponse['interval'])
            Logger.info(str(trackerResponse))
            Logger.info("Updating Peer List From Tracker :" + self.tracker)
            self.torrent.updatePeers(self.tracker, peers)
            refreshID = self.torrent.reactor.callLater(interval, self.sendTrackerAnnounceRequest)
            self.torrent.refreshTracker.append(refreshID)

def udp_create_announce_request(connection_id, payload, s_port):
    action = 0x1 #action (1 = announce)
    transaction_id = udp_get_transaction_id()
    buf = struct.pack("!q", connection_id)                                     #first 8 bytes is connection id
    buf += struct.pack("!i", action)                                         #next 4 bytes is action 
    buf += struct.pack("!i", transaction_id)                                 #followed by 4 byte transaction id
    buf += struct.pack("!20s", urllib.unquote(payload['info_hash']))         #the info hash of the torrent we announce ourselves in
    buf += struct.pack("!20s", urllib.unquote(payload['peer_id']))             #the peer_id we announce
    buf += struct.pack("!q", int(urllib.unquote(payload['downloaded'])))     #number of bytes downloaded
    buf += struct.pack("!q", int(urllib.unquote(payload['left'])))             #number of bytes left
    buf += struct.pack("!q", int(urllib.unquote(payload['uploaded'])))         #number of bytes uploaded
    buf += struct.pack("!i", 0x2)                                             #event 2 denotes start of downloading
    buf += struct.pack("!i", 0x0)                                             #IP address set to 0. Response received to the sender of this packet
    key = udp_get_transaction_id()                                             #Unique key randomized by client
    buf += struct.pack("!i", key)
    buf += struct.pack("!i", TRACKER_PEER_COUNT)                             #Number of peers required. Set to -1 for default
    buf += struct.pack("!i", int(urllib.unquote(payload['port'])))              #port on which response will be sent
    # buf += struct.pack("!i", int(s_port))                                  #port on which response will be sent
    return (buf, transaction_id)

def udp_parse_announce_response(buf, sent_transaction_id):
    if len(buf) < 20:
        Logger.error(("Wrong response length while announcing: %s" % len(buf)))
        raise RuntimeError("Wrong response length while announcing: %s" % len(buf))    
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action
    res_transaction_id = struct.unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id    
    if res_transaction_id != sent_transaction_id:
        Logger.error("Transaction ID Did not Match for " + self.tracker + " Expected :" + str(sent_transaction_id) + " Received :" + str(res_transaction_id))
        return {'interval':0, 'leeches':0, 'seeds':0}, list()
    Logger.info("Parsing Response from Tracekr")
    if action == 0x1:
        ret = dict()
        offset = 8; 
        #next 4 bytes after action is transaction_id, so data doesnt start till byte 8        
        ret['interval'] = struct.unpack_from("!i", buf, offset)[0]
        offset += 4
        ret['leeches'] = struct.unpack_from("!i", buf, offset)[0]
        offset += 4
        ret['seeds'] = struct.unpack_from("!i", buf, offset)[0]
        offset += 4
        Logger.debug(str("Seeds:"+str(ret['seeds']) + " || Leeches:"+str(ret['leeches']) + "|| Interval:"+str(ret['interval'])))
        peers = list()
        x = 0
        while offset != len(buf):
            peers.append(dict())
            peers[x]['IP'] = struct.unpack_from("!i",buf,offset)[0]
            offset += 4
            if offset >= len(buf):
                raise RuntimeError("Error while reading peer port")
            peers[x]['port'] = struct.unpack_from("!H",buf,offset)[0]
            offset += 2
            x += 1
        return ret,peers
    else:
        #an error occured, try and extract the error string
        error = struct.unpack_from("!s", buf, 8)
        Logger.warn(("Action="+str(action)))
        raise RuntimeError("Error while annoucing: %s" % error)

def udp_create_connection_request():
    connection_id = 0x41727101980                             #default connection id
    action = 0x0                                             #action (0 = give me a new connection id)    
    transaction_id = udp_get_transaction_id()
    buf = struct.pack("!q", connection_id)                     #first 8 bytes is connection id
    buf += struct.pack("!i", action)                         #next 4 bytes is action
    buf += struct.pack("!i", transaction_id)                 #next 4 bytes is transaction id
    return (buf, transaction_id)

def udp_parse_connection_response(buf, sent_transaction_id):
    if len(buf) < 16:
        raise RuntimeError("Wrong response length getting connection id: %s" % len(buf))            
    action = struct.unpack_from("!i", buf)[0]                 #first 4 bytes is action

    res_transaction_id = struct.unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        raise RuntimeError("Transaction ID doesnt match in connection response! Expected %s, got %s"
            % (sent_transaction_id, res_transaction_id))

    if action == 0x0:
        connection_id = struct.unpack_from("!q", buf, 8)[0] #unpack 8 bytes from byte 8, should be the connection_id
        return connection_id
    elif action == 0x3:        
        error = struct.unpack_from("!s", buf, 8)
        raise RuntimeError("Error while trying to get a connection response: %s" % error)
    pass


'''