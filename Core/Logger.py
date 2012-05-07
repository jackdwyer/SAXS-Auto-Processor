import datetime

def log(name, message):
    now = datetime.datetime.now()
    logFile = "engine.log"
    formatting  = '%34s %10s %1s'
    print str(now)
    print formatting % ('['+name+']','--', message+"\n"),
    f = open(logFile, 'a')
    f.write(formatting % ('['+name+']','--', message+"\n"))#Needed for string formatting
