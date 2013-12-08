__author__ = 'Allen Brown'

from SendRecv import SendRecvObj

# Inherits from the SendRecv class to implement Better UDP
class SendRecvUDPwithParity(SendRecvObj):

    packetDataSize = 508
    packetSubheaderSize = 4		# Additional Header (1 byte) - Sequence number (count up from 1), parity packet (0)
								# Additional Header (1 byte) - end of packets flag (2), parity packet (1)
                                # Additional Header (2 byte) - packet size
    packetHeaderSize = 8

    def __init__(self):
        self.sendBufferData = []
        self.receiveBufferData = []
        self.bufferSubheader = []
        self.sequenceSend = 0
        self.sequenceReceive = 0
        self.resetReceiveCount = 0
        self.lostPacketCount = 0
        self.subheaderTypeFlag = 0
        self.packetSize = 0

    # Send will break up packets into 508 bytes of data + a 4 byte sub-header for more reliable UDP + a 8 byte header.
    #return - an array of bytearrays that represent packetization of the input data
    def send(self, dataIn):
        dataOut = []
        buffer = bytearray()

        offset = 0            # Used to keep track of simulated send
        self.sequenceSend = 0 # Used to keep track of entire sequence
        paritySequence = 0    # Used to keep track of parity sequence

#DEBUG        print "send length  ", len(dataIn)

        # For small packets, just send them out
        if len(dataIn) < (self.packetDataSize):
            packet = bytearray()
            header = bytearray(self.packetHeaderSize)
            packet.extend(header)
            packet.extend(dataIn[0:len(dataIn)])
            dataOut.append(packet)
            return dataOut
            
        # Keep sending until all commanded data has been sent (simulated send)
        while offset < len(dataIn):
            # Increment sequence counters
            self.sequenceSend += 1
            paritySequence += 1
            
            # Reset flags to 0
            endOfPacketsFlag = 0
            sendParityPacket = 0

            # Allocate memory for packet
            packet = bytearray()

            # Allocate memory for UDP header and append header to packet
            header = bytearray(self.packetHeaderSize)
            packet.extend(header)

            # Allocate memory to UDP sub-header for more reliable UDP
            subheader = bytearray(self.packetSubheaderSize)

            # Set sequencer number in sub-header
            subheader[0] = self.sequenceSend

            # If last packet is being sent out of 10 packets
            if paritySequence == 10:
                # Set parity packet flag
                sendParityPacket = 1
				
            # Perform additional check to see if this is last packet being sent but it's not the 10th packet
            elif (offset + self.packetDataSize) >= len(dataIn):
                # Set end of packet flag
                endOfPacketsFlag = 2
                
                # Only send parity packet if more than one packet is sent
                if paritySequence > 1:
                    # Set parity packet flag
                    sendParityPacket = 1

            # Set sub-header type flag
            subheader[1] = endOfPacketsFlag

            # Check if last packet in block is less than max size
            if (len(dataIn) - offset) < self.packetDataSize:
                packetSize = len(dataIn) - offset
                fullSizePacket = bytearray(self.packetDataSize)
                
                # Copy the contents into the fullSizepacket
                for index in range(0, packetSize - 1):
                    fullSizePacket[index] = dataIn[offset + index]
                
                # Set sequencer number and append sub-header to packet
                if packetSize > 255:
                    subheader[2] = 255
                    subheader[3] = packetSize - 255
                else:
                    subheader[2] = packetSize
                    subheader[3] = 0
                packet.extend(subheader)
                
                # Append data to packet
                packet.extend(fullSizePacket[0:self.packetDataSize])

                # Store data for future parity packet
                buffer.extend(fullSizePacket[0:self.packetDataSize])
            else:
                packetSize = self.packetDataSize
                
                # Set sequencer number and append sub-header to packet
                subheader[2] = 255
                subheader[3] = packetSize - 255
                packet.extend(subheader)
            
                # Append data to packet
                packet.extend(dataIn[offset:offset+self.packetDataSize])

                # Store data for future parity packet
                buffer.extend(dataIn[offset:offset+self.packetDataSize])
            
            # Append packet to dataOut to simulate sending packet out on network
            dataOut.append(packet)

            # Increment offset by packetDataSize
            offset += packetSize

            # If a parity packet needs to be sent
            if sendParityPacket == 1:
