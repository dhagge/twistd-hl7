'''
TCP proxy that accepts HL7 messages on a port and proxies them to the http handler

This file can be run as a python program or directly (as a twistd daemon) with:
    twistd -y /location_to_source/src/hl7proxy/main.py --logfile=/var/log/twistd/twistd.log --pidfile=/var/run/twistd/twistd.pid
or, if setup as a daemon (/etc/init.d/hl7proxy):
    sudo service hl7proxy [start|stop|restart]

Note: this version will not auto-reload, so if you change the hl7proxy code the service must be manually restarted

Can be manually tested with the command (requires hl7 package):
    mllp_send --file path/to/project/test/data/hl7_activity_order --port 8181 --loose localhost

@author: damianhagge
'''

import os, json, sys
import logger

from mllp import MLLPFactory
from hl7_receiver import HL7Receiver
from logger import log
from twisted.application import service, internet
from twisted.python import usage

class Options(usage.Options):
    '''
    Note: These options are currently http only but could be enhanced with:
        - Auth header for each http call
        - a socket to send messages to (rather than an http call)
        - specify some python code to be called to handle the HL7 message (instead of an http call)
        - etc...

    Example:
        python main.py -p 8111 -h http://localhost:8080/hl7/handler -a application/vnd.com.restful.service.emr.v1+json
    '''
    optParameters = [
        ["port", "p", 8181, "The port to bind to (defaults to 8181)", int],
        ["httpUri", "h", None, "An http URI to which each individual HL7 message will be sent (as a seperate http POST call for each message)"],
        ["acceptHeader", "a", None, "The accept (content type) header that will be sent with each http call"]
    ]

config = Options()
try:
    config.parseOptions() # When given no argument, parses sys.argv[1:]
except usage.UsageError, errortext:
    print '%s: %s' % (sys.argv[0], errortext)
    print '%s: Try --help for usage details.' % (sys.argv[0])
    sys.exit(1)

if config['httpUri'] is None:
    print 'An httpUri parameter must be specified in order to run hl7proxy'
    print '%s: Try --help for usage details.' % (sys.argv[0])
    sys.exit(1)

receiver = HL7Receiver(config['httpUri'], config['acceptHeader'])
mllp_factory = MLLPFactory(receiver)

log.info('Proxy is listening on on port %s' % config['port'])

if __name__=='__main__':
    '''running as a python app'''
    from twisted.internet import reactor
    reactor.listenTCP(config['port'], mllp_factory)
    reactor.run()
else:
    '''running as a twistd daemon'''
    application = service.Application("hl7proxy")
    internet.TCPServer(config['port'], mllp_factory).setServiceParent(application)
