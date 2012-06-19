"""
Jack Dwyer
"""

import logging
import sys
import zmq
import time
from threading import Thread
from Worker import Worker
from Core import AverageList
from Core import DatFile
from Core import DatFileWriter



class WorkerBufferAverage(Worker):    
    def __init__(self):
        Worker.__init__(self, "Worker Buffer Average")
        
        #Specific Class Variables
        self.averagedBuffer = None
        self.bufferIndex = 1
        self.buffers = []
        self.averagedIntensities = None
        
        self.previousName = None
        
        
        #specific ZMQ 
        self.context = zmq.Context()
        self.reply = self.context.socket(zmq.REP)

    
    def connect(self, pullPort = False, pubPort = False, replyPort = False):
        try:
            if (pullPort):
                self.pull.bind("tcp://127.0.0.1:"+str(pullPort))

            if (pubPort):
                self.pub.connect("tcp://127.0.0.1:"+str(pubPort))
            
            if (replyPort):
                self.reply.bind("tcp://127.0.0.1:"+str(replyPort))
                
                replyThread = Thread(target=self.requestBufferThread)
                replyThread.setDaemon(True)
                replyThread.start()
                
                
            self.logger.info("Connected Pull Port at: %(pullPort)s - Publish Port at: %(pubPort)s - Reply Port at: %(replyPort)s" % {'pullPort' : pullPort, 'pubPort' : pubPort, 'replyPort':replyPort})
        
        except:  
            self.logger.critical("ZMQ Error - Unable to connect")
            raise Exception("ZMQ Error - Unable to connect")
        
        self.run()

    
        
    def processRequest(self, command, obj):                
        self.logger.info("Processing Received object")
        command = str(obj['command'])
        
        if (command == "buffer"):
            buffer = obj['buffer']
            self.logger.info("Buffer Sample")
            self.averageBuffer(buffer)
            
            
            
    def averageBuffer(self, buffer):
        self.buffers.append(buffer)
        intensities = []
        for buffer in self.buffers:
            intensities.append(buffer.getIntensities())
            
        datName = "avg_buffer_" + str(self.bufferIndex) + "_" +buffer.getBaseFileName()
        self.averagedIntensities = self.averageList.average(intensities)
        
        self.datWriter.writeFile(self.absoluteLocation + "/avg/", datName, { 'q' : self.buffers[-1].getq(), "i" : self.averagedIntensities, 'errors':self.buffers[-1].getErrors()})
        
        if not (self.previousName == datName):
            self.pub.send_pyobj({"command":"averaged_buffer", "location":datName})
            self.previousName = datName



    
    def requestBufferThread(self):
        try:
            while True:
                test = self.reply.recv() #wait for request of buffer
                if (test == 'test'):
                    self.reply.send_pyobj("REQUESTED DATA")
                if (test == "request_buffer"):
                    if (self.averagedIntensities):
                        self.reply.send_pyobj(self.averagedIntensities)      
                    else:
                        self.reply.send_pyobj(False)
        except KeyboardInterrupt:
            pass   




    def rootNameChange(self):
        self.logger.info("Root Name Change Called - No Action Required")

    def newBuffer(self):
        self.averagedBuffer = None
        self.bufferIndex = self.bufferIndex + 1
    
    def clear(self):
        Worker.clear(self)
        self.averagedBuffer = None
        self.bufferIndex = 1
        self.buffers = []

        

if __name__ == "__main__":
    #Test Cases
    context = zmq.Context()
    port = 1200
    
    worker = WorkerBufferAverage()

    t = Thread(target=worker.connect, args=(port,))
    t.start()
    time.sleep(0.1)

    
    testPush = context.socket(zmq.PUSH)
    testPush.connect("tcp://127.0.0.1:"+str(port))
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "static_image"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "static_image"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "shut_down"})