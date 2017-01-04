__author__ = 'moar'
import logging
from uuid import uuid3,NAMESPACE_URL,getnode
from datetime import datetime
from platform import uname
from struct import pack
import TrackerAnnounce
from twisted.internet import reactor

CLIENT_VERSION='0.01b'

ANNOUNCER_POOL=[['10.0.0.57',9999],['10.0.0.57',63351]]


#TODO:need to receive this from the Announcer
'''############################################################
'''############################################################

'''############################################################
'''############################################################
def start_log():
    logging.basicConfig(filename='ptp2p_%s.log'%(datetime.now().strftime('%Y-%m-%d')),
                            filemode='a',
                            format='%(asctime)s : %(message)s',
                            level=logging.INFO)
    logging.info("Client Started.\nLog Initialized")

class TorrentSharingNode(object):
    """Main Torrent Client Class"""
    def __init__(self, torrent_link):
        self.torrent_link = torrent_link
        #self.peerID = self.generatePID()
        self.port = 61234
       # self.initAll()




    def initAll(self):
    #    self.isMagnet = Magnet.isMagnetURI(self.torrent_link)
    #    Logger.info("Initializing Torrent Data")
    #    if(self.isMagnet == True):
     #       # Send MagnetURI To class and get torrent Data
    #        pass
    #    else:
            # Get Torrent Data From Net
        torrent_raw_data  = self.downloadTorrentFile()
        self.torrent = Torrent.Torrent(reactor, raw_data = torrent_raw_data, peer_id = self.peerID, port = self.port)
        Logger.info("Initialization For Torrent Data Complete")

    def downloadTorrentFile(self):
        Logger.info("Now Downloading Torrent File")
        url = self.torrent_link
        f = urllib2.urlopen(url)
        temp_torrent_filename = "tempTorrentFile.torrent.gz"
        data = f.read()
        try:
            #download the torrent file pointed to by the url.
            with open(temp_torrent_filename, "wb") as code:
                code.write(data)
            #save it in a temp file.
            f = gzip.open(temp_torrent_filename,'rb')
            file_content = f.read()
            #unzip it to extract original contents and delete this temp file.
            os.remove(temp_torrent_filename)
        except:
            file_content = data
        Logger.info("Torrent File Download Complete")
        return file_content

class Client(object):
    def __init__(self):
        super(Client,self).__init__()
        #self.PID=
        self.init_ClientInfo()
        self.init_Announcers()
       # self.announcers=dict

    def init_ClientInfo(self):
        self.info={
            'client_id':self.get_CID(),
            'client_version':self.get_clientVersion(),
            'os_info':self.get_OSInfo()
        }
        print self.info

    def get_clientVersion(self):
        return pack('5s',CLIENT_VERSION)

    def get_OSInfo(self):
        return pack('20s',' '.join((uname()[0],uname()[2],uname()[3]))[:20])

    def get_CID(self):
        return pack('36s',str(uuid3(NAMESPACE_URL,''.join(uname())+str(getnode())))[:36])

    def init_Announcers(self):
        for announcer in ANNOUNCER_POOL:
            tracker=TrackerAnnounce.UDPAnnouncerProtocol(announcer,self.info)
            reactor.listenUDP(0,tracker)
        reactor.run()





def start_peer():
    pass



if __name__=='__main__':
    #TorrentSharingNode('a')
    client=Client()
    #start_log()
   # start_peer()