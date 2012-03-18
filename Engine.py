#!/usr/bin/env python2.7
"""
Jack Dwyer
18 March 2012

Engine for the SAXS/WAXS Auto Processor
"""

import epics
import time
import zmq
from CommonLib import LogLine

class Engine():
    def __init__(self):
        
        
        #ZeroMQ setup stuff
        self.context = zmq.Context()
        self.buffers = self.context.socket(zmq.PUSH)
        self.buffers.bind("tcp://*:7881")  
        self.sample = self.context.socket(zmq.PUSH)
        self.sample.bind("tcp://*:7882")
    
        #Make sure all sockets are created
        time.sleep(1.0)
    
    def epicPVChange(self, value, **kw ):
        """Check Logline, get all details on latest image """
        if value == 100:

                         
    def run(self, user):
        self.user = user
        self.buildTable()
        
        
        epics.camonitor("13SIM1:cam1:NumImages_RBV", callback=self.epicPVChange)
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    

if __name__ == "__main__":
    engine = Engine()
    user = raw_input("ENTER USER >>")
    engine.run(user)
