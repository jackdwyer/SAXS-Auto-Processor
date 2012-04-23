"""
Jack Dwyer
12/04/2012
Will be super class for all workers

Will also be abstract/interface for what methods need to be overridden etc
"""



import zmq
import sys
import time
from threading import Thread

from CommonLib.Logger import log
class Worker():
    def __init__(self, name):
        self.name = name
        self.dataList = []
        self.replyData = []
        
        self.reply = False
                
        #ZMQ stuff
        self.context = zmq.Context()
        self.pull = self.context.socket(zmq.PULL)
        
        log(self.name, "Generated")
        
        
    def connect(self, pullPort, replyPort = False):
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort));
        
        if (replyPort != False):
            self.reply = self.context.socket(zmq.REP)
            self.reply.connect("tcp://127.0.0.1:"+str(replyPort))
            log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: "+str(replyPort))
        else:
            log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: INACTIVE")
        self.run()



    def addToDataList(self, data):
        self.dataList.append(data)
        

    
    def clear(self):
        #Clear all lists TODO dictionaries/variables
        for i in range(len(self.dataList)):
            self.dataList[i] = []
        print self.dataList
        
    def doWork(self, filter):                
        if (str(filter) == "clear"):
            self.clear()
            
        #Test    
        if (str(filter) == "testPush"):
            log(self.name, "TestPull/Push - Completed")
            
    def sendData(self):
        try:
            while True:
                req = self.reply.recv() #wait for request of buffer
                if (req == "buffer"):
                    self.reply.send_pyobj(self.replyData)
                    
                #Test    
                if (req == "testReply"):
                    self.reply.send_pyobj(req)
        except KeyboardInterrupt:
            pass   

    
    
    def run(self):
        if (self.reply != False):
            replyThread = Thread(target=self.sendData)
            replyThread.start()
        try:
            while True:
                filter = self.pull.recv()
                self.doWork(filter)
                
        except KeyboardInterrupt:
            pass
                
         
if __name__ == "__main__":
    pushPort = 4000
    reqPort = 4001
    context = zmq.Context()
    replyPass = False

    
    #Test 1 - Only a pull socket
    b = Worker("Worker")
    t = Thread(target=b.connect, args=(pushPort, False))
    t.start()
    time.sleep(1)
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("testPush")
    testPush.close()
    
    #Test 2
    b = Worker("Worker")
    t = Thread(target=b.connect, args=(pushPort, reqPort))
    t.start()
    time.sleep(0.5)
    
    testReq = context.socket(zmq.REQ)
    testReq.bind("tcp://127.0.0.1:"+str(reqPort))
    testReq.send("testReply")
    testReply = testReq.recv_pyobj()
    
    if (testReply == "testReply"):
        replyPass = True

    testReq.close()
    
    if (replyPass):
        print "TEST OVER - Succeeded"
    else:
        print "TEST OVER - Failed with reply"

    
    
    
    
    
    