"""
Jack Dwyer
12/04/2012
Will be super class for all workers

Will also be abstract/interface for what methods need to be overridden etc
"""



import zmq
import sys
sys.path.append("../")

import time
from threading import Thread

from Core.Logger import log
from Core import DatFileWriter
from Core import AverageList


class Worker():
    def __init__(self, name):
        self.name = name
        
        self.aveIntensities = []
        self.aveQ = []
        self.aveErrors = []
        
        #need this to be able to save data etc
        self.user = ""
        self.experiment = ""
        self.absolutePath = ""
        
        self.aveBuffer = []
        self.needBuffer = True
        
        #Set so that a reply socket is not always started
        self.reply = False        
        #ZMQ stuff
        self.context = zmq.Context()
        self.pull = self.context.socket(zmq.PULL)
        #for requesting Buffer
        self.reqBuffer = self.context.socket(zmq.REQ)
        
        
        #DatFile writer
        self.datWriter = DatFileWriter.DatFileWriter()
        #Averager
        self.ave = AverageList.AverageList()



        self.dataList = [self.aveBuffer, self.aveIntensities, self.aveQ,  self.aveErrorsa
                         ]        
        log(self.name, "Generated")
        
        
    def setName(self, name):
        self.name = name
    
    def updateDetails(self, user, experiment, absolutePath):
        self.user = user
        self.experiment = experiment
        self.absolutePath = absolutePath
        
    
    def connect(self, pullPort, replyPort = False):
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort));
        
        if (replyPort != False):
            self.reply = self.context.socket(zmq.REP)
            self.reply.bind("tcp://127.0.0.1:"+str(replyPort))
            log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: "+str(replyPort))
        else:
            log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: INACTIVE")
        self.run()


    def setBufferRequest(self, port):
        self.reqBuffer.connect("tcp://127.0.0.1"+str(port))

    def addToClearList(self, data):
        """Slap all lists in here to be cleared when needed"""
        self.dataList.append(data)
        

    
    def clear(self):
        #Clear all lists TODO dictionaries/variables
        for i in range(len(self.dataList)):
            self.dataList[i] = []
        self.needBuffer = True
        print self.dataList
        log(self.name, "Cleared")
        
        
    def process(self, filter):    
        #raise Exception("You must override this method!")

        if (str(filter) == "testPush"):
            log(self.name, "Test Pull/Push - Completed")

    
            
            
    def sendData(self):
        try:
            while True:
                req = self.reply.recv() #wait for request of buffer
                if (req == "buffer"):
                    self.reply.send_pyobj(self.aveBuffer)
                    
                #Test    
                if (req == "testReply"):
                    self.reply.send_pyobj(req)
                    log(self.name, "Test Req/Rep - Completed")

        except KeyboardInterrupt:
            pass   

    
    
    def run(self):
        if (self.reply != False):
            replyThread = Thread(target=self.sendData)
            replyThread.start()
        try:
            while True:
                filter = self.pull.recv()
                if (filter == 'clear'):
                    self.clear()
                else:
                    self.process(filter)
                
        except KeyboardInterrupt:
            pass
        
    
    def close(self):
        """Close all zmq sockets"""
        self.pull.close()
        try:
            self.reply.close()
        except KeyboardInterrupt:
            pass 
                
         
if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False

    print "TEST 1 - ONLY PUSH/PULL"
    #Test 1 - Only a pull socket
    b = Worker("Worker (Sub)")
    t = Thread(target=b.connect, args=(pushPort, False))
    t.start()

    
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("clear")
    time.sleep(0.1)
    testPush.close()
    b.close()


    #Test 2
    print "TEST 2 - ONLY REQ/RECV"
    b = Worker("Worker (Sub)")
    t = Thread(target=b.connect, args=(pushPort, reqPort))
    t.start()
    
    testReq = context.socket(zmq.REQ)
    testReq.connect("tcp://127.0.0.1:"+str(reqPort))
    testReq.send("testReply")
    testReply = testReq.recv_pyobj()
    
    if (testReply == "testReply"):
        replyPass = True

    testReq.close()
    b.close()
    
    if (replyPass):
        print "TEST OVER - Succeeded"
    else:
        print "TEST OVER - Failed with reply"

    
    
    
    
    
    