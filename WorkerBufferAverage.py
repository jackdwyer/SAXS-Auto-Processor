 #!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012
"""

import zmq
from CommonLib import DatFile
import sys
import time
from threading import Thread
from CommonLib import LogLine
from CommonLib import TableBuilder


class WorkerBufferAverage():
    
    def __init__(self):
        self.allIntensities = []
        self.aveIntensities = []

    
    
    def run(self, datFile):
        self.allIntensities.append(datFile.intensities)
        value = 0.0
        
        #Loop across list and create averages
        aveIntensities = []
        for i in range(len(self.allIntensities[0])):
            for x in range(len(self.allIntensities)):
                value = self.allIntensities[x][i] + value
                value = (value/(len(self.allIntensities)))
                
            aveIntensities.insert(x, value)
        self.aveIntensities = aveIntensities
        print aveIntensities
            
        print "Average Buffer Generated"
  
    def getAve(self):
        return self.aveIntensities
    
    
    

def send_buffer_data(context, worker):
    bufferReply = context.socket(zmq.REP)
    bufferReply.bind("tcp://127.0.0.1:7883")
    
    try:
        while True:
            req = bufferReply.recv() #wait for request of buffer
            bufferReply.send_pyobj(worker.aveIntensities)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    worker = WorkerBufferAverage()
    
    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        worker.run("testDat/0p009_0166.dat")
    
    else:
        context = zmq.Context()

        buffers = context.socket(zmq.PULL)
        buffers.connect("tcp://127.0.0.1:7881")
        
        junk = Thread(target=send_buffer_data, args=(context, worker))
        junk.start()
        try:
            while True:
                datFile = buffers.recv_pyobj()
                worker.run(datFile)
                
        except KeyboardInterrupt:
            pass