__author__ = 'Alex Borg'

import unittest

from TestSendRecv import *
from SendRecv import SendRecvObj
from SendRecvUDP import SendRecvUDP

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


if __name__ == '__main__':
    unittest.main()
