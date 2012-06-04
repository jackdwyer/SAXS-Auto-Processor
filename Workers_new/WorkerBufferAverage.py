import logging
import sys
import zmq
import time
from threading import Thread
from Worker import Worker



class WorkerBufferAverage(Worker):    
    def __init__(self):
        Worker.__init__(self, "Worker Static Image")
        
        #Specific Class Variables
        self.averagedBuffer = None
        
        
    def processRequest(self, command, obj):                
        self.logger.info("Processing Received object")
        command = str(obj['command'])
        
        if (command == "static_image"):
            self.logger.info("Received a static image")
        
        if (command == "averaged_buffer"):
            self.logger.info("Received an averaged buffer")
            


    

        

if __name__ == "__main__":
    #Test Cases
    context = zmq.Context()
    port = 1200
    
    worker = WorkerStaticImage()

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