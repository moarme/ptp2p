#!usr/bin/env python

#kristen widman and tom ballinger
#Oct 15, 2012

import urllib
import struct
from datetime import datetime
from Constants import *

'''''''''''''''''''''
# Abstract Classes
'''''''''''''''''''''
def number_to_bytes(number):  
    '''returns a number 4 bytes long'''
    if number < 255:
        length = '\x00\x00\x00' + chr(number)
    elif number < 256**2:
        length = '\x00\x00' + chr((number)/256) + chr((number) % 256)
    elif number < 256**3:
        length = ('\x00'+ chr((number)/256**2) + chr(((number) % 256**2) / 256) +
            chr(((number) % 256**2) % 256))
    else:
        length = (chr((number)/256**3) + chr(((number)%256**3)/256**2) + chr((((number)%256**3)%256**2)/256) + chr((((number)%256**3)%256**2)%256))
    return length

def bytes_to_number(bytestring):  
    '''bytestring assumed to be 4 bytes long and represents 1 number'''
    number = 0
    i = 3
    for byte in bytestring:
        try:
            number += ord(byte) * 256**i
        except(TypeError):
            number += byte * 256**i
        i -= 1
    return number

class Message(object):
    """This is for everything but Handshake
        If you subclass this, you should provide class attributes for:
        protocol_args     (if not implemented, will use base class - [])
        protocol_extended (if not implemented, will use base class - None)
        msg_id (this should be a single byte)
    """
    DBG_MODE=G_DBG_MODE
    DBG_MODE=False
    protocol_args = []
    protocol_extended = None

    def __init__(self,**kwargs):
        if 'response' in kwargs:
            self.debug_mesg( '__init__','::Got response::')
            self.__setup_from_bytestring(kwargs['response'])
        elif set(self.protocol_args + ([self.protocol_extended] if self.protocol_extended else [])) == set(kwargs.keys()):
            self.__setup_from_args(kwargs)
        else:
            self.debug_mesg( '__init__',':: stuff from message class{0},{1}'.format(str(set(self.protocol_args)),  str([self.protocol_extended]) if self.protocol_extended else str()))
            self.debug_mesg( '__init__',':: kwargs'+str(set(kwargs.keys())))
            raise Exception("Bad init values")

    def debug_mesg(self,afunc,dmessage,mes_status='OKGREEN'):
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
            print datetime.now().strftime('Messages.Message.{0}: %Y.%m.%d %H:%M:%S\t\t').format(afunc)\
                  +bcolors['ENDC']+bcolors[mes_status]+str(dmessage)+bcolors['ENDC']

    def __setup_from_bytestring(self, bytestring):
        self.msg_length = bytes_to_number(bytestring[0:4])
        # print "ByteString :", bytestring
        if len(bytestring) > 4:
            # msg_id = bytestring[4]
            msg_id = struct.unpack("B",bytestring[4])[0]
            # print "1.msg_id Set :" , msg_id
        else:
            msg_id = ''
            # print "2.msg_id Set :" , msg_id
        assert self.msg_id == msg_id, str("Message ID's do not match." + str(self.msg_id) + str(msg_id))
        payload = bytestring[5:]
        for arg_name in self.protocol_args:
            # print "Setting: "+str(arg_name)+" "+str(payload[:4])
            setattr(self, arg_name, payload[:4])
            payload = payload[4:]
        if self.protocol_extended:
            # print "Setting: "+str(self.protocol_extended)+" "+str(payload)
            
            setattr(self, self.protocol_extended, payload)

    def __setup_from_args(self, kwargs):
        for arg_name in self.protocol_args:
            setattr(self, arg_name, kwargs[arg_name])
        if self.protocol_extended:
            setattr(self, self.protocol_extended, kwargs[self.protocol_extended])
        if isinstance(self, KeepAlive):
            self.msg_length = number_to_bytes(0)
        else:
            self.msg_length = number_to_bytes(sum(len(x) for x in kwargs.values()) + 1)

    def __str__(self):
        s = ''
        s += self.msg_length
        if self.msg_id != '':
            s += chr(self.msg_id)
        for arg_name in self.protocol_args:
            s += str(getattr(self, arg_name))
        if self.protocol_extended:
            # print self.protocol_extended, s
            s += getattr(self, self.protocol_extended)
        return s

    def __repr__(self):
        return repr(str(self))

    def __len__(self):
        return bytes_to_number(self.msg_length) + 4

'''''''''''''''''''''
# Peer Communication Classes
'''''''''''''''''''''
class PeerHandshake(object):
    """Represents a handshake object
        Has 2 inits to create from incoming bytestring or from info_hash and peer_id
        for outgoing handshake.
    """
    DBG_MODE=G_DBG_MODE
    DBG_MODE=False
    def __init__(self,*args):
        self.debug_mesg( '__init__','Handshake message len:'+str(len(args)))
        if len(args) == 1: self.__setup1(*args)
        elif len(args) == 2: self.__setup2(*args)

    def debug_mesg(self,afunc,dmessage,mes_status='OKGREEN'):
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
            print datetime.now().strftime('Messages.Handshake.{0}: %Y.%m.%d %H:%M:%S\t\t').format(afunc)\
                  +bcolors['ENDC']+bcolors[mes_status]+str(dmessage)+bcolors['ENDC']

    def __setup1(self,payload):
        self.pstrlen = payload[0]
        self.pstr = payload[1:20]  #pstrlen assumed = 19; might not be true (if in another protocol)
        self.reserved = payload[20:28]
        self.info_hash = payload[28:48]
        self.peer_id = payload[48:68]
    #pstr - string identifier of the protocol
    def __setup2(self,info_hash,peer_id):
        self.pstrlen    = chr(19)
        self.pstr       = "BitTorrent protocol"
        self.reserved   = "\x00\x00\x00\x00\x00\x00\x00\x00"
        self.info_hash  = urllib.unquote(info_hash) # We store the info_hash in the percentage escape format. So we have to unquote it
        self.peer_id    = urllib.unquote(peer_id)   # We store the peer_id in the percentage escape format. So we have to unquote it

    def __str__(self):
        return self.pstrlen+self.pstr+self.reserved+self.info_hash+self.peer_id

    def __len__(self):
        return 49+ord(self.pstrlen)

class KeepAlive(Message):
    msg_id = ''

class Choke(Message):
    msg_id = 0

class Unchoke(Message):
    msg_id = 1

class Interested(Message):
    msg_id = 2

class NotInterested(Message):
    msg_id = 3

class Have(Message):
    protocol_args = ['index']
    msg_id = 4

class Bitfield(Message):
    protocol_extended = 'bitfield'
    msg_id = 5

class Request(Message):
    protocol_args = ['index','begin','length']
    msg_id = 6
    
class Piece(Message):
    protocol_args = ['index','begin']
    protocol_extended = 'block'
    msg_id = 7

class Cancel(Message):   
    protocol_args = ['index','begin','length']
    msg_id = 8

class Port(Message):
    protocol_extended = 'listen_port'
    msg_id = 9

'''''''''''''''''''''
# Announcer Communication Classes
'''''''''''''''''''''
class AnnouncerHandshake(Message):
    protocol_args = ['client_version','os_info','client_id']

class HelloToAnnouncer(Message):
    protocol_args = ['info_hash','downloaded','uploaded']

#TODO:
class KeepAnnouncerAlive(Message):
    protocol_args = ['client_id','list_info_hash']