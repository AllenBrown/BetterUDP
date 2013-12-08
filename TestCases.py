__author__ = 'Alex Borg'

import unittest

from TestSendRecv import *
from SendRecv import SendRecvObj
from SendRecvUDP import SendRecvUDP
from SendRecvUDPwithParity import SendRecvUDPwithParity
from SendRecvRS import SendRecvRS

# unit test class to test send receive functions
# currently not checking values for returns, this is just a structure that
# allows easy calling of the TestSendRecvFunc with different objects
class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        print 'setting up'

    def tearDown(self):
        print 'tearing down'

    def test_basic(self):
        print 'starting test basic'
        testObj = SendRecvObj()
        #self.assertTrue(TestSendRecvFunc(testObj),"Failed first test")
        TestSendRecvFunc(testObj)
        pass

    def test_udp(self):
        print 'starting test UDP'
        testObj = SendRecvUDP()
        #self.assertTrue(TestSendRecvFunc(testObj),"Failed first test")
        TestSendRecvFunc(testObj)
        pass

    def test_udp_parity(self):
        print 'starting test UDP_with_Parity'
        testObj = SendRecvUDPwithParity()
        TestSendRecvFunc(testObj)
        pass

    def test_rs(self):
        print 'starting test Reed-Solomon encoding'
        testObj = SendRecvRS()
        TestSendRecvFunc(testObj)
        pass

if __name__ == '__main__':
    unittest.main()
