import logging
import sys
sys.path.append("../")

import zmq
import time
from threading import Thread
from Worker import Worker
from Core import DatFile


from sqlalchemy import *


class WorkerDB(Worker):    
    def __init__(self):
        Worker.__init__(self, "WorkerDB")
        
        #Specific ZMQ stuff for WorkerDB, it uses SUB/PUB
        self.sub = self.context.socket(zmq.SUB)

        
    def processRequest(self, command, obj):                
        self.logger.info("Processing Received object")
        command = str(obj['command'])
        self.logger.info("Unknown Command - Did not process")
   
    def connect(self, pullPort = False, subPort = False):
        try:
            if (pullPort):
                self.pull.bind("tcp://127.0.0.1:"+str(pullPort))

            if (subPort):
                self.sub.bind("tcp://127.0.0.1:"+str(subPort))
                self.sub.setsockopt(zmq.SUBSCRIBE, "")
                
            self.logger.info("Connected Pull Port at: %(pullPort)s - Subscribed Port at: %(pubPort)s" % {'pullPort' : pullPort, 'pubPort' : subPort})
        
        except:  
            self.logger.critical("ZMQ Error - Unable to connect")
            raise Exception("ZMQ Error - Unable to connect")
        
        self.run()
    
    
    def setUser(self, user):
        self.user = str(user)
        self.logger.info("User set to %(user)s" % {'user':self.user})
        
        db = create_engine('sqlite:///tutorial.db')

        db.echo = False  # Try changing this to True and see what happens
        
        self.logger.info("Database created for user")

    
    
    
    
    
    
    
    
    
    
    
    
    def sub(self):
        try:
            while True:
                
                recievedObject = self.sub.recv_pyobj()
                self.logger.info("Received Object")
                try:
                    command = str(recievedObject['command'])
                except KeyError:
                    self.logger.error("No command key sent with object, can not process request")
                    continue
                
                #Default Commands            
                if (command == "update_user"):
                    self.clear()
                    super.setUser(recievedObject['user'])
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
        
    def close(self):
        try:
            time.sleep(0.1)
            self.sub.close()
            self.logger.info("Closed ports - shutting down")
        except:
            self.logger.critical("Failed to close ports")
            raise Exception("Failed to close ports")
        finally:
            sys.exit()
            
            
if __name__ == "__main__":
    #Test Cases
    context = zmq.Context()
    port = 1211
    
    worker = WorkerDB()
    print worker.getName()

    t = Thread(target=worker.connect, args=(port,))
    t.start()
    time.sleep(0.1)

    testPub = context.socket(zmq.PUB)
    testPub.connect("tcp://127.0.0.1:"+str(port))

    testPub.send_pyobj({'command' : "test"})
    testPub.send_pyobj({'command' : "shut_down"})