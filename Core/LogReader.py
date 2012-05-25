"""
Jack Dwyer
Class for reading the logfile
hopfully this will fix all my errors
"""
import time
import sys
from Logger import logger
from threading import Thread



class LogReader():
    def __init__(self):
        self.log = ""
        self.name = "LogReader"
        self.logLocation = ""
        self.alive = True
        self.thread = None
        self.callback = None

    def setLocation(self, logLocation):
        print "location set"
        self.logLocation = logLocation

    def setCallback(self, callback):
        self.callback = callback

    def kill(self):
        self.alive = False
        self.thread.join()

    def watch(self):
        self.thread = Thread(target=self.watchThread,)
        self.thread.start()


    def fileWatch(self):
        #other shit here for if file dont exist
        fp = open(self.logLocation,'r')

        while self.alive:
            new = fp.readline()
            if new:
                yield new
            else:
                time.sleep(0.5)

    def watchThread(self):
        for line in self.fileWatch():
            self.callback(line)



if __name__ == "__main__":
    
    def callback(line):
        print line,

    a = LogReader()
    a.setLocation("livelogfile.log")
    a.setCallback(callback)

    a.watch()

    time.sleep(10)

    a.kill()
    print "Done"



""""

class LogReader():
    def __init__(self):
        self.log = ""
        self.name = "LogReader"
        self.logLocation = ""
        self.alive = True
        
    def setLocation(self, logLocation):
        print "location set"
        self.logLocation = logLocation
        
    def kill(self):
        self.alive = False
        
    def watch(self):
        Thread(target=self.watchThread,).start()


    def watchThread(self):
        if not (self.log):
            start_time = time.time()
            logger(self.name, "Log File")
            while not (self.log):
                if ((time.time() - start_time) > 30.0):
                    logger(self.name, "Error: can not open log file at location: " + self.logLocation)
                    logger(self.name, "FATAL ERROR")
                    logger(self.name, "Shutting down")
                    sys.exit()
                else:
                    logger(self.name, "Opened Log File")
                    time.sleep(0.1)
                    self.log = open(self.logLocation, 'r')
                   
        while True:
            new = self.log.readline()
            if new: 
                yield new
            else:
                logger(self.name, "waiting for a new line")
                time.sleep(0.5)

        

    

    
    
if __name__ == "__main__":
    
    
    def line():
        print "called back"
    
    def start_watch(callback=line):
        f
    
    def lines2():    
        print "lines"
        while True:
            for line in a.watch():
                print line
                
    
    a = LogReader()
    a.setLocation("/home/dwyerj/beamlinetesting/b/raw_dat/livelogfile.log")

    l = Thread(target=lines2,)
    l.start()
    
    print "t"
    
    """