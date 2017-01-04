__author__ = 'moar'
import MessageTemplates,urllib,struct
from datetime import datetime

class MessageParser(object):

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
            print datetime.now().strftime('Parcer.{0}: %Y.%m.%d %H:%M:%S\t\t').format(afunc)\
                  +bcolors['UNDERLINE']+bcolors[mes_status]+str(dmessage)+bcolors['ENDC']

    def __init__(self,message):


    def parse_handshake(self, data=""):

    def parse_nonHandshakeMessage(self, data):
        bytestring = data
        if (bytestring[0:4] == '\x00\x00\x00\x00'):
            # Its a Keep Alive message #
            message_obj = MessageTemplates.KeepAlive(response=bytestring)
        else:
            self.debug_mesg( 'parse_nonHandshakeMessage','data[4]={0}\t{1}'.format(str(struct.unpack('!b',data[4])),{
              0: 'lambda: Messages.Choke(response=bytestring)',
              1: 'lambda: Messages.Unchoke(response=bytestring)',
              2: 'lambda: Messages.Interested(response=bytestring)',
              3: 'lambda: Messages.Interested(response=bytestring)',
              4: 'lambda: Messages.Have(response=bytestring)',
              5: 'lambda: Messages.Bitfield(response=bytestring)',
              6: 'lambda: Messages.Request(response=bytestring)',
              7: 'lambda: Messages.Piece(response=bytestring)',
              8: 'lambda: Messages.Cancel(response=bytestring)',
              9: 'lambda: Messages.Port(response=bytestring)',
            }[struct.unpack('!b',data[4])[0]]))
            message_obj  = {
              0: lambda: MessageTemplates.Choke(response=bytestring),
              1: lambda: MessageTemplates.Unchoke(response=bytestring),
              2: lambda: MessageTemplates.Interested(response=bytestring),
              3: lambda: MessageTemplates.Interested(response=bytestring),
              4: lambda: MessageTemplates.Have(response=bytestring),
              5: lambda: MessageTemplates.Bitfield(response=bytestring),
              6: lambda: MessageTemplates.Request(response=bytestring),
              7: lambda: MessageTemplates.Piece(response=bytestring),
              8: lambda: MessageTemplates.Cancel(response=bytestring),
              9: lambda: MessageTemplates.Port(response=bytestring),
            }[    struct.unpack('!b',data[4])[0]   ]()     # The 5th byte in 'data' is the message type/id
        self.process_message(message_obj)


