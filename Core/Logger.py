def log(name, message):
    logFile = "engine.log"
    formatting  = '%34s %10s %1s'
    f = open(logFile, 'a')
    f.write(formatting % ('['+name+']','--', message+"\n"))#Needed for string formatting
