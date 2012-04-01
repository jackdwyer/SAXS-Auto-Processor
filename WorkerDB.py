#!/usr/bin/env python2.7
"""
Jack dywer
20 march 2012
"""
#TODO: Fix up sample Typpe, eg write to another table of subtracted types.

import zmq
from CommonLib import TableBuilder
from CommonLib import Logger
import MySQLdb as mysql



class WorkerDB():
    def __init__(self):
        #for logging
        self.name = "WorkerDB"
        Logger.log(self.name, "Worker Generated")

        
        #General SQL setup
        self.host = "localhost"
        self.root = "root"
        self.password = "a"
        
        self.user = ""
        self.experiment = ""
        self.logTable = "" 
        self.imageTable = ""
    
    def forceDBCreation(self, user):
        
        Logger.log(self.name, "Forcing Database Creation")
        self.user = user
        try:
            db = mysql.connect(user=self.root, host=self.host, passwd=self.password)
            c = db.cursor()
            cmd = "CREATE DATABASE IF NOT EXISTS " + str(self.user) + ";"
            c.execute(cmd)      
            Logger.log(self.name, "Database Created for user: " + str(self.user))
        except Exception:
            Logger.log(self.name, "Database CREATION FAILED for user:" + str(self.user))
            raise
    
    
    def buildExperimentTable(self, experiment):
        self.experiment = experiment
        collumAttributes = ['I0', 'NumericTimeStamp', 'WashType', 'FilePluginDestination', 'TimeStamp', 'Energy', 'NORD', 'SampleType', 'It', 'SampleTableX', 'SampleTableY', 'Temperature2', 'Temperature1', 'WellNumber', 'Ibs', 'exptime', 'FilePluginFileName', 'ImageLocation']
        self.logTable = TableBuilder.TableBuilder(self.user, self.experiment, collumAttributes)
        
        #This needs to bs fixed to support different sample types
        imageLoc = ['subtracted_location']
        self.imageTable = TableBuilder.TableBuilder(self.user, 'Images', imageLoc)
        
    def writeLogToDB(self, logLine):
        self.logTable.addData(logLine.data)
        
    def writeImageLocation(self, location):
        d = { "subtracted_location" : location }
        self.imageTable.addData(d)
    



if __name__ == "__main__":
    worker = WorkerDB()
    context = zmq.Context()
    dbWriter = context.socket(zmq.PULL)
    dbWriter.connect("tcp://127.0.0.1:7884")
    
    try:
        while True:
            #Will be first sent, what to write/do
            filter = dbWriter.recv()
            if (str(filter) == "user"):
                user = dbWriter.recv()
                Logger.log(worker.name, "Recieved Command to build Database for user: " + str(user))
                worker.forceDBCreation(user)
                
            if (str(filter) == "Experiment"):
                experiment = dbWriter.recv()
                Logger.log(worker.name, "Building experiment table: " + str(experiment))
                worker.buildExperimentTable(str(experiment))
            
            if (str(filter) == "logLine"):
                Logger.log(worker.name, "Writing LogLine to DB")
                logLine = dbWriter.recv_pyobj()
                worker.writeLogToDB(logLine)
                Logger.log(worker.name, "LogLine written")

                
            if (str(filter) == "ImageLocation"):
                location = dbWriter.recv()
                Logger.log(worker.name, "Image Location recieved, writing to DB")
                worker.writeImageLocation(str(location))
                Logger.log(worker.name, "Location written: ", str(location))
                

    except KeyboardInterrupt:
        pass
