"""
Jack Dwyer
Class for reading the logfile
hopfully this will fix all my errors
"""
import time
import sys
from Logger import logger
from threading import Thread



class LogWatcher():
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

        while True:
            try:
                fp = open(self.logLocation,'r')
                break
            except IOError:
                print "Waiting for logFile"
                print self.logLocation
                time.sleep(0.5);
            
            #other shit here for if file dont exist
        
        print "In FileWatch"
        
        while self.alive:
            new = fp.readline()
            if new:
                yield new
            else:
                time.sleep(0.5)

    def watchThread(self):
        for line in self.fileWatch():
            print line
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


