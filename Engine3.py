"""
Jack Dwyer
26/04/2012

Engine v0.3
- Loads all default workes

"""



import yaml
import epics
import time
import zmq
import sys
from Core import DatFile
from Core import LogLine
from Core.Logger import log
from Core import DirectoryCreator
import MySQLdb as mysql

from threading import Thread
import threading

from Workers import WorkerBufferAverage
from Workers import WorkerDB
from Workers import WorkerRollingAverageSubtraction
from Workers import WorkerStaticImage



class Engine3():
    """
    Starts Buffer Average worker first so buffer average can bind to the correct port
    """
    
    def __init__(self, configFile):
        self.name = "Engine"
        log(self.name, "Engine Started")
        #ZeroMQ setup stuff
        self.context = zmq.Context()
        
        #Currne
        self.user = ""
      
        #Default workers
        self.bufferAverage = WorkerBufferAverage.WorkerBufferAverage()
        self.staticImage = WorkerStaticImage.WorkerStaticImage()
        self.rollingAverageSubtraction = WorkerRollingAverageSubtraction.WorkerRollingAverageSubtraction()
        #self.DB = WorkerDB.WorkerDB()
        
        #Connect Up all Workers, and have them ready
        self.bufferRequest = self.context.socket(zmq.REQ)
        self.bufferRequest.connect("tcp://127.0.0.1:5000")
        log(self.name, "Connected -> BufferRequest")

        self.bufferPush = self.context.socket(zmq.PUSH)
        self.bufferPush.bind("tcp://127.0.0.1:5001")
        log(self.name, "Binded -> BufferPush")

        self.staticPush = self.context.socket(zmq.PUSH)
        self.staticPush.bind("tcp://127.0.0.1:5002")
        log(self.name, "Binded -> StaticPush")

        time.sleep(0.1)

        self.rollingPush = self.context.socket(zmq.PUSH)
        self.rollingPush.bind("tcp://127.0.0.1:5003")
        log(self.name, "Binded -> RollingPush")

        time.sleep(0.1)
        
        bufferThread = Thread(target=self.bufferAverage.connect, args=(5001, 5000))
        bufferThread.isDaemon()
        bufferThread.start()

            
            
        staticImageThread = Thread(target=self.staticImage.connect, args=(5002,))
        staticImageThread.isDaemon()
        staticImageThread.start()
        
        rollingAverageThread = Thread(target=self.rollingAverageSubtraction.connect, args=(5003,))
        rollingAverageThread.isDaemon()

        rollingAverageThread.start()

        time.sleep(0.1)

        log(self.name, "All Workers ready")
        self.watchForChangeOver()
        self.watchForImage()
        log(self.name, "All Workers ready")

        

        
        
        
        
        
        
        
        
        
        
        
        #Start this thread last
        cliThread = Thread(target=self.cli())
        cliThread.isDaemon()
        cliThread.start()
        


    def getUser(self, path):
        """Splits file path, and returns only user"""
        user = path.split("/")
        user = filter(None, user) #needed to remove the none characters from the array
        return user[-1] #currently the user_epn is the last object in the list
    
    def setUser(self, char_value = False, **kw):
        if not (char_value): #needed for cli, though my kill engine, if user monitor doesnt return a valid value
            char_value = raw_input("Enter User: ")
        
        self.user = self.getUser(char_value) #get new user
        log(self.name, "User Changed -> " + str(self.user))
        
        self.bufferPush.send("updateUser")
        self.bufferPush.send(self.user)
        
        self.staticPush.send("updateUser")
        self.staticPush.send(self.user)

        self.rollingPush.send("updateUser")
        self.rollingPush.send(self.user)



    #EPICS MONITORING

    def watchForChangeOver(self):
        epics.camonitor("13SIM1:TIFF1:FilePath_RBV", callback=self.setUser)

    def watchForImage(self):
        epics.camonitor("13SIM1:cam1:NumImages_RBV", callback=self.imageTaken)
        
    def imageTaken(self):
        log(self.name, "image taken")

     
    #For Testing    
    def testPush(self):
        self.sendCommand("test")

        
    def testRequest(self):
        self.bufferRequest.send("test")
        test = self.bufferRequest.recv_pyobj()
        log(self.name, "RESPONSE RECIEVED -> " + test)
        
    def close(self):
        self.staticImage.close()
        
    def returnUser(self):
        log(self.name, "Current User : " + self.user)
        self.sendCommand("getUser")
    
    
    def cli(self):
        while True:
            time.sleep(0.1) #TODO: fixing printing output. - This is a quick fix to give enough time for all threads and workers
                            #to print/log out there data
            command = str(raw_input(">> "))
            if not hasattr(self, command):
                print "%s is not a valid command" % command
                print "user 'help' for list of commands"
            else:
                getattr(self, command)()
        
    def help(self):
        print "---- Test Commands ----"
        print "testPush - Test zmq push function"
        print "testRequest - Test zmq request function"
        
        print "---- Usage Commands ----"
        print "userChange(user)"
        
    def exit(self):
        print threading.activeCount()
        print "exiting..."
        sys.exit(self)
        print threading.activeCount()
        
        
    #########
    # Helper functions
    def sendCommand(self, command):
        self.staticPush.send(command)
        self.bufferPush.send(command)
        self.rollingPush.send(command)

        

if __name__ == "__main__":
    engine = Engine3("config.yaml")
    engine.testPush()
    engine.testRequest()
    engine.watchForChangeOver()


    
