__author__ = 'moar'


class StatisticManager(object):
    #
    #TODO: Manage statistic for every peer
    #
    def __init__(self):
        self.current_speed=0            #kilobytes/second
        self.max_speed=0                #kilobytes/second
        self.downloaded_from_peer=0
        self.uploaded_to_peer=0
        self.downloaded_pieces=set()    #kilobytes
        self.uploaded_pieces=set()      #kilobytes

    def update(self,speed=0,downloaded=0,uploaded=0,downloaded_piece=None,uploaded_piece=None):
        self.current_speed=speed
        self.max_speed=self.max_speed if speed<self.max_speed else speed
        self.downloaded_from_peer+=downloaded
        self.uploaded_to_peer+=uploaded
        self.downloaded_pieces.add(downloaded_piece)
        self.uploaded_pieces.add(uploaded_piece)

    def get_efficiency(self,bytesWritten,dataReceived):
        (bytesWritten*100)/self.torrent.requester.total_data_received



    Logger.info("File Size Remaining: " + str((self.torrent.file_manager.file_to_stream_length - self.torrent.file_manager.bytesWritten)/1024) + " kilobytes")
    Logger.info("Efficiency: " + str((self.torrent.file_manager.bytesWritten*100)/self.torrent.requester.total_data_received) + "%")
    Logger.info("Speed: " + str(self.torrent.file_manager.bytesWritten/((time.time()-self.torrent.start_time)*1024)) + " kilobytes/second")