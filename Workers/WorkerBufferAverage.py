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
        Worker.__init__(self, "WorkerBufferAverage")
        self.allIntensities = []
        self.allErrors = []
        self.allQ = []
        
        self.avIntensities = []
        self.avErrors = []
        self.avQ = []
        
        #self.addToClearList(self.allIntensities, self.allErrors, self.allQ)
        self.reply = self.context.socket(zmq.REP)

        #self.sendDataThread = Thread(target=self.sendData())
        
        self.bufferIndex = 0

    
    def process(self, test):       
        if (test == "test"):
            log(self.name, "RECIEVED - 'test' message")
            
            
            
        if (test == "buffer"):
            buffer = self.pull.recv_pyobj()
            log(self.name, "RECIEVED - Buffer")
            self.average(buffer)
            
    def newBuffer(self):
        self.bufferIndex = self.bufferIndex + 1
        self.allIntensities = []
        self.allErrors = []
        self.allQ = []
        self.avIntensities = []
        self.avErrors = []
        self.avQ = []
        
    def clear(self):
        self.bufferIndex = 0
        self.allIntensities = []
        self.allErrors = []
        self.allQ = []
        self.avIntensities = []
        self.avErrors = []
        self.avQ = []
            
    
    def average(self, datBuffer):
        self.allIntensities.append(datBuffer.intensities)
        self.allErrors.append(datBuffer.errors)
        self.allQ.append(datBuffer.q)


        #averaging out
        self.avIntensities = self.ave.average(self.allIntensities)
        self.avErrors = self.ave.average(self.allErrors)
        self.avQ = self.ave.average(self.allQ)
        
        self.datWriter.writeFile(self.absoluteLocation+"/avg/", "buffer" + str(self.bufferIndex) + "_" + "avg_" + datBuffer.getBaseFileName(), { 'q': self.avQ, 'i' : self.avIntensities, 'errors':self.avErrors})

        log(self.name, "Averaging Completed")


            
    def connect(self, pullPort, replyPort):
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort))
        self.reply.bind("tcp://127.0.0.1:"+str(replyPort))
        log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: "+str(replyPort))
        
        replyThread = Thread(target=self.sendData)
        replyThread.setDaemon(True)
        replyThread.start()

        self.run()


    def getAverageBuffer(self):
        return {'intensities' : self.avIntensities, 'errors' : self.avErrors, 'q' : self.avQ}
    
    
    def sendData(self):
        try:
            while True:
                test = self.reply.recv() #wait for request of buffer
                if (test == 'test'):
                    self.reply.send_pyobj("REQUESTED DATA")
                if (test == "request_buffer"):
                    log(self.name, "BufferRequested")
                    self.reply.send_pyobj(self.getAverageBuffer())
                    

        

        except KeyboardInterrupt:
            pass   
        
        #OVERRIDE IN BUFFER
    def close(self):
        """Close all zmq sockets"""
        self.pull.close()
        self.reply.close()
        log(self.name, "Sockets Closed")
        sys.exit()
        



if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False




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
