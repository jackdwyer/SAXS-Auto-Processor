"""
Jack Dwyer
06-07-2012
Better simulator, to send specific requests for testing
"""

import yaml
import time
import epics

class Sim3():
    def __init__(self, configuration):
        
        try:
            stream = file(configuration, 'r') 
        except IOError:
            logging.critical(self.name, "Unable to find configuration file (config.yaml, in current directory), exiting.")
            sys.exit
        
        config = yaml.load(stream)
        self.rootDirectory = config.get('RootDirectory')
        self.userChangePV = config.get('UserChangePV')
        
        self.workers = config.get('workers')
        
        
        
        self.run()
        
    def run(self):
        try:
            while True:
                print "1: Enter a User string"
                print "2: Send Repeat Request of same User"
                print "3: Send Repeat Request of different User"
    
                option = raw_input("Enter Option: ")
            
                
                if (option == "1"):
                    user = raw_input("Enter User: ")
                    self.sendUser(user)
                    
                if (option == "2"):
                    user = raw_input("Enter User: ")
                    timeout = raw_input("Enter timeout: ")
                    numOfTimes = raw_input("Number of runs: ")
                    i = 0
                    while (i < int(numOfTimes)):
                        self.sendUser(user)
                        time.sleep(float(timeout))
                        print i
                        i = i + 1                
        
                if (option == "3"):
                    timeout = raw_input("Enter timeout: ")
                    numOfTimes = raw_input("Number of runs: ")
                    i = 0
                    user = "JackA"
                    while (i < int(numOfTimes)):
                        self.sendUser(user)
                        time.sleep(float(timeout))
                        print i
                        i = i + 1                
                        user = user + "_a"
        except KeyboardInterrupt:
            pass
    
    def sendUser(self, user):
        epics.caput(self.userChangePV, "/location/to/something/"+str(user)+"/images" + bytearray("\0x00"*256))

                


if __name__ == "__main__":
    sim = Sim3("simsettings.conf")


