#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012

23 March
- Fixing what is written out
"""

import zmq
import sys

from Core.Logger import log
from Core import DatFile
from Core import DatFileWriter

from Worker import Worker

class WorkerStaticImage(Worker):
    def __init__(self):
        Worker.__init__(self, "WorkerStaticImage")
        print self.name

if __name__ == "__main__":

    worker = WorkerStaticImage()
    worker.connect(5001, 5002)

         

