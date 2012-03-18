import epics
import time

while True:
    if epics.caget("13SIM1:cam1:NumImages_RBV") == 100:
        """
        
        
        Read logline
        get image type       
        
        
        
        
        """
        #Read LogLine
        #
    else:
        time.sleep(0.1)