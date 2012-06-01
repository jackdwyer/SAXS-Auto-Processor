"""
Jack Dwyer
31-05-2012
Base Worker Class
"""


import zmq
import sys
import time

import logging

sys.path.append("../")

import time
from threading import Thread


class Worker():
    def __init__(self, name = "Default Worker"):
        #General Variables
        self.name = name

        
        
        #ZMQ stuff
        self.context = zmq.Context()
        self.pull = self.context.socket(zmq.PULL)
        
        
        #Class Variables
        self.logger = None
        self.pullPort = None
        #User Specific Variables (eg, user, their location relative to engine)
        
        self.setLoggingDetails()

        
    def connect(self, pullPort):
        self.pull.bind("tcp://127.0.0.1:"+str(pullPort))
        self.logger.info("Connected at Port %(pullPort)s" % {'pullPort' : pullPort})
        
        self.run()
        
    
    def close(self):
        try:
            time.sleep(0.1)
            self.pull.close()  
            self.logger.info("Closed port")
        except:
            self.logger.critical("Failed to close port")
            raise StandardError("Failed to close port")
        
    
    def run(self):
        try:
            while True:
                recievedObject = self.pull.recv_pyobj()
                self.logger.info("Received Object")
                command = recievedObject['command']

                #Default Commands            

                    
                if (command == "update_user"):
                    self.user = receivedObject['user']
                    
                    
                if (command == "test"):
                     print "test command received"
                     
                if (command == "test_receive"):
                    print recievedObject['test_receive']
                     
                if (command == "shut_down"):
                    break
                     
                     
        except KeyboardInterrupt:
                pass
        
        self.close()
            
    
    
    ###Logging Setup
    def setLoggingDetails(self):
        LOG_FILENAME = 'logs/'+self.name+'.log'
        FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format=FORMAT)
        
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger(self.name).addHandler(console)
        
        self.logger = logging.getLogger(self.name)
        self.logger.info("\nLOGGING STARTED")
        
        
if __name__ == "__main__":
    #Test Cases
    context = zmq.Context()
    port = 1200
    
    worker = Worker()

    t = Thread(target=worker.connect, args=(port,))
    t.start()
    time.sleep(0.1)

    
    testPush = context.socket(zmq.PUSH)
    testPush.connect("tcp://127.0.0.1:"+str(port))
    print "sent command"
    testPush.send_pyobj({'command' : "test"})
    v = raw_input(">>")
    testPush.send_pyobj({'command' : "test_receive", "test_receive" : v})
    testPush.send_pyobj({'command' : "shut_down"})
    
    
