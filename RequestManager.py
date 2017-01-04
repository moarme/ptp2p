__author__ = 'moar'

class RequestManager(object):
    def generate_next_request(self):
        while True:
            #Ask the Requests Manager for new Blocks to request
            self.debug_mesg( 'generate_next_request','Start asking the Requests Manager for new Blocks to request...')
            piece_index,block_index = self.torrent.requester.get_next_block(self)
            #piece_index,block_index=(702,0)
            self.debug_mesg( 'generate_next_request','Next blocks are piece_index={0}, block_index={1}'.format(str(piece_index),str(block_index)))
            if block_index < 0 or len(self.set_of_blocks_requested) >= MAX_REQUEST_TO_PEER:
                if self.torrent.file_manager.StreamCompleted == True:
                    reactor.stop()
                   # print self.torrent.file_manager.pieces_status
                    self.debug_mesg( 'generate_next_request','Reactor stopped!',mes_status='FAIL')
                    return
                else:
                    self.debug_mesg( 'generate_next_request','block_index > 0 or len(self.set_of_blocks_requested) < MAX_REQUEST_TO_PEER')
                    break
            block_byte_offset = block_index*BLOCK_SIZE
            #Add this to the set of blocks requested.
            self.set_of_blocks_requested.add((piece_index,block_index))
            #print self.torrent.file_manager.no_of_pieces

            request_size=self.torrent.file_manager.last_piece_size if piece_index == self.torrent.file_manager.last_piece_index and block_index==self.torrent.file_manager.last_block_index else BLOCK_SIZE
            self.debug_mesg( "generate_next_request","Requesting the part (index={0},begin={1},length={2} from a peer {3}".format(str(piece_index),str(block_byte_offset),str(request_size),str(self.ip)),mes_status='FAIL')

            self.transport.write(str(MessageTemplates.Request(
                index = MessageTemplates.number_to_bytes(piece_index),
                begin = MessageTemplates.number_to_bytes(block_byte_offset),
                length = MessageTemplates.number_to_bytes(request_size))))
                #length = Messages.number_to_bytes(576))))
            self.torrent.requester.requestSuccessful(self, piece_index,block_index)
            #Add timeout for requests.
            self.debug_mesg( "generate_next_request","Sending Request For Piece :{0} to {1}".format(str(MessageTemplates.number_to_bytes(piece_index)),str(self.ip)))
            Logger.info("Sending Request For Piece :" + str(MessageTemplates.number_to_bytes(piece_index)) + " to " + str(self.ip))
            reactor.callLater(TIMEOUT,self.checkTimeout,piece_index,block_index)
            return

        # TODO: Think about answering requests
    def answer_request(self, piece_index, begin, length):
        data = ""
        remaining_length = length
        while(remaining_length>0):
            block_index = int(begin/BLOCK_SIZE)
            if(self.torrent.file_manager.blockExists(piece_index,block_index)):    #block_exists indicates if block is present
                if(remaining_length >= BLOCK_SIZE):
                    data = self.torrent.file_manager.readBlock(piece_index,block_index)[begin%BLOCK_SIZE:]    #readBlock returns the data block
                    begin = math.ceil(begin/BLOCK_SIZE)*ConstantsBLOCK_SIZE
                    remaining_length -= BLOCK_SIZE-begin%BLOCK_SIZE
                else:
                    data = self.torrent.file_manager.readBlock(piece_index,block_index)[begin%BLOCK_SIZE:remaining_length]
                    remaining_length = 0
                self.transport.write(str(MessageTemplates.Piece(
                index = MessageTemplates.number_to_bytes(piece_index),
                begin = MessageTemplates.number_to_bytes(begin),
                block = data)))    #send corresponding data block
                if(begin == self.torrent.file_manager.get_piece_length(piece_index)):    #get piece length for corresponding piece index
                    piece_index += 1
                    begin = 0

    def cancelRequestFor(self,piece_index,block_index):
        if((piece_index,block_index) in self.set_of_blocks_requested):
            self.set_of_blocks_requested.remove((piece_index,block_index))
        begin = block_index*BLOCK_SIZE
        piece_index = MessageTemplates.number_to_bytes(piece_index)
        begin = MessageTemplates.number_to_bytes(block_index)
        length = MessageTemplates.number_to_bytes(BLOCK_SIZE)
        self.transport.write(str(MessageTemplates.Cancel(index = piece_index, begin = begin, length = length)))

    def checkTimeout(self, piece_index, block_index): #1
        self.debug_mesg("checkTimeout","{2}:For piece_index={0}, block_index={1}".format(str(piece_index),str(block_index),str(self.ip)))
        #Called after the expected time of receiving a (piece,block).Checks the set of pending requests to determine if retransmission is needed or not.
        if (piece_index,block_index) in self.set_of_blocks_requested:
            self.torrent.requester.removeRequest(self,piece_index, block_index)