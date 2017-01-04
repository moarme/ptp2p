import logging as Logger
import math
from bitstring import BitArray
import logging as Logger
from Constants import *
from datetime import datetime


class FileManager(object):
    """
    Class to manage all the blocks and pieces and other Helper Functions
    Also to read and write from the File.
    """
    DBG_MODE=G_DBG_MODE
    DBG_MODE=False


    def __init__(self, info):
        Logger.debug("Initializing File Manager")
        self.initPiecesBlocks(info)
        self.files_list = list()
        self.hashes=[i for i in info['pieces'][::20]]
        print 'len(self.hashes)',len(self.hashes)
        self.setMarkersForFileToDownload(info)
        self.initFile()
        Logger.debug("Initializing File Manager Complete")
        self.StreamCompleted = False
        self.bytesWritten = 0

    def debug_mesg(self,afunc,dmessage,mes_status='WARNING'):
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
            print datetime.now().strftime('FileManager.FileManager.{0}: %Y.%m.%d %H:%M:%S\t\t').format(afunc)\
                  +bcolors['ENDC']+bcolors[mes_status]+str(dmessage)+bcolors['ENDC']

    def initFile(self):
        file_name = self.file_to_stream['name']
        fout = open(file_name, "wb")
        data = BitArray(int(self.file_to_stream_length)*8)
       # print data
        data = data.tobytes()
        fout.write(data)
        fout.close()

    def initPiecesBlocks(self, info):
        Logger.debug("Initializing properties")
        self.piece_length     = info['piece length']
        self.total_length     = self.real_total_length = self.getTotalLength(info)
        self.no_of_blocks     = int(math.ceil(float(self.piece_length)/float(BLOCK_SIZE)))
        self.no_of_pieces     = int(math.ceil(float(self.total_length)/float(self.piece_length)))
        self.pieces_status    = BitArray(self.no_of_pieces)
        self.debug_mesg( 'initPiecesBlocks','total_length='+str(self.total_length))
        self.debug_mesg( 'initPiecesBlocks','no_of_blocks='+str(self.no_of_blocks))
        self.debug_mesg( 'initPiecesBlocks','no_of_pieces='+str(self.no_of_pieces))
        self.debug_mesg( 'initPiecesBlocks','pieces_status='+str(self.pieces_status))
        self.block_status     = list()
        self.block_data       = list()

        for x in xrange(self.no_of_pieces-1):
            ll = list()
            for y in xrange(self.no_of_blocks):
                ll.append(dict())
            self.block_data.append(ll)
            self.block_status.append(BitArray(self.no_of_blocks))
        self.last_piece_size = self.total_length - self.piece_length*(self.no_of_pieces-1)
        print 'self.total_length=',self.total_length,self.piece_length,'*',(self.no_of_pieces-1),'=',self.piece_length*(self.no_of_pieces-1)
        print 'self.last_piece_size',self.last_piece_size
        blocks_in_last_piece=int(math.ceil(float(self.last_piece_size)/float(BLOCK_SIZE)) )
        print 'blocks_in_last_piece=',blocks_in_last_piece
        ll = list()
        for x in xrange(blocks_in_last_piece):
            ll.append(dict())
        self.block_data.append(ll)
        self.block_status.append(BitArray(blocks_in_last_piece))
        self.last_piece_index=self.no_of_pieces-1
        self.last_block_index=blocks_in_last_piece-1
        #for i,b in enumerate(self.block_status):
        #    print i,b



        # Logger.info("My Bitfield :" + str(Messages.Bitfield(bitfield=self.torrent.pieces_status)))

    def getTotalLength(self, info):
        if('files' in info):
            listofFiles = info['files']
            total = 0
            for files in listofFiles:
                total += files['length']
            return total
        else:
            return info['length']

    # Sets the Starting And Ending Point of the File to Stream. 
    # The Function Sets the start_piece_id and start_block_offset for the file in the start_piece_id
    # Also stores the byte offset inside the block in start_byte_offset
    # Also stores the length of the File to Stream in file_to_stream_length in bytes
    def setMarkersForFileToDownload(self, info):
        Logger.debug("Setting Markers For File to be Downloaded in the Global Byte Array Data")
        if('files' in info):
            Logger.debug("Torrent has Multiple Files")
            # If Multiple Files
            x = 1
            #TODO: Maybe this part needs to be remastered. Too many loops I suppose
            for file_ in info['files']:
                path = ""
                for p in file_['path']:
                    path += p
                self.debug_mesg('setMarkersForFileToDownload','{0}:\t{1}\t{2}'.format(str(x),str(file_['length']),str(path)))
                x += 1
            print  "setMarkersForFileToDownload:Enter ID for File To Stream :"
            choice = int(input())
            byteOffset = 0
            x = 1
            for file_ in info['files']:
                if x >= choice:
                    self.file_to_stream = file_
                    p = ""
                    for p in file_['path']:
                        path = p
                    self.file_to_stream['name'] = path
                    break
                byteOffset += file_['length']
                x += 1
                self.debug_mesg( 'setMarkersForFileToDownload','byteOffset '+str(byteOffset))
            #TODO: === End of part ===

            self.debug_mesg( 'setMarkersForFileToDownload','self.piece_length'+str(self.piece_length))
            self.debug_mesg( 'setMarkersForFileToDownload','byteOffset%self.piece_length='+str(byteOffset%self.piece_length))
            self.real_start_absolute_byte_offset     = self.start_absolute_byte_offset     = byteOffset
            self.real_start_piece_id                 = self.start_piece_id                 = int(byteOffset/self.piece_length) 
            self.real_start_block_offset             = self.start_block_offset             = int((byteOffset%self.piece_length)/BLOCK_SIZE)
            self.real_start_byte_offset             = self.start_byte_offset             = int((byteOffset%self.piece_length)%BLOCK_SIZE)
            self.debug_mesg( 'setMarkersForFileToDownload','self.real_start_absolute_byte_offset '+str(self.real_start_absolute_byte_offset))
            self.debug_mesg( 'setMarkersForFileToDownload','self.real_start_piece_id '+str(self.real_start_piece_id))
            self.debug_mesg( 'setMarkersForFileToDownload','self.real_start_block_offset '+str(self.real_start_block_offset))
            self.debug_mesg( 'setMarkersForFileToDownload','self.real_start_byte_offset '+str(self.real_start_byte_offset))

            self.real_file_to_stream_length         = self.file_to_stream_length         = self.file_to_stream['length']
            self.start_diff = 0;


            #TODO: Maybe needs to be remastered too. It seems like he's checking the same condition twice
            if(self.real_start_byte_offset > 0):
                self.start_absolute_byte_offset -= self.real_start_byte_offset
                self.file_to_stream_length += self.real_start_byte_offset

            if( ((self.real_start_absolute_byte_offset + self.real_file_to_stream_length)%self.piece_length)%BLOCK_SIZE != 0 ):
                diff = ((self.real_start_absolute_byte_offset + self.real_file_to_stream_length)%self.piece_length)%BLOCK_SIZE
                diff = BLOCK_SIZE - diff
                self.file_to_stream_length += diff
                self.end_byte_offset = diff
            #TODO: === End of part ===

            print 'FileManager.setMarkersForFileToDownload:start_piece_id=',self.start_piece_id, 'start_block_offset=',self.start_block_offset,'start_byte_offset=', self.start_byte_offset


        else :
      #      self.abs_number_of_pieces=info['length']/info['piece length']
      #      self.end_number_of_bytes=info['length']%info['piece length']
      #      self.end_number_of_blocks=self.end_number_of_bytes/BLOCK_SIZE
      #      self.end_number_of_bytes=self.end_number_of_bytes%BLOCK_SIZE
      #      print 'FileManager.setMarkersForFileToDownload:abs_number_of_pieces:',self.abs_number_of_pieces
      #      print 'FileManager.setMarkersForFileToDownload:end_number_of_blocks:',self.end_number_of_blocks
      #      print 'FileManager.setMarkersForFileToDownload:end_number_of_bytes:',self.end_number_of_bytes
      #      print "FileManager.setMarkersForFileToDownload:FileManager.setMarkersForFileToDownload:Single File Path :", info['name']
            self.start_absolute_byte_offset =0
            self.start_piece_id = 0
            self.start_block_offset = 0
            self.start_byte_offset = 0
            self.end_byte_offset=0#16960
            self.file_to_stream_length = info['length']
            print 'FileManager.setMarkersForFileToDownload:info',info
            self.file_to_stream = {'name':info['name'], 'length':info['length']}#, 'md5sum': info['md5sum']}

        #self.current_pos_piece_id = 702
        self.current_pos_piece_id =self.start_piece_id
        self.current_block_offset = self.start_block_offset

    # Returns what 'data' to be written at (piece_id, block_id)
    # The same (piece_id, block_id) will have upto MALI_LIMIT data blocks.
    # If atleast two of them are same, then we know that it is not malicious (to a very good extent atleast)
    # Returns -1 to say that two same data blocks found yet
    def shouldWrite(self, piece_id, block_id, data):
        if data not in self.block_data[piece_id][block_id]  :
            self.block_data[piece_id][block_id][data] = 0
        self.block_data[piece_id][block_id][data] += 1
        # A certain Data pair has been formed. Return this data
        if self.block_data[piece_id][block_id][data] > 1 or self.block_data[piece_id][block_id][data] >= MALI_LIMIT :
            return data
        # If none of the data received for the given block do not match and the max limit has been reached then randomly pick any piece
        # This might cause the selection of a malicious data block. 
        # TODO : Get rid of malicious data blocks
        if len(self.block_data[piece_id][block_id]) == MALI_LIMIT:
            self.block_data[piece_id][block_id].popitem()[0]
        # No Match found until now, but the Max Limit has not been reached as well
        return -1


    # Arguments : 
    #     piece_id     : The offset of the piece where to write the data 
    #     block_id     : The offset of the block inside the piece where to write the data
    #     data         : The data to be written
    def writeToFile(self, piece_id, block_id, data):
        # If the block has already been written, then skip
        if self.blockExists(piece_id, block_id) :
            return
        data = self.shouldWrite(piece_id, block_id, data)
        # If the blocks already been added have no common data yet
        if data == -1 :
            return

        if piece_id == self.start_piece_id and block_id == self.start_block_offset :
            data = data[self.start_byte_offset:]

        if self.incrementPieceBlock(piece_id, block_id) == (-1, -1):
            self.debug_mesg( "writeToFile","incrementPieceBlock == (-1, -1):{0},{1}".format(str(piece_id),str(block_id)))
            data = data[:-self.end_byte_offset]
        self.debug_mesg( "writeToFile","Writing to Disk {0},{1}".format(str(piece_id),str(block_id)),mes_status='FAIL')
        Logger.info(str("Writing to Disk " + str(piece_id) + "," + str(block_id)))
        file_name = self.file_to_stream['name']
        fout = open(file_name, "rb+")
        seek_offset = self.byteOffset(piece_id, block_id) - self.start_absolute_byte_offset
        self.debug_mesg( 'writeToFile','byteOffset for piece_id={0}, block_id={1} is {2}'.format(str(piece_id),str(block_id),str(seek_offset)),mes_status='FAIL')
        self.debug_mesg( "writeToFile", 'seek_offset:{0} for len {1}'.format(str(seek_offset),str(len(data))),mes_status='FAIL')
        if(seek_offset < 0 or seek_offset >= self.file_to_stream_length):
            raise "ERROR : The Block being written is out of bounds or is not the file being downloaded"
            return
        fout.seek(seek_offset)
        fout.write(data)
        fout.close()
        self.updateStatus(piece_id, block_id)
        self.bytesWritten += len(data)
        self.debug_mesg( "writeToFile","{0} bytes written".format(self.bytesWritten),mes_status='FAIL')
        self.updateCurrentHeadPosition()

    # Arguments : 
    #     piece_id     : The offset of the piece where to read the data from 
    #     block_id     : The offset of the block inside the piece where to read the data from
    # Return :
    #     A bytearray of size 'BLOCK_SIZE' which represents the block at (piece_id, block_id)

    def readBlock(self, piece_id, block_id):
        Logger.info(str("Reading From Disk " + str(piece_id) + "," + str(block_id)))
        file_name = self.file_to_stream['name']
        fin = open(file_name, "rb")
        seek_offset = self.byteOffset(piece_id, block_id) - self.start_absolute_byte_offset
        if(seek_offset < 0 or seek_offset >= self.file_to_stream_length):
            raise "ERROR : The Block that is trying to be read is out of bounds or is not the file being downloaded"
            return
        fin.seek(seek_offset)
        data = bytearray(fin.read(BLOCK_SIZE))
        fin.close()
        return data

    # Checks to see if the Block has already been written and saved
    def blockExists(self, piece_id, block_id):
        self.debug_mesg( 'blockExists','checking {0},{1}'.format(str(piece_id),str(block_id)))
        if self.checkBounds(piece_id, block_id) != 0:
            return False
        if(self.block_status[piece_id][block_id] == True):
            return True
        return False

    # Returns the Byte Offser (0 Index) for a given combination of (piece_id, block_id)
    #FIXME: Try to do faster
    def byteOffset(self, piece_id, block_id):
        ret = 0
        ret += piece_id*self.piece_length
        ret += block_id*BLOCK_SIZE
        return ret

    def getBlockCountFor(self, piece_id):   #5
        if piece_id >= len(self.block_status) or piece_id < 0:
           # raise Exception("ERROR : Piece ID out of Bounds for piece_id "+str(piece_id))
            pass
        return len(self.block_status[piece_id])

    def getPieceLength(self, piece_id):
        return self.getBlockCountFor(piece_id) * BLOCK_SIZE

    # Update the Status Bits to true, to show we have the given block
    def updateStatus(self, piece_id, block_id):
        self.debug_mesg( 'updateStatus','Updating status for {0},{1}'.format(str(piece_id),str(block_id)))
        self.block_status[piece_id][block_id] = True

        
    # Increment the pair (piece_id, block_id) to the next in interation and return the new (piece_id', block_id')
    # The Function Returns (-1, -1) if the end is reached
    def incrementPieceBlock(self, piece_id, block_id):  #3
        self.debug_mesg('incrementPieceBlock','incrementing piece_id={0},block_id={1}'.format(str(piece_id),str(block_id)))
        val = self.checkBounds(piece_id, block_id+1)
        if val == 0:
            return (piece_id, block_id+1)
        elif val == 1:
            return (piece_id+1, 0)
        else :
            return (-1, -1)

    def getPieceBlockForByteOffset(self, byteoffset):
        piece_id = int(byteOffset/self.piece_length) 
        block_id = int((byteOffset%self.piece_length)/BLOCK_SIZE)
        return piece_id,block_id

    # Updates the Position of the Head.
    # The Head points to the first unavailable block minus 1 in the entire data.
    # Sets 'StreamCompleted' as True if End of File Reached
    def updateCurrentHeadPosition(self):
        self.debug_mesg( 'updateCurrentHeadPosition','updating current head position')
        while( self.block_status[self.current_pos_piece_id][self.current_block_offset] == True ):
            (self.current_pos_piece_id, self.current_block_offset) = self.incrementPieceBlock(self.current_pos_piece_id, self.current_block_offset)
            if self.current_pos_piece_id == -1 and self.current_block_offset == -1:
                self.StreamCompleted = True
                return

    # Checks whether (piece_id, block_id) is correct
    # Returns 0 : If all Correct
    # Returns 1 : If piece_id needs to be incremented by 1 and block_id needs to be set to 0
    # Returns 2 : If this is the last block_id and last piece_id of the given File we are streaming
    def checkBounds(self, piece_id, block_id):      #4
        self.debug_mesg( 'checkBounds','Checking for  piece_id={0}, block_id={1}'.format(str(piece_id),str(block_id)))
        #print piece_id-1,self.block_status[piece_id-1]
        if not piece_id >= len(self.block_status) or piece_id < 0:
            self.debug_mesg( 'checkBounds','Normal Bound: Piece id is not >= {0} or {1} < 0'.format(str(len(self.block_status)),str(piece_id)))
            if(self.getBlockCountFor(piece_id) > block_id):
                seek_offset = self.byteOffset(piece_id, block_id) - self.start_absolute_byte_offset
                if( seek_offset >= self.file_to_stream_length):
                    return 2
                else:
                    return 0
            if self.checkBounds(piece_id+1, 0) == 0:
                return 1
        return 2

