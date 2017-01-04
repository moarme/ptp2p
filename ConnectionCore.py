from twisted.internet import reactor, protocol
from PeerCommunication import MessageTemplates,MessageParser,PeerProcessor
from Constants import *
import urllib
import logging as Logger
from bitstring import BitArray
from datetime import datetime
import struct

import time
from hashlib import sha1

class PeerConnectionCore(protocol.Protocol):
    DBG_MODE=G_DBG_MODE
    peerState={'weChoked':True,
               'heChoked':True,
               'received':0.0,
               'sent':0.0,
               'bitmap':}
  #  DBG_MODE=False
    def __init__(self, torrent):
        self.torrent             = torrent
        self.peerCommunicator=PeerProcessor()
        self.peerMessageProc=MessageProcessor()
        self.pending_requests     = 0
        self.interested         = False
        self.peer_interested     = False
        self.choked             = True
       # self.peer_choked         = True
        self.buffer = ""
        self.set_of_blocks_requested = set()
        self.peer_has_pieces = BitArray(torrent.file_manager.no_of_pieces)
        self.set_of_blocks_received = set()

    def debug_mesg(self,afunc,dmessage,mes_status='OKBLUE'):
        bcolors={
        'HEADER' : '\033[95m',
        'OKBLUE' : '\033[94m',
        'OKGREEN' : '\033[92m',
        'WARNING' : '\033[93m',
        'FAIL' : '\033[91m',
        'ENDC' : '\033[0m',
        'BOLD' : '\033[1m',
        'UNDERLINE' : '\033[4m'}
        if self.DBG_MODE or mes_status=='FAIL':
            print datetime.now().strftime('Core.BitTorrenter.{0}: %Y.%m.%d %H:%M:%S\t\t').format(afunc)\
                  +bcolors['UNDERLINE']+bcolors[mes_status]+str(dmessage)+bcolors['ENDC']

    def connectionMade(self):
        self.transport.write(self.torrent.handshake_message)
        self.factory             = self.transport.connector.factory
        self.ip                 = self.transport.connector.host
        self.port                 = self.transport.connector.port
        self.debug_mesg( 'connectionMade','Connection Made with {0}:{1}'.format(str(self.ip),str(self.port)),mes_status='FAIL')
        # Call Handshake Fuction

    def dataReceived(self, data):
        # Logger.info("Peer said:" + str(data)) 
        handshake_response_data = MessageTemplates.Handshake(data)
        handshake_info_hash = handshake_response_data.info_hash
        data = self.handleData(data)

        while(data != None):
            self.debug_mesg('dataReceived','data != None from {0} : {1}'.format(str(self.ip),str(self.port)))
            Parser.Parcer(data)
            if(self.canSendRequest()):
                self.debug_mesg( 'dataReceived','Core.BitTorrenter.dataReceived: canSendRequest = True')
                self.generate_next_request()    #Send Request for next block
            # Get Next Message in Queue
            if(self.torrent.file_manager.bytesWritten != 0):
                Logger.info("File Size Remaining: " + str((self.torrent.file_manager.file_to_stream_length - self.torrent.file_manager.bytesWritten)/1024) + " kilobytes")
                Logger.info("Efficiency: " + str((self.torrent.file_manager.bytesWritten*100)/self.torrent.requester.total_data_received) + "%")
                Logger.info("Speed: " + str(self.torrent.file_manager.bytesWritten/((time.time()-self.torrent.start_time)*1024)) + " kilobytes/second")
            data = self.handleData()

    # Handles the newly received Data. It appends the data to the buffer and returns the next message in Queue. The Returned message should be parsed based on its type
    def handleData(self, data = ""):
        self.buffer += data
        message = ""
        if(self.buffer[1:20].lower() == "bittorrent protocol"):
            message += self.buffer[:68]
            self.buffer = self.buffer[68:]
            return message
        message_length = MessageTemplates.bytes_to_number(self.buffer[:4]) + 4
        if(len(self.buffer) >= message_length):
            message = self.buffer[:message_length]
            self.buffer = self.buffer[message_length:]
            return message
        return None







    def writeData(self, piece_index, begin, data):
        if(begin%BLOCK_SIZE != 0):
            #The beginning of data is in the middle of a block. Discard this data since we are going to request data in blocks anyway
            data = data[((math.ceil(float(begin)/float(BLOCK_SIZE))*BLOCK_SIZE) - begin):]
            begin += (math.ceil(float(begin)/float(BLOCK_SIZE))*BLOCK_SIZE) - begin
        block_index = int(begin/BLOCK_SIZE)
        self.debug_mesg('writeData','Preparing for writing {0} piece {1} block beginning from {2}. Data len={3}'.format(str(piece_index),str(block_index),str(begin),str(len(data))),mes_status='FAIL')
        while(data != ""):
           # if(len(data) >= BLOCK_SIZE):
                if(self.torrent.file_manager.blockExists(piece_index,block_index) == True):
                    self.torrent.requester.total_requests_wasted += 1
                    self.torrent.requester.cancelRemainingRequests(piece_index,block_index)
                else:
                    self.torrent.file_manager.writeToFile(piece_index,block_index, data)
                    self.torrent.requester.total_requests_used += 1
                    self.torrent.requester.removeRequest(self,piece_index,block_index)
                    if(self.torrent.file_manager.blockExists(piece_index,block_index) == True):
                        self.torrent.requester.cancelRemainingRequests(piece_index,block_index)
                data = data[BLOCK_SIZE:]
                piece_index,block_index = self.torrent.file_manager.incrementPieceBlock(piece_index, block_index)
         #   else:
          #      break





