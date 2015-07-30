'''
End-to-end tests for twisted launched as TCP listener

@author: damianhagge
'''
import os

from nose.tools import ok_
from nose.twistedtools import reactor, deferred

from twisted.internet import defer
from twisted.internet.protocol import ClientFactory, Protocol

from hl7proxy.mllp import MLLPFactory
from hl7proxy.mllp import MinimalLowerLayerProtocol as mllp
from mllp_test import TestReceiver

class TestMainTwistedDemon():
    def setup(self):
        self.receiver = TestReceiver(1)
        self.mllp_factory = MLLPFactory(self.receiver)
        self.port = reactor.listenTCP(0, self.mllp_factory, interface="127.0.0.1")
        self.portnum = self.port.getHost().port

    def teardown(self):
        self.port.stopListening()

    @deferred(timeout=10.0)
    def test_one(self):
        message = self._get_hl7_msg('hl7_activity_order')
        # wrap message MLLP message container
        message = mllp.start_block + message + mllp.end_block + mllp.carriage_return

        d_resp = defer.Deferred()

        def handle_response(msg, protocol):
            ok_(msg.startswith(mllp.start_block + 'MSH|^~\\&|||LAB|HNA|'), 'check message start')
            ending = mllp.end_block + mllp.carriage_return + '|ACK|Q160749835T204717222||2.3\rMSA|AA|Q160749835T204717222\rMSA|AA|Q160749835T204717222'
            msg.endswith(ending)
            d_resp.callback(True)
            self.port.stopListening() # ends the test

        send_msg('localhost', self.portnum, message, handle_response)
        return d_resp

    def _get_hl7_msg(self, file_name):
        fn = os.path.join(os.path.dirname(__file__) + '/data', file_name)
        with open(fn,'r') as f:
            return f.read()

class TestClientProtocol(Protocol):

    callback = None

    def connectionMade(self):
        self.transport.write(self.req_msg)

    def dataReceived(self, data):
        self.callback(data, self)

class TestClientFactory(ClientFactory):

    protocol = TestClientProtocol

    def __init__(self, req_msg, msg_handler):
        self.req_msg = req_msg
        self.msg_handler = msg_handler

    def buildProtocol(self, address):
        proto = ClientFactory.buildProtocol(self, address)
        proto.req_msg = self.req_msg
        proto.callback = self.msg_handler
        return proto

def send_msg(host, port, msg, callback):
    factory = TestClientFactory(msg, callback)
    reactor.connectTCP(host, port, factory)