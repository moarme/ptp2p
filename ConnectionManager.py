__author__ = 'moar'

class ConnectionServant(object):
    def __init__(self, torrent):
        self.torrent             = torrent
        self.pending_requests     = 0
        self.interested         = False
        self.peer_interested     = False
        self.choked             = True
       #?? self.peer_choked         = True
        self.buffer = ""
        self.set_of_blocks_requested = set()



    def killPeer(self):
        if (self.ip, self.port) in self.factory.peers_found:
            self.factory.peers_handshaken.remove((self.ip, self.port))
        self.transport.loseConnection()

    def canSendRequest(self):
        self.debug_mesg( 'canSendRequest','interested={0}, choked={1}, pending_requests={2}'.format(str(self.interested),str(self.choked),str(self.pending_requests)))
        if self.interested and not self.choked and self.pending_requests<=5:
            return True
        return False