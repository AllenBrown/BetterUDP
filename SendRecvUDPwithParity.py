__author__ = 'Allen Brown'

from SendRecv import SendRecvObj

# Inherits from the SendRecv class to implement Better UDP
class SendRecvUDPwithParity(SendRecvObj):
    bufferSubheader = []
    bufferData = []
    packetDataSize = 510
    packetSubheaderSize = 2		# Additional Header (1 byte) - Sequence number
								# Additional Header (1 byte) - end of packets flag
    packetHeaderSize = 8

    # Send will break up packets into 510 bytes of data + a 2 byte sub-header for more reliable UDP + a 8 byte header.
    #return - an array of bytearrays that represent packetization of the input data
    def send(self, dataIn):
        dataOut = []
        buffer = []

        offset = 0			# Used to keep track of simulated send
        sequenceNumber = 1	# Used to keep track of sequence as well as which packet gets lost

        print "send length  ", len(dataIn)
        # Keep sending until all commanded data has been sent (simulated send)
        while offset < len(dataIn):
            # Default end of packets flag to 0
            endOfPackets = 0

            # Allocate memory for packet
            packet = bytearray()

            # Allocate memory for UDP header and append header to packet
            header = bytearray(self.packetHeaderSize)
            packet.extend(header)

            # Allocate memory to UDP sub-header for more reliable UDP
            subheader = bytearray(self.packetSubheaderSize)

            # Set sequencer number in sub-header
            subheader[0] = sequenceNumber

            # If last packet is being sent out of 10 packets
            if sequenceNumber == 10:
                # Set end of packet flag
                endOfPackets = 1
				
            # Perform additional check to see if this is last packet being sent but it's not the 10th packet
            elif ((offset + self.packetDataSize) >= len(dataIn) and (sequenceNumber < 10)):
                # Set end of packet flag
                endOfPackets = 1

            # Set end of packets flag in sub-header
            subheader[1] = endOfPackets

            # Append sub-header to packet
            packet.extend(subheader)

            # Append data to packet
            packet.extend(dataIn[offset:offset+self.packetDataSize])

            # Store data for future parity packet
            buffer.extend(dataIn[offset:offset+self.packetDataSize])

            # Append packet to dataOut to simulate sending packet out on network
            dataOut.append(packet)

            # Increment offset by packetDataSize (510)
            offset += self.packetDataSize

            # If last packet sent (simulated send) contained the end of packets flag set true
            if endOfPackets == 1:
                # Then create and send a parity packet based on all 10 packets

                # Reset Sequence Number for future messages
                sequenceNumber = 0
				
            # Increment the sequence number
            sequenceNumber += 1
        return dataOut

    #recv does not necessary return bytes after each call
    # (e.g. it could be waiting for checksum data)
    #param dataIn - a bytearray of the bits that come from the network
    #return - a bytearray of the reconstructed bytes
    def recv(self, dataIn):
        dataOut = []
        header = bytearray(self.packetHeaderSize)

        offset = 0			# Used to keep track of simulated send
        print "receive length  ", len(dataIn)
        SendRecvUDPwithParity.bufferData = bytearray()
        #SendRecvUDPwithParity.bufferData.append(dataIn[self.packetHeaderSize + self.packetSubheaderSize:self.packetHeaderSize + self.packetSubheaderSize + self.packetDataSize])
        return dataIn[self.packetHeaderSize + self.packetSubheaderSize:]
        #return SendRecvUDPwithParity.bufferData[offset:]

        # Keep receiving until all commanded data has been received (simulated receive)
        while offset < len(dataIn):
            # Pull UDP header from packet and increment offset
            header = dataIn[offset:offset+self.packetHeaderSize]
            offset += self.packetHeaderSize

            # Pull UDP header from packet and increment offset
            bufferSubheader.append(dataIn[offset:offset+self.packetSubheaderSize])
            offset += self.packetSubheaderSize

            # Append packet from dataIn to dataOut; simulating receiving a packet from the network
            dataOut.append(dataIn[offset:offset+self.packetDataSize])

            # Store data for future parity packet
            bufferData.append(dataIn[offset:offset+self.packetDataSize])

            # Increment offset by packetDataSize (510)
            offset += self.packetDataSize

            # If last packet sent (simulated send) contained the end of packets flag set true
            #if endOfPackets == 1:
            # Set sequencer number from sub-header
            #sequenceNumber = subheader[1]

            # Set end of packet flag from sub-header
            #endOfPackets = subheader[2]
        return dataOut[offset:]