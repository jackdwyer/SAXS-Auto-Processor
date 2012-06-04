"""
Jack Dwyer
31-05-2012
Base Worker Class
"""


import zmq
import sys
sys.path.append("../")

import time

import logging


import time
from threading import Thread


class Worker():
    def __init__(self, name = "Default Worker"):
        #General Variables
        self.name = name
        


        
        
        #ZMQ stuff
        self.context = zmq.Context()
        self.pull = self.context.socket(zmq.PULL)
        self.pub = self.context.socket(zmq.PUB)
        
        
        #Class Variables
        self.logger = None
        
        #User Specific Variables (eg, user, their location relative to engine)
        self.user = None
        self.absoluteLocation = None
        
        
        
        #Setup logging 
        self.setLoggingDetails()
        


        
    def connect(self, pullPort = False, pubPort = False):
        try:
            if (pullPort):
                self.pull.bind("tcp://127.0.0.1:"+str(pullPort))

            if (pubPort):
                self.pub.connect("tcp://127.0.0.1:"+str(pubPort))
                
            self.logger.info("Connected Pull Port at: %(pullPort)s - Publish Port at: %(pubPort)s" % {'pullPort' : pullPort, 'pubPort' : pubPort})
        
        except:  
            self.logger.critical("ZMQ Error - Unable to connect")
            raise Exception("ZMQ Error - Unable to connect")
        
        self.run()


        
    
    def run(self):
        try:
            while True:
                
                recievedObject = self.pull.recv_pyobj()
                self.logger.info("Received Object")
                try:
                    command = str(recievedObject['command'])
                except KeyError:
                    self.logger.error("No command key sent with object, can not process request")
                    continue
                
                #Default Commands            
                if (command == "update_user"):
                    self.clear()
                    self.setUser(recievedObject['user'])
                    continue
                    
                if (command == "absolute_directory"):
                    self.setDirectory(receievedObject['absolute_directory'])
                    continue
                
                if (command == "clear"):
                    self.clear()
                    continue
                   
                if (command == "shut_down"):
                    break
               
                #Test commands
                if (command == "test"):
                     print "test command received"
                     continue
                 
                if (command == "test_receive"):
                    print recievedObject['test_receive']
                    continue
               
                else:
                   self.processRequest(command, recievedObject)      
                   continue
               
               
        except KeyboardInterrupt:
                pass
        
        self.close()
    
    
    #This must be overridden
    #It specifies how you want to process specific commands for workers   
    def processRequest(self, command, obj):
        raise Exception("Must override this method")
    
 
         
    #Generic Methods shared by all workers
    def setUser(self, user):
        self.user = str(user)
        self.logger.info("User set to %(user)s" % {'user':self.user})
                
    def setDirectory(self, directory):
        self.absoluteLocation = directory
        
    #This should be called from super class    
    def clear(self):
        self.logger.info("Cleared Details")
        self.user = None
        self.absoluteLocation = None 
        
    def close(self):
        try:
            time.sleep(0.1)
            self.pull.close()  
            self.logger.info("Closed ports")
        except:
            self.logger.critical("Failed to close ports")
            raise Exception("Failed to close ports")
        finally:
            sys.exit()
    
    #Generic method to publish data to the database worker
    def pubData(self, command):
        self.pub.send({'command':command})
    
    
    
    
    
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
    testPush.send_pyobj({'command' : "test"})
    
    testPush.send_pyobj({'command':"update_user", "user":"Tom"})


    #v = raw_input(">>")
    #testPush.send_pyobj({'command' : "test_receive", "test_receive" : v})
    testPush.send_pyobj({'command' : "shut_down"})
    
    
