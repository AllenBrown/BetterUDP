__author__ = 'Alex Borg'

from SendRecv import SendRecvObj

# inherits from the SendRecv class to implement the UDP header. Breaks up each
# data block into 1460 byte packets
# FIXME: Add proper header information to allow whole packet loss instead of each fragment
class SendRecvUDP(SendRecvObj):
    packetDataSize = 1472
    packetHeaderSize = 8

    #send will break up packets into 1472 bytes of data + a 4 byte header.
    # this leaves 20 bytes for the IP header
    #return - an array of bytearrays that represent packetization of the input data
    def send(self, dataIn):
        dataOut = []

        offset = 0
        while offset < len(dataIn):
            packet = bytearray()
            header = bytearray (self.packetHeaderSize)
            packet.extend(header)
            packet.extend(dataIn[offset:offset+self.packetDataSize])
            dataOut.append(packet)
            offset += self.packetDataSize
        return dataOut

    #recv does not necessary return bytes after each call
    # (e.g. it could be waiting for checksum data)
    #param dataIn - a bytearray of the bits that come from the network
    #return - a bytearray of the reconstructed bytes
    def recv(self, dataIn):
        return dataIn[self.packetHeaderSize:]



