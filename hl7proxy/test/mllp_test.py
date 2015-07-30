'''
Tests for the proxy mllp factory/protocol/handler

@author: damianhagge
'''
from nose.tools import eq_
import hl7

from twisted.internet import defer
from hl7proxy.ack import ACK
from hl7proxy.mllp import IHL7Receiver, MinimalLowerLayerProtocol, MLLPFactory
from zope.interface import implements


EXPECTED_ACK = 'MSH|^~\\&|GHH OE|BLDG4|GHH LAB|ELAB-3|{0}|ACK|CNTRL-3456|P|2.4\rMSA|{1}|CNTRL-3456'
HL7_MESSAGE = 'MSH|^~\\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\rPID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\rOBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\rBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F'

class TestReceiver(object):
    implements(IHL7Receiver)

    def __init__(self, network_id):
        self.messages = []
        self.ack_code = 'AA'

    def handleMessage(self, message):
        self.messages.append(message)
        return defer.succeed(ACK(message, self.ack_code))

    def getCodec(self):
        return 'utf-8'

class MockTransport():
    def write(self, msg):
        self.msg = msg

class TestMinimalLowerLayerProtocol():
    def setup(self):
        self.receiver = TestReceiver(1)
        self.protocol = MinimalLowerLayerProtocol()
        self.protocol.factory = MLLPFactory(self.receiver)
        self.protocol.transport = MockTransport()

    def test_parse_message(self):
        self.protocol.dataReceived('\x0b' + HL7_MESSAGE + '\x1c\x0d')
        eq_(self.receiver.messages, [HL7_MESSAGE])
        eq_(self.protocol.transport.msg, '\x0b' + EXPECTED_ACK.format(self._get_msg_datetime(), 'AA') + '\x1c\x0d')

    def test_uncaught_error(self):
        'throw a random exception, make sure Errback is used'
        def raise_exception():
            raise Exception
        self.receiver.handleMessage = raise_exception
        self.protocol.dataReceived('\x0b' + HL7_MESSAGE + '\x1c\x0d')
        eq_(self.protocol.transport.msg, '\x0b' + EXPECTED_ACK.format(self._get_msg_datetime(), 'AR') + '\x1c\x0d')

    def test_parse_message_unicode(self):
        message = HL7_MESSAGE.replace('BLDG4', 'x\x82y')
        self.protocol.dataReceived('\x0b' + message + '\x1c\x0d')

        expected_message = unicode(HL7_MESSAGE).replace(u'BLDG4', u'xy')
        eq_(self.receiver.messages, [expected_message])

        expected_ack = EXPECTED_ACK.replace('BLDG4', 'xy')
        eq_(self.protocol.transport.msg, '\x0b' + expected_ack.format(self._get_msg_datetime(), 'AA') + '\x1c\x0d')

    def _get_msg_datetime(self):
        msg = hl7.parse(self.protocol.transport.msg)
        return unicode(msg.segment('MSH')[6])

class DummyObject(object):
    def __init__(self, props):
        for propKey in props.keys():
            setattr(self, propKey, props[propKey])