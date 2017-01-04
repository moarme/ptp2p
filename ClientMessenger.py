__author__ = 'moar'
from struct import pack,unpack_from
from urllib import unquote


class UDPMessagePacker(object):
    def udp_get_transaction_id(self):
        return int(random.randrange(0, 255))

    @staticmethod
    def udp_create_product_request(connection_id, payload):
            action = 0x1 #action (1 = announce)
            transaction_id = UDPMessagePacker.udp_get_transaction_id()
            buf = pack("!q", connection_id)                                     #first 8 bytes is connection id
    #        buf += pack("!i", action)                                         #next 4 bytes is action
            buf += pack("!i", transaction_id)                                 #followed by 4 byte transaction id
            buf += pack("!20s", unquote(payload['info_hash']))         #the info hash of the torrent we announce ourselves in
            buf += pack("!20s", unquote(payload['peer_id']))             #the peer_id we announce
            buf += pack("!q", int(unquote(payload['downloaded'])))     #number of bytes downloaded
            buf += pack("!q", int(unquote(payload['left'])))             #number of bytes left
            buf += pack("!q", int(unquote(payload['uploaded'])))         #number of bytes uploaded
            buf += pack("!i", 0x2)                                             #event 2 denotes start of downloading
            buf += pack("!i", 0x0)                                             #IP address set to 0. Response received to the sender of this packet
            key = UDPMessagePacker.udp_get_transaction_id()                                             #Unique key randomized by client
            buf += pack("!i", key)
    #        buf += pack("!i", TRACKER_PEER_COUNT)                             #Number of peers required. Set to -1 for default
            buf += pack("!i", int(unquote(payload['port'])))              #port on which response will be sent
    #        buf += pack("!i", int(s_port))                                  #port on which response will be sent
            return (buf, transaction_id)

    @staticmethod
    def udp_peer_list(connection_id,product_id,transaction_id=udp_get_transaction_id()):
        buf = pack("!q", connection_id) 					#first 8 bytes is connection id
        #key = UDPMessagePacker.udp_get_transaction_id()                                  #next 4 bytes is transaction id. Unique key randomized by client
        buf += pack("!i", transaction_id)
        buf+=  pack('!h',6)
        buf += pack("!i", product_id)
        return (buf, transaction_id)

    @staticmethod
    def udp_product_interested(connection_id,product_id):
        buf = pack("!q", connection_id) 					#first 8 bytes is connection id
        key = UDPMessagePacker.udp_get_transaction_id()                                  #next 4 bytes is transaction id. Unique key randomized by client
        buf += pack("!i", key)
        buf+=  pack('!h',2)
        buf += pack("!i", product_id)
        return (buf, key)

    @staticmethod
    def udp_create_connection_request(connection_id,info):
        buf = pack("!q", connection_id) 					#first 8 bytes is connection id
        key = UDPMessagePacker.udp_get_transaction_id()                                  #next 4 bytes is transaction id. Unique key randomized by client
        buf += pack("!i", key)
        buf += pack("!36s", info['client_id'])
        buf += pack("!5s",  info['client_version'])
        buf += pack("!20s", info['os_info'])
        return (buf, key)

class UDPMessageUnpacker(object):

    def unpack(self,data):
        self.data=data
        self.message['connection_id']=unpack_from("!q", self.data)[0]
        self.unpack_handshake()
        return self.message

    def unpack_handshake(self):
        self.message['transaction_id']=unpack_from('!i',self.data,8)[0]
        self.message['client_id']=unpack_from("!36s", self.data,12)[0]
        self.message['client_version']=unpack_from('!5s',self.data,48)[0]
        self.message['os_version']=unpack_from('!20s',self.data,53)[0]
    @staticmethod
    def udp_product_interested(self,connection_id,product_id):
        buf = pack("!q", connection_id) 					#first 8 bytes is connection id
        key = self.udp_get_transaction_id()                                  #next 4 bytes is transaction id. Unique key randomized by client
        buf += pack("!i", key)
        buf += pack("!i", product_id)
        return (buf, key)