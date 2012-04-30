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
from Core import DatFile
from Core import LogLine
from Core.Logger import log
from Core import DirectoryCreator
import MySQLdb as mysql

from threading import Thread

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
      
        
        
        #Default workers
        self.bufferAverage = WorkerBufferAverage.WorkerBufferAverage()
        self.staticImage = WorkerStaticImage.WorkerStaticImage()
        self.rollingAverageSubtraction = WorkerRollingAverageSubtraction.WorkerRollingAverageSubtraction()
        #self.DB = WorkerDB.WorkerDB()
        
        
        
               

        
        self.bufferRequest = self.context.socket(zmq.REQ)
        self.bufferRequest.connect("tcp://127.0.0.1:5000")
        log(self.name, "Connected -> BufferRequest")

        self.bufferPush = self.context.socket(zmq.PUSH)
        self.bufferPush.bind("tcp://127.0.0.1:5001")
        log(self.name, "Binded -> BufferPush")

        self.staticPush = self.context.socket(zmq.PUSH)
        self.staticPush.bind("tcp://127.0.0.1:5002")
        log(self.name, "Binded -> StaticPush")
        
        self.rollingPush = self.context.socket(zmq.PUSH)
        self.rollingPush.bind("tcp://127.0.0.1:5003")
        log(self.name, "Binded -> RollingPush")

        bufferThread = Thread(target=self.bufferAverage.connect, args=(5001, 5000))
        bufferThread.start()
        
        staticImageThread = Thread(target=self.staticImage.connect, args=(5002, 5000))
        staticImageThread.start()
        
        rollingAverageThread = Thread(target=self.rollingAverageSubtraction.connect, args=(5003, 5000))
        rollingAverageThread.start()



        time.sleep(0.1)
        #staticImageThread.start()
        #rollingAverageThread.start()

        
        #self.BufferAverage.connect(5000)
        #self.StaticImage.connect(5001, 5600)
        #self.RollingAverageSubtraction(5802, 4555)
        
        
        #self.BufferAverage.close()
        #self.StaticImage.close()
        #self.RollingAverageSubtraction.close()
        
        
        
    def testPush(self):
        self.staticPush.send("test")
        self.bufferPush.send("test")
        self.rollingPush.send("test")

        
        


if __name__ == "__main__":
    engine = Engine3("config.yaml")
    engine.testPush();
