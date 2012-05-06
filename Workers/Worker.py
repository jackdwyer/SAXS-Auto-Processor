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
        

        
        #need this to be able to save data etc
        self.user = ""
        self.experiment = ""
        self.absolutePath = ""
        
        self.aveBuffer = []
        self.needBuffer = True
        
        #Set so that a reply socket is not always started
        self.reqBuffer = False        
        #ZMQ stuff
        self.context = zmq.Context()
        self.pull = self.context.socket(zmq.PULL)
        
        #for requesting Buffer
        #self.reqBuffer = self.context.socket(zmq.REQ)
        
        
        #DatFile writer
        self.datWriter = DatFileWriter.DatFileWriter()
        #Averager
        self.ave = AverageList.AverageList()



        self.dataList = []     
        log(self.name, "Generated")
        
        
    def setName(self, name):
        self.name = name
    
    def updateDetails(self, user, experiment, absolutePath):
        self.user = user
        self.experiment = experiment
        self.absolutePath = absolutePath
        
    #Overriden by Buffer Average
    def connect(self, pullPort):
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort));
        log(self.name, "All Ports Connected -> pullPort: "+str(pullPort))
        self.run()

    
      
      
      
      
    def addToClearList(self, dataList):
        """Slap all lists in here to be cleared when needed"""
        self.dataList.append(dataList)
        

    
    def clear(self):
        #Clear all lists TODO dictionaries/variables
        for i in range(len(self.dataList)):
            self.dataList[i] = []
        self.needBuffer = True
        print self.dataList
        log(self.name, "Cleared")
       
       
        
        
    def process(self, filter):    
        raise Exception("You must override this method!")
  


    
    def test(self):
        log(self.name, "Test Method Preformed") 
        

            

    
    #Overridden in WorkerBufferAverage
    def run(self):
        #if (self.reqBuffer != False):
            #replyThread = Thread(target=self.sendData)
            #replyThread.start()
        try:
            while True:
                filter = self.pull.recv()
                
                if (str(filter) == "updateUser"):
                    log(self.name, "Received Command - updateUser")
                    self.user = self.pull.recv()
                    log(self.name, "New User -> " + self.user)
                
                if (str(filter) == "getUser"):
                    log(self.name, "Current User : " + self.user)
                
                if (str(filter) == "testPush"):
                    testString = self.pull.recv();
                    log(self.name, "Test Pull/Push - Completed - String Received : " + testString)
                    
                if (str(filter) == "static_image"):
                    log(self.name, "Static Image - Received")
                
                if (str(filter) == "exit"):
                    self.close()
                
                if (filter == 'clear'):
                    self.clear()
                else:
                    self.process(filter)
                
        except KeyboardInterrupt:
            pass
        
    
    #OVERRIDE IN BUFFER
    def close(self):
        """Close all zmq sockets"""
        #time.sleep(0.1)
        self.pull.close()        
        log(self.name, "Closed")
        sys.exit()
                
         
if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False

    print "TEST 1 - ONLY PUSH/PULL"
    #Test 1 - Only a pull socket
    b = Worker("Worker (Sub)")
    t = Thread(target=b.connect, args=(pushPort,))
    t.start()

    
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("clear")
    time.sleep(0.1)
    testPush.close()
    b.close()


    #Test 2
    print "TEST 2 - ONLY REQ/RECV"
    b = Worker("Worker")
    t = Thread(target=b.connect, args=(pushPort,))
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
        
    sys.exit()
