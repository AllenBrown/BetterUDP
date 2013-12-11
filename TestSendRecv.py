__author__ = 'Alex Borg'

import random
from SendRecv import *

# @Brief - floating point range
def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

# @Brief - drop a packet if random number is less than percentLoss
# return - bytes to send, number bytes actually lost in the network
def SimulateNetLoss(netData, percentLoss):
    if percentLoss > random.random():
        return bytearray(), len(netData)
    return netData, 0


# @Brief - drop packet if any datagram is lost
# calculate data loss for each 1480 bytes of data. If any of them are dropped,
# the whole packet is lost.
# @return - bytes to send, number bytes actually lost in the network
def SimulateNetIPDatagramLoss(netData, percentLoss):
    datagramSize = 1480
    offset = 0
    bytesLost = 0
    while offset < len(netData):
        if percentLoss > random.random():
            bytesLost += min(len(netData)-offset, datagramSize)
        offset += datagramSize
    if bytesLost > 0:
        return bytearray(), bytesLost
    return netData, bytesLost


# @Brief - simple comparison of input and output data arrays
# detects size differences and byte differences
# @return - 1 if the same, 0 if different
def CompareBytearrays(inputData, outputData):
    if len(inputData) != len(outputData):
        return 0
    i = 0
    #while i < len(inputData):
    #    if inputData[i] != outputData[i]:
    #        return 0
    #    i += 1
    return 1


# @Brief run a single test run.
# @param SendRecvInstance - a class derived from SendRecvObj
# @param inputData - the input data array that will be sent in it's entirety
# @param percentLoss - the percent data loss rate betwen 0.0 and 1.0
# @param blockSize - The size of chunks to be sent to the send function in each call
# @return - boolean no data lost, ratio of total bytes lost by system, ratio of bytes Lost in Network, ratio of efficiency
def testRun(SendRecvInstance, inputData, percentLoss, blockSize, networkLossFunc):
    outputData = bytearray()
    offset = 0
    totalBytesLost = 0
    totalBytesSent = 0
    while offset < len(inputData):
        sendData = inputData[offset:offset+blockSize]
        offset += blockSize
        netData = SendRecvInstance.send(sendData)

        for packet in netData:
            totalBytesSent += len(packet)
            recvPacket, bytesLost = networkLossFunc(packet,percentLoss)
            totalBytesLost += bytesLost
            recvData = SendRecvInstance.recv(recvPacket)
            outputData.extend(recvData)

    noDataLoss = CompareBytearrays(inputData, outputData)
    
    comparisonCount = 0
    maxIndex = len(inputData)
    if maxIndex > len(outputData):
        maxIndex = len(outputData)
    for index in range (0,maxIndex):
        if inputData[index] == outputData[index]:
            comparisonCount += 1
    #dataPercentLost = (len(inputData) - len(outputData)) / float(len(inputData))
    dataPercentLost = (len(inputData) - comparisonCount) / float(len(inputData))
    networkPercentLost = totalBytesLost / float(len(inputData))
    efficiency = len(inputData) / float(totalBytesSent)

    return noDataLoss, dataPercentLost, networkPercentLost, efficiency


# call from outside. Runs through multiple iterations of the actual test run with
# variable parameters
# FIXME: Possibly add multiple runs with the same parameters to collect statistics of each run
# FIXME: Possibly add output of data to a table to create charts
# FIXME: create variable test data to so byte comparison means something
def TestSendRecvFunc(SendRecvInstance):
    inputData = bytearray (100000)
    for index in range (0,len(inputData)):
        inputData[index] = 1
    numberTestRuns = 100
    for percentLoss in frange(0.0,0.1,0.01):
        for blockSize in range(10100, 65000, 10000):
            for x in [0,1]:
                if x == 0:
                    testSuccess, dataPercentLost, networkPercentLost, efficiency = testRun(SendRecvInstance, inputData, percentLoss, blockSize, SimulateNetLoss)
                    print "Jumbo Packet Data good=", testSuccess, ", blocksize=", blockSize, ", efficiency=", efficiency, ", total loss=", dataPercentLost, ", network loss=", networkPercentLost
                else:
                    testSuccess, dataPercentLost, networkPercentLost, efficiency = testRun(SendRecvInstance, inputData, percentLoss, blockSize, SimulateNetIPDatagramLoss)
                    print "Packetized Data good=", testSuccess, ", blocksize=", blockSize, ", efficiency=", efficiency, ", total loss=", dataPercentLost, ", network loss=", networkPercentLost