# Each torrent has its own Factory. And only one factory
class BitTorrentFactory(protocol.ClientFactory):
    DBG_MODE=G_DBG_MODE
    #DBG_MODE=False
    def __init__(self, torrent):
        self.torrent = torrent
        self.peers_found = dict()
        self.peers_handshaken = set()

    def debug_mesg(self,afunc,dmessage,mes_status='OKBLUE'):
        bcolors={
        'HEADER' : '\033[95m',
        'OKBLUE' : '\033[94m',
        'OKGREEN' : '\033[92m',
        'WARNING' : '\033[93m',
        'FAIL' : '\033[91m',
        'ENDC' : '\033[0m',
        'BOLD' : '\033[1m',
        'UNDERLINE' : '\033[4m'}
        if self.DBG_MODE:
            print datetime.now().strftime('Core.BitTorrenter.{0}: %Y.%m.%d %H:%M:%S\t\t').format(afunc)\
                  +bcolors['UNDERLINE']+bcolors[mes_status]+str(dmessage)+bcolors['ENDC']

    def numberOfConnectedPeers(self):
        return len(self.connected_peers)
    # To check if there is already a discovered peer  with the Peer having ip : peer_ip and port : peer_port
    def has_peer(self, peer_ip, peer_port):
        if (peer_ip, peer_port) in self.peers_found:
            return True
        return False

    # To check if there is an ongoing connection with the Peer having ip : peer_ip and port : peer_port
    def is_connected_peer(self, peer_ip, peer_port):
        if (peer_ip, peer_port) in self.connected_peers:
            return True
        return False
    def buildProtocol(self, addr):
        peer = BitTorrenter(self.torrent) # Protocol is named as 'peer'
        self.debug_mesg('buildProtocol','addr={0}'.format(str(addr)))

        # Add The peer to the set of discovered Peers
        # Make Sure the Peers for which the Protocol is being built, is not already added
        # This Check needs to be done before the reactor.connectToTCP() is called
        self.peers_found[(addr.host, addr.port)] = peer
        return peer
    def clientConnectionFailed(self, connector, reason): 
        Logger.info(str("Connection failed REASON :" + str(reason)))

        # reactor.stop()
    def clientConnectionLost(self, connector, reason): 
        Logger.info("Connection lost.")
