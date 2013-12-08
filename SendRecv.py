__author__ = 'Alex Borg'

# base class for creating send receive algorithms
# classes should inherit from this and override the send and receive functions
class SendRecvObj:

    def clear(self):
        pass

    #send should always return byte arrays after each call
    #param dataIn - should be a bytearray of the bytes to be sent
    #return - an array of bytearrays that represent packetization of the input data
    def send(self, dataIn):
        dataOut = []
        dataOut.append(dataIn)
        return dataOut

    #recv does not necessary return bytes after each call
    # (e.g. it could be waiting for checksum data)
    #param dataIn - a bytearray of the bits that come from the network
    #return - a bytearray of the reconstructed bytes
    def recv(self, dataIn):
        return dataIn


