#!/usr/bin/env python2.7
"""
Jack dywer
20 march 2012
"""
#TODO: Fix up sample Typpe, eg write to another table of subtracted types.


import sys
import time
from threading import Thread
sys.path.append("../")
import zmq
from Core import AverageList
from Core.Logger import logger
from Core import DatFile

from Worker import Worker

from Core import TableBuilder
import MySQLdb as mysql



class WorkerDB(Worker):
    
    def __init__(self):
        Worker.__init__(self, "WorkerDB")
        
    def connect(self, pullPort):
        self.pull.bind("tcp://127.0.0.1:"+str(pullPort))
        self.run()
    
    def run(self):
        try:
            while True:
                test = self.pull.recv()
                                
                #Generic Worker Control
                if (str(test) == "update_user"):
                    logger(self.name, "Received Command - updateUser")
                    self.user = self.pull.recv()
                    self.forceDBCreation(self.user)
                    self.buildTables()
                
                if (str(test) == "getUser"):
                    logger(self.name, "Current User : " + self.user)


                if (str(test) == "log_line"):
                    logLine = self.pull.recv_pyobj()
                    self.writeLogToDB(logLine)
                    
                if (str(test) == "sub_static_image"):
                    loc = self.pull.recv()
                    self.writeSubtractionLocation(loc)
                    
                if (str(test) == "buffer_file"):
                    loc = self.pull.recv()
                    self.writeBufferLocation(loc)
                    
                if (str(test) == "subtracted_average_image"):
                    loc = self.pull.recv()
                    self.writeAveragedSubtactedLocation(loc)
                    
                if (str(test) == "average_image"):
                    loc = self.pull.recv()
                    self.writeAveragedLocation(loc)
                
                
                if (str(test) == 'clear'):
                    self.clear()

                if (str(test) == "exit"):
                    self.close()
                    
                if (str(test) == "test"):
                    logger(self.name, "Received TEST")
                    
                                        
                #Test shit   
                if (str(test) == "testPush"):
                    testString = self.pull.recv();
                    logger(self.name, "Test Pull/Push - Completed - String Received : " + testString)

                
        except KeyboardInterrupt:
            pass

    
    def forceDBCreation(self, user):
        logger(self.name, "Forcing Database Creation")
        try:
            db = mysql.connect(user="root", host="localhost", passwd="a")
            c = db.cursor()
            cmd = "CREATE DATABASE IF NOT EXISTS " + str(user) + ";"
            c.execute(cmd)      
            logger(self.name, "Database Created for user: " + str(user))
        except Exception:
            logger(self.name, "Database CREATION FAILED for user:" + str(user))
            raise
    
    def buildTables(self):
        collumAttributes = ['WashType', 'SampleOmega', 'FilePluginDestination', 'Temperature2', 'Temperature1', 'WellNumber', 'SamplePhi', 'NumericTimeStamp', 'I0', 'SampleY', 'SampleX', 'SampleChi', 'TimeStamp', 'SampleType', 'ImageCounter', 'Ibs', 'exptime', 'FilePluginFileName', 'Energy', 'It', 'SampleTableX', 'SampleTableY', 'NORD', 'ImageLocation']

        collumAttributes_old = ['I0', 'NumericTimeStamp', 'WashType', 'FilePluginDestination', 'TimeStamp', 'Energy', 'NORD', 'SampleType', 'It', 'SampleTableX', 'SampleTableY', 'Temperature2', 'Temperature1', 'WellNumber', 'Ibs', 'exptime', 'FilePluginFileName', 'ImageLocation']
        self.logTable = TableBuilder.TableBuilder(self.user, "Log", collumAttributes)
        
        #This needs to bs fixed to support different sample types
        bufferRows = ['buffer_location']
        self.bufferTable = TableBuilder.TableBuilder(self.user, 'buffers', bufferRows)
        
        subtractedRows = ['subtracted_location']
        self.subtractedTable = TableBuilder.TableBuilder(self.user, 'subtracted_images', subtractedRows)
        
        averagedRows = ['average_location']
        self.averagedTable = TableBuilder.TableBuilder(self.user, 'average_images', averagedRows)
        
        averagedSubRows = ['subtracted_average_location']
        self.averagedSubTable = TableBuilder.TableBuilder(self.user, 'average_subtracted_images', averagedSubRows)

    
    
    def writeLogToDB(self, logLine):
        self.logTable.addData(logLine.data)
        
    def writeSubtractionLocation(self, image):
        self.subtractedTable.addData({ "subtracted_location" : image })
    
    def writeBufferLocation(self, image): 
        self.bufferTable.addData({ "buffer_location" : image })
        
    def writeAveragedLocation(self, image):
        self.averagedTable.addData({ "average_location" : image })
    
    def writeAveragedSubtactedLocation(self, image):
        self.averagedSubTable.addData({ "subtracted_average_location" : image })
        
        
if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False

    print "TEST 1 - ONLY PUSH/PULL"
    #Test 1 - Only a pull socket
    b = Worker("Worker db")
    t = Thread(target=b.connect, args=(pushPort,))
    t.start()

    
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("clear")
    time.sleep(0.1)
    testPush.close()
    b.close()
        
    sys.exit()


