#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012
"""

import epics
import time

import zmq

context = zmq.Context()

buffers = context.socket(zmq.PUSH)
buffers.bind("tcp://*:7888")


sample = context.socket(zmq.PUSH)
sample.bind("tcp://*:7889")

time.sleep(1.0)
b = True

def send_buffer(value, **kw):
    global b
    if value == 100:
        if (b):
            print "sending data"
            buffers.send("testDat/0p009_0166.dat")
            print "sent"
            b = False
        else:
            print "sending SAMPLE"
            sample.send("testDat/0p009_0166.dat")
            print "sent"
            b = True
            

        
epics.camonitor("13SIM1:cam1:NumImages_RBV", callback=send_buffer)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass