__author__ = 'Alex Borg'

import random
from SendRecv import *

# @Brief - floating point range
def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

# @Brief - drop a packet if random number is less than percentLoss
def SimulateNetLoss(netData, percentLoss):
    if percentLoss > random.random():
        netData = bytearray()
    return netData


# @Brief - simple comparison of input and output data arrays
# detects size differences and byte differences
# @return - 1 if the same, 0 if different
def CompareBytearrays(inputData, outputData):
    if len(inputData) != len(outputData):
        return 0
    i = 0
    while i < len(inputData):
        if inputData[i] != outputData[i]:
            return 0
        i += 1
    return 1


# @Brief run a single test run.
# @param SendRecvInstance - a class derived from SendRecvObj
# @param inputData - the input data array that will be sent in it's entirety
# @param percentLoss - the percent data loss rate betwen 0.0 and 1.0
# @param blockSize - The size of chunks to be sent to the send function in each call
# FIXME: add return stats for total bytes sent over the network and % lost
def testRun(SendRecvInstance, inputData, percentLoss, blockSize):
    outputData = bytearray()
    offset = 0
    while offset < len(inputData):
        sendData = inputData[offset:offset+blockSize]
        offset += blockSize
        netData = SendRecvInstance.send(sendData)

        for packet in netData:
            recvPacket = SimulateNetLoss(packet,percentLoss)
            recvData = SendRecvInstance.recv(recvPacket)
            outputData.extend(recvData)

    return CompareBytearrays(inputData, outputData)


# call from outside. Runs through multiple iterations of the actual test run with
# variable parameters
# FIXME: add multiple runs with the same parameters to collect statistics of each run
def TestSendRecvFunc(SendRecvInstance):
    inputData = bytearray (1000000)
    numberTestRuns = 100
    for percentLoss in frange(0.0,0.9,0.1):
        for blockSize in range(100, 65000, 10000):
            testSuccess = testRun(SendRecvInstance, inputData, percentLoss, blockSize)
            if testSuccess:
                print "Succeed in blocksize = " , blockSize , ", with loss of " , percentLoss , "%"
            else:
                print "Failed in blocksize = " , blockSize , ", with loss of " , percentLoss , "%"


