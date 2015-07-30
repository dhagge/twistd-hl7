'''
Handler for the actual processing of an HL7 message

@author: damianhagge
'''

import urllib2
from mllp import IHL7Receiver
from zope.interface import implements
from logger import log

class HL7Receiver():

    implements(IHL7Receiver)

    def __init__(self, http_uri, accept_header):
        self.http_uri = http_uri
        self.accept_header = accept_header
        log.debug('Running with http URI %s and accept header %s' % (http_uri, accept_header));

    def handleMessage(self, message):
        log.debug('Receiver handling message: %s' % message)

        resp = None
        try:
            headers = {}
            if self.accept_header is not None:
                header['Accept'] = accept_header
            req = urllib2.Request(http_uri, message, headers)
            opener = urllib2.build_opener(MethodRespectingRedirectHandler())
            log.debug('Opening %s' % http_uri)
            resp = opener.open(req)
            data = resp.read()
            return data
        except:
            log.exception('Error in hl7receiver')
            raise
        finally:
            if resp != None:
                resp.close()

    def getCodec(self):
        return 'utf-8'

class MethodRespectingRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """
        Handles redirects by making the same request method to any redirect locations.

        urllib2.HTTPRedirectHandler follows the HTTP standard and converts any redirect into a GET.
        """
        m = req.get_method()
        if (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m == "POST"):

            newurl = newurl.replace(' ', '%20')
            newheaders = dict((k,v) for k,v in req.headers.items()
                              if k.lower() not in ("content-length", "content-type")
                             )
            return urllib2.Request(newurl,
                                   req.get_data(),
                                   headers=newheaders,
                                   origin_req_host=req.get_origin_req_host(),
                                   unverifiable=True)
        else:
            raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)