class PeerMessageProcessor(object):
    def __init__(self):
        self.message_obj=message_obj
        self.processMessage()
        self.parser=MessageParser()
        self.peer_has_pieces = BitArray(torrent.file_manager.no_of_pieces)
        #?? self.set_of_blocks_received = set()

    def take_package(self):
        if(message[1:20].lower() == "bittorrent protocol"):
            self.debug_mesg( '__init__','Got Handshake Message')
            # The message is a Handshake Message
            self.parse_handshake(data)
        else:
            #self.debug_mesg( 'dataReceived','Core.BitTorrenter.dataReceived: The message is not a Handshake Message')
            self.parse_nonHandshakeMessage(data)


    def processMessageObj(self,message):
        fmt = 'Peer : {:16s} || {:35s}'
        if isinstance(self.message_obj, MessageTemplates.Choke):
            self.processChoke()
        elif isinstance(self.message_obj, MessageTemplates.Unchoke):
            self.processUnchoke()
        elif isinstance(self.message_obj, MessageTemplates.Interested):
            self.processInterested()
        elif isinstance(self.message_obj, MessageTemplates.NotInterested):  #Should be NotInterested
            self.processNotInterested()
        elif isinstance(self.message_obj, MessageTemplates.Have):
            self.processHave()
        elif isinstance(self.message_obj, MessageTemplates.Bitfield):
            self.processBitfield()
        elif isinstance(self.message_obj, MessageTemplates.Request):
            self.processRequest()
        #TODO: implement sending pieces/serving torrents
        elif isinstance(self.message_obj, MessageTemplates.Piece):
            self.processPiece()
        elif isinstance(self.message_obj, MessageTemplates.Cancel):
            pass

    def processHandshake(self):
        # If the Info Hash matches the torrent's info hash, add the peer to the successful handshake set
        handshake_response_data = MessageTemplates.Handshake(data)
        handshake_info_hash = handshake_response_data.info_hash
        if handshake_info_hash == urllib.unquote(self.torrent.payload['info_hash']):
            self.factory.peers_handshaken.add((self.ip, self.port))
            self.transport.write(str(MessageTemplates.Interested()))
            self.buffer += data[68:]

            # print "Sending my BitField Message"
            self.transport.write(str(MessageTemplates.Bitfield(bitfield=self.torrent.file_manager.pieces_status.tobytes())))
            # print "SENT"
        else :
            # TODO : What to do when the peer has given has invalid garbage Data
            self.killPeer()
        return


    def processChoke(self):
        Logger.info(fmt.format(str(self.ip) , "Choke"))
        self.choked = True

    def processUnchoke(self):
        Logger.info(fmt.format(str(self.ip) , "UnChoke"))
        self.choked = False

    def processInterested(self):
        Logger.info(fmt.format(str(self.ip) , "Interested"))
        self.peer_interested = True

    def processNotInterested(self):
        Logger.info(fmt.format(str(self.ip) , "Not Interested"))
        self.peer_interested = False

    def processHave(self):
        piece_index = MessageTemplates.bytes_to_number(message_obj.index)
        self.torrent.requester.havePiece(self,piece_index)
        self.debug_mesg( 'process_message',"{0} Has Piece Index : {1}".format(str(self.ip),str(piece_index)))
        Logger.info(fmt.format(str(self.ip) , "Has Piece Index :" + str(piece_index)))
        ret = self.torrent.file_manager.checkBounds(piece_index,0)
        if ret != 2:
            self.interested = True;
            self.transport.write(str(MessageTemplates.Unchoke()))
            self.peer_choked = False
        self.peer_has_pieces[piece_index] = 1

    def processBitfield(self):
            self.debug_mesg( 'process_message','Got bitfield from %s'%(str(self.ip)))
       #     Logger.info(str("Peer :") + str(self.ip) + " || " + "Bitfield")
            self.torrent.requester.haveBitfield(self,message_obj.bitfield)
            bitarray = BitArray(bytes=message_obj.bitfield)
            self.peer_has_pieces = bitarray[:len(self.peer_has_pieces)]
            flag = False
            for i in range(self.torrent.file_manager.start_piece_id,len(message_obj.bitfield)):
                ret = self.torrent.file_manager.checkBounds(i,0)
                if ret != 2:
                    if message_obj.bitfield[i] == True:
                        flag = True
                        break
                else:
                    break
            if flag == True:
                self.interested = True
                self.transport.write(str(MessageTemplates.Unchoke()))
                self.peer_choked = False
            # assert self.torrent.file_manager.no_of_pieces == len(message_obj.bitfield), str("Peer Has Pieces is not of same length as Message_obj.bitfield" + str(self.torrent.file_manager.no_of_pieces) + "|.|.|.|.|" +str(len(message_obj.bitfield)))

    def processRequest(self):
        Logger.info(fmt.format(str(self.ip) , "Request"))
        if self.peer_choked == False:
            answer_request(message_obj.index,message_obj.begin,message_obj.length)

    def processPiece(self):
        #self.pending_requests -= 1 TODO: pending_requests mechanism
        piece_index = MessageTemplates.bytes_to_number(message_obj.index)
        block_byte_offset = MessageTemplates.bytes_to_number(message_obj.begin)
        block_index = block_byte_offset/BLOCK_SIZE
        Logger.info(fmt.format(str(self.ip) , str(piece_index) + "," + str(block_index) + " :: Recevied Data Piece!!! !:D :D :D"))
        self.torrent.requester.updateTotalDataReceived(len(message_obj.block))
        if((piece_index,block_index) in self.set_of_blocks_requested):
            self.set_of_blocks_requested.remove((piece_index,block_index))
        self.set_of_blocks_received.add((piece_index,block_index))
        #Change the following line as per the function name used in FileManager.

        message_obj.index = MessageTemplates.bytes_to_number(message_obj.index)
        message_obj.begin = MessageTemplates.bytes_to_number(message_obj.begin)
        self.debug_mesg( 'process_message','isinstance(message_obj, MessageTemplates.Piece): from {0} piece={1}, block={2} Recevied Data Piece!!!'.format(str(self.ip),str(piece_index),str(block_index)),mes_status='FAIL')
       # print 'isinstance(message_obj, Messages.Piece): {0}, {1}, {2} Recevied Data Piece!!!'.format(str(self.ip),str(piece_index),str(block_index))
        received_data_hash = sha1(message_obj.block).digest()
        if received_data_hash=
        self.writeData(message_obj.index, message_obj.begin, message_obj.block)
        self.debug_mesg( 'process_message','isinstance(message_obj, MessageTemplates.Piece): Received || Total Current Requests: {0}'.format(str(self.torrent.requester.total_requests)))
        self.debug_mesg( 'process_message','isinstance(message_obj, MessageTemplates.Piece): Received || Wasted Requests:{0}'.format(str(self.torrent.requester.total_requests_wasted)))
        self.debug_mesg( 'process_message','isinstance(message_obj, MessageTemplates.Piece): Received || Cancelled Requests:{0}'.format(str(self.torrent.requester.total_requests_cancelled)))
        self.debug_mesg( 'process_message','isinstance(message_obj, MessageTemplates.Piece): Received || Requests Used:{0}'.format(str(self.torrent.requester.total_requests_used)))
        self.debug_mesg( 'process_message','isinstance(message_obj, MessageTemplates.Piece): Received || Total Requests Sent:{0}'.format(str(self.torrent.requester.total_requests_sent)))
        Logger.info("Received || Total Current Requests :" + str(self.torrent.requester.total_requests))
        Logger.info("Received || Wasted Requests:" + str(self.torrent.requester.total_requests_wasted))
        Logger.info("Received || Cancelled Requests:" + str(self.torrent.requester.total_requests_cancelled))
        Logger.info("Received || Requests Used:" + str(self.torrent.requester.total_requests_used))
        Logger.info("Received || Total Requests Sent:" + str(self.torrent.requester.total_requests_sent))

        # assert self.torrent.requester.total_requests_sent == self.torrent.requester.total_requests_wasted + self.torrent.requester.total_requests_cancelled + self.torrent.requester.total_requests_used, "Chutiyapa in count of requests wasted and Cancelled"

    def processCancel(self):
        Logger.info(fmt.format(str(self.ip) , "Cancelled Request :\\"))
    #def processPort(self):


class AnnouncerMessageProcessor(object):
    def __init__(self):
        super(AnnouncerMessageProcessor,self).__init__()

    def processMessage(self,packedMessage):
        pass

    def processNewTorrentAnnounce(self):
        pass

    def processPeerList(self):
        pass

    def processTorrentInfo(self):
        pass

    def processAnnouncerListUpdate(self):
        pass
