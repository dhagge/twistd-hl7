'''
Logger for the hl7proxy

@author: damianhagge
'''
import sys
import logging
from logging.handlers import RotatingFileHandler

class LoggerManager(object):
    """
    Log manager that wraps the logging mechanism.
    Example:
    .. code-block:: python

        import main
        log = main.LoggerManager().get_log()
    """

    def __init__(self):
        self.log = logging.getLogger('proxy')
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(threadName)-10s %(levelname)-7s %(filename)s %(funcName)s [%(name)s] %(message)s")
        try:
            sys.stdout.write("Attempting to setup file logging for hl7proxy...\n")
            filehandler = RotatingFileHandler("/var/log/twistd/hl7proxy.log", maxBytes=2097152, backupCount=5)
            filehandler.setLevel(logging.DEBUG)
            filehandler.setFormatter(formatter)
            self.log.addHandler(filehandler)
            sys.stdout.write("Logging to file /var/log/twistd/hl7proxy.log")
        except:
            # fallback to stream logger
            streamhandler = logging.StreamHandler(sys.stdout)
            streamhandler.setLevel(logging.DEBUG)
            streamhandler.setFormatter(formatter)
            self.log.addHandler(streamhandler)
            self.log.info("Logging to stream instead of file for hl7proxy.\n")

    def get_log(self):
        return self.log

log = LoggerManager().get_log()
