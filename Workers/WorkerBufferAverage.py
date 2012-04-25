"""
Jack Dwyer
24 April 2012
refactored WorkerBufferAverage
"""

import sys
import time
from threading import Thread
sys.path.append("../")
import zmq
from Core import AverageList
from Core.Logger import log
from Core import DatFile

from Worker import Worker

class WorkerBufferAverage(Worker):
    def __init__(self):
        Worker.__init__(self, "WorkerStaticImage")
        self.allIntensities = []
        self.aveIntensities = []
        
        self.addToClearList(self.allIntensities)
    
    
    def process(self, filter):
        if (filter == "buffer"):
            datFile = buffers.recv_pyobj()
            self.allIntensities.append(datFile.intensities)
            #only averages out all intensities
            self.aveBuffer = self.ave.average(self.allIntensities)
            log(self.name, "Average Buffer Generated")
            
    
    #Need to override the run method, as we only want the buffer to clear if there is a new buffer
    def run(self):
        if (self.reply != False):
            replyThread = Thread(target=self.sendData)
            replyThread.start()
        try:
            while True:
                filter = self.pull.recv()
                if (filter == 'newBuffer'):
                    self.clear()
                else:
                    self.process(filter)
                
        except KeyboardInterrupt:
            pass
        



if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False

    print "TEST 1 - ONLY PUSH/PULL"
    #Test 1 - Only a pull socket
    b = WorkerBufferAverage()
    t = Thread(target=b.connect, args=(pushPort, False))
    t.start()

    
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("clear")
    time.sleep(0.1)
    testPush.close()


    #Test 2
    print "TEST 2 - ONLY REQ/RECV"
    b = WorkerBufferAverage()
    t = Thread(target=b.connect, args=(pushPort, reqPort))
    t.start()
    
    testReq = context.socket(zmq.REQ)
    testReq.connect("tcp://127.0.0.1:"+str(reqPort))
    testReq.send("testReply")
    testReply = testReq.recv_pyobj()
    
    if (testReply == "testReply"):
        replyPass = True

    testReq.close()
    
    if (replyPass):
        print "TEST OVER - Succeeded"
    else:
        print "TEST OVER - Failed with reply"     
