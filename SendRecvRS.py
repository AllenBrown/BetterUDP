__author__ = 'William Sims'

from SendRecv import SendRecvObj
from net_ecc import EncodePackets
from net_ecc import DecodePackets
from net_ecc import ParseHeader

import math

PACKET_SIZE = 1024

class SendRecvRS(SendRecvObj):
    # send will break up packets using Reed-Solomon encoding.
    #return - an array of bytearrays that represent packetization of the input data
    def send(self, dataIn):
        dataOut = []

        k = int(math.ceil(float(len(dataIn)) / PACKET_SIZE))
        n = int(math.ceil(k * 1.1))
        dataOut = EncodePackets(str(dataIn), n, k)

        return dataOut


    def __init__(self):
        self.receivedData = []

    def clear(self):
        self.receivedData = []

    #recv does not necessary return bytes after each call
    # decodes the packets using Reed-Solomon
    #param dataIn - a bytearray of the bits that come from the network
    #return - a bytearray of the reconstructed bytes
    def recv(self, dataIn):
        self.receivedData.append(str(dataIn))
        header = ParseHeader(dataIn[:dataIn.find('\n')])
        n, k = int(header[2]), int(header[4])
        if len(self.receivedData) == k:
            recoveredData = DecodePackets(self.receivedData)
        else:
            recoveredData = ''
        return recoveredData

