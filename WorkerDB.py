#!/usr/bin/env python2.7
"""
Jack dywer
20 march 2012
"""
#TODO: Fix up sample Typpe, eg write to another table of subtracted types.

import zmq
from CommonLib import *
import MySQLdb as mysql



class WorkerDB():
    def __init__(self):
        #General SQL setup
        self.host = "localhost"
        self.root = "root"
        self.password = "a"
        
        
        
        self.user = ""
        self.experiment = ""
        self.logTable = "" 
        self.imageTable = ""
    
    
    def forceDBCreation(self, user):
        print "here"
        self.user = user
        try:
            print "trying.."
            db = mysql.connect(user=self.root, host=self.host, passwd=self.password)
            c = db.cursor()
            cmd = "CREATE DATABASE IF NOT EXISTS " + str(self.user) + ";"
            c.execute(cmd)      
            print "DATABASE CREATED for USER: ", self.user
        except Exception:
            print "Database for user: " + str(self.user) + "  -Failed to be created"
            raise
    
    
    def buildExperimentTable(self, experiment):
        self.experiment = experiment
        collumAttributes = ['GISAXS_OMEGA', 'Protein_SMPL', 'Phi', 'NumericTimeStamp', 'Slit_3_V', 'I0', 'Slit_2_V', 'Slit_2_H', 'NOMINAL_CL', 'Slit_3_H', 'Keithly2', 'Slit_4_H', 'TimeStamp', 'ActualExpTime', 'Ibs', 'Slit_4_V', 'exptime', 'SMPL_TBL_X', 'SMPL_TBL_Y', 'Energy', 'It', 'Temp2', 'Temp1', 'SMPL_TYPE', 'GISAXS_SMPL_X', 'GISAXS_SMPL_Y', 'ImageLocation']
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
    dbWriter.bind("tcp://*:7884")
    
    try:
        while True:
            #Will be first sent, what to write/do
            filter = dbWriter.recv()
            if (str(filter) == "user"):
                user = dbWriter.recv()
                print "Building a Database for user: ", user
                worker.forceDBCreation(user)
                
            if (str(filter) == "Experiment"):
                experiment = dbWriter.recv()
                print "Building Table for Experiment: ", experiment
                worker.buildExperimentTable(str(experiment))
            
            if (str(filter) == "logLine"):
                print "Writing out LogLine To DB"
                logLine = dbWriter.recv_pyobj()
                worker.writeLogToDB(logLine)
                print "Logline written to DB"

                
            if (str(filter) == "ImageLocation"):
                location = dbWriter.recv()
                print "Writing ImageLocation: ", location
                worker.writeImageLocation(str(location))
                print "Location Written"
                

    except KeyboardInterrupt:
        pass