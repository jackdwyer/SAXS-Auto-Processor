import datetime

def log(name, message):
    now = datetime.datetime.now()
    
    
    
    logFile = "engine.log"
    formatting  = '%s %2s %10s %1s'
    #print str(now)
    print formatting % (str(now), ' -- ['+name+']','--', message+"\n"),
    f = open(logFile, 'a')
    f.write(formatting % (str(now), '-- ['+name+']','--', message+"\n"))#Needed for string formatting

if __name__ == "__main__":
    log("Jack", "UNIT TEST MESSAGE")