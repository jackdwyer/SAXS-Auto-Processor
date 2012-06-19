import time
import epics

class callBackTest():
    def __init__(self):
        self.previousUser = None
    
    def testUser(self, user):
        if not (self.previousUser):
            self.previousUser = user
            print "Previous user set"
        
        if (self.previousUser == user):
            print "Same User - Do nothing"
        
        if (self.previousUser != user):
            self.previousUser = user
            print "Must do something"

    def printUser(self, char_value, **kw):
        print char_value
        self.testUser(char_value)
    
    def setWatcher(self):
        epics.camonitor("13SIM1:TIFF1:FilePath", callback=self.printUser)

    def run(self):
        self.setWatcher()
        while True:
            time.sleep(0.5)


"""    
def printUser(char_value = False, **kw):
    print char_value


def setImageLocationEpics():
    epics.caput("13SIM1:TIFF1:FilePath", "Jack" + bytearray("\0x00"*256))
    """

if __name__ == "__main__":
    e = callBackTest()
    e.run()