#DEBUG                print "buffer length  ", len(buffer)
                # Allocate memory and send a parity packet based on all 10 packets
                parityPacket = bytearray(self.packetHeaderSize + self.packetSubheaderSize + self.packetDataSize)
            
                # Set sub-header in parity packet
                parityPacket[self.packetHeaderSize] = paritySequence
                parityPacket[self.packetHeaderSize + 1] = 1 # Set 1 for parity packet flag
                if packetSize > 255:
                    parityPacket[self.packetHeaderSize + 2] = 255
                    parityPacket[self.packetHeaderSize + 3] = packetSize - 255 # Provide size of last packet
                else:
                    parityPacket[self.packetHeaderSize + 2] = packetSize
                    parityPacket[self.packetHeaderSize + 3] = 0
                
                # Loop through all bytes and set parity
                for index in range(0,self.packetDataSize - 1):
                    # At a minimum 2 packets have been sent, so send a parity packet based on 2 packets
                    parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                        buffer[index +(self.packetDataSize * 0)]^
                        buffer[index +(self.packetDataSize * 1)])
                    # If more than 2 packets have been sent, send a parity packet based on 3 packets
                    if self.sequenceSend > 2:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^
                            buffer[index +(self.packetDataSize * 2)])
                    # If more than 3 packets have been sent, send a parity packet based on 4 packets
                    if self.sequenceSend > 3:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^        
                        buffer[index +(self.packetDataSize * 3)])
                    # If more than 4 packets have been sent, send a parity packet based on 5 packets
                    if self.sequenceSend > 4:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^
                        buffer[index +(self.packetDataSize * 4)])
                    # If more than 5 packets have been sent, send a parity packet based on 6 packets
                    if self.sequenceSend > 5:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^    
                        buffer[index +(self.packetDataSize * 5)])
                    # If more than 6 packets have been sent, send a parity packet based on 7 packets
                    if self.sequenceSend > 6:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^
                        buffer[index +(self.packetDataSize * 6)])
                    # If more than 7 packets have been sent, send a parity packet based on 8 packets
                    if self.sequenceSend > 7:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^
                        buffer[index +(self.packetDataSize * 7)])
                    # If more than 8 packets have been sent, send a parity packet based on 9 packets
                    if self.sequenceSend > 8:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^
                        buffer[index +(self.packetDataSize * 8)])
                    # If more than 9 packets have been sent, send a parity packet based on 10 packets
                    if self.sequenceSend > 9:
                        parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index] = (
                            parityPacket[self.packetHeaderSize + self.packetSubheaderSize + index]^
                        buffer[index +(self.packetDataSize * 9)])
                    
                    # Reset parity sequence
                    paritySequence = 0
                # Append packet to dataOut to simulate sending packet out on network
                dataOut.append(parityPacket)
        return dataOut

    #recv does not necessary return bytes after each call
    # (e.g. it could be waiting for checksum data)
    #param dataIn - a bytearray of the bits that come from the network
    #return - a bytearray of the reconstructed bytes
    def recv(self, dataIn):
        empty = []
        header = bytearray(self.packetHeaderSize)

        offset = 0			# Used to keep track of simulated send
        #DEBUG print "receive length  ", len(dataIn)

        # For small packets, just receive them
        if len(dataIn) < (self.packetHeaderSize + self.packetDataSize):
            # Check to see if we lost non-parity packet
            if len(dataIn) == 0 and self.subheaderTypeFlag <> 2:
                # If we are resetting the receive count, then empty our static arrays
                if self.subheaderTypeFlag == 1:
                    self.resetReceiveCount = 0
                    self.receiveBufferData = []
                    self.bufferSubheader = []
                    self.lostPacketCount = 0
                    self.sequenceReceive = 0
                    self.subheaderTypeFlag = 0
                    
                # Store blanks in case parity packet might recover in the future
                self.receiveBufferData.extend(bytearray(self.packetDataSize))
                self.bufferSubheader.extend(bytearray(self.packetSubheaderSize))
                self.sequenceReceive += self.packetDataSize

            # Check to see if we lost a parity packet
            if len(dataIn) == 0 and self.subheaderTypeFlag == 2:
                # Store data before we reset static buffers
                dataOut = bytearray()
                #DEBUG print "self.receiveBufferData length before reset ", len(self.receiveBufferData)
                dataOut.extend(self.receiveBufferData[0:len(self.receiveBufferData)])
                
                # Reset static data
                self.resetReceiveCount = 0
                self.receiveBufferData = []
                self.bufferSubheader = []
                self.lostPacketCount = 0
                self.sequenceReceive = 0
                self.subheaderTypeFlag = 0
                
                # Return current receiveBufferData, we can't fix anything since we lost parity packet
                #DEBUG print "dataOut length ", len(dataOut)
                return dataOut 
                
            self.lostPacketCount += 1
            return dataIn[self.packetHeaderSize:]
            
        else:
            # Pull UDP header from packet and increment offset
            header = dataIn[offset:offset+self.packetHeaderSize]
            offset += self.packetHeaderSize

            # Pull UDP header from packet and increment offset
            sequenceNumber = dataIn[offset]
            self.subheaderTypeFlag = dataIn[offset + 1]
            self.packetSize = dataIn[offset + 2] + dataIn[offset + 3]
            #DEBUG print "end of packet/parity flag ", self.subheaderTypeFlag, " sequence ", sequenceNumber, " packet size ", self.packetSize, " lost count ", self.lostPacketCount
            
            # If we are resetting the receive count, then empty our static arrays
            if self.resetReceiveCount == 1 or (sequenceNumber == 1 and self.lostPacketCount <> 0):
                self.receiveBufferData = []
                self.bufferSubheader = []
                self.lostPacketCount = 0
                self.sequenceReceive = 0
                
            # If we have not received a parity packet, do normal processing
            if self.subheaderTypeFlag <> 1:
                # bufferSubheader can be used in the future for packet reordering
                self.bufferSubheader.extend(dataIn[offset:offset+self.packetSubheaderSize])
                offset += self.packetSubheaderSize

                # Store data for future parity packet
                self.receiveBufferData.extend(dataIn[offset:offset+self.packetDataSize])
                #DEBUG print "data in", len(dataIn), "buffer length ", len(self.receiveBufferData), " lost count ", self.lostPacketCount
                    
                # Increment offset by packetDataSize
                offset += self.packetSize
            
                # If the flag has been set to reset the receive count, reset data
                if self.resetReceiveCount == 1:
                    self.resetReceiveCount = 0
                # Default, just increment the receive sequence
                else:
                    self.sequenceReceive += self.packetSize

            # Else If we received a parity packet and 1 packet was lost associated with parity packet
            elif self.subheaderTypeFlag == 1 and self.lostPacketCount == 1:
                #DEBUG print " buffersubheader size ", len(self.bufferSubheader)
                # Loop through all packets to determine the packet lost
                for index in range (0, sequenceNumber):
                    #DEBUG print " sub-header sequence ", self.bufferSubheader[index*self.packetSubheaderSize], " index ", (index + 1)
                    # If the sub-header buffer is 0 then we found the missing packet
                    if self.bufferSubheader[index*self.packetSubheaderSize] == 0:
                        # Perform parity calculation to recover lost packet
                        # Loop through data buffer and repopulate
                        for jndex in range (0, self.packetDataSize - 1):
                            # Create temporary storage
                            tempData = 0
                            kndex = 0

                            # Loop through all other packets at jndex and XOR the data
                            while kndex < sequenceNumber:
                                # Make sure not to XOR with missing packet 
                                if kndex <> index:
                                    #DEBUG if ((kndex*self.packetDataSize) + jndex) > len(self.receiveBufferData):
                                    #DEBUG     print " kndex ", kndex, " jndex ", jndex, " calc index ", ((kndex*self.packetDataSize) + jndex), " buff len ", len(self.receiveBufferData)
                                    tempData = (tempData ^ 
                                        self.receiveBufferData[(kndex*self.packetDataSize) + jndex])
                                # Increment kndex
                                kndex += 1
                            
                            # Lastly XOR the parity packet at jndex with temporary storage 
                            self.receiveBufferData[(index*self.packetDataSize) + jndex] = (
                                dataIn[self.packetHeaderSize+self.packetSubheaderSize+jndex] ^ tempData)
                                
                        # Break the index loop since the missing data packet was found
                        break
                
                # Reset flag
                self.resetReceiveCount = 1
            
            # Parity packet is unable to correct if multiple packets were lost during transmission
            elif self.subheaderTypeFlag == 1 and self.lostPacketCount > 1:
                # Reset flag
                self.resetReceiveCount = 1
            else:
                # Reset flag
                self.resetReceiveCount = 1
                
            #DEBUG print "self.sequenceReceive ", self.sequenceReceive, " dataIn length ", len(self.receiveBufferData), " subheader length ", len(self.bufferSubheader)
            if self.subheaderTypeFlag == 1:
                return self.receiveBufferData
            else:
                return empty[0:]