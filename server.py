#!/usr/bin/env python2.7

#Import Twisted Network Library
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor


#Distinguish between OS
#if OS X, currentPlatform = "darwin"
import sys
currentPlatform = sys.platform



#OS X only: import Objective C library for mouse control

from Quartz.CoreGraphics import CGEventCreateMouseEvent
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import kCGEventMouseMoved
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseDragged
from Quartz.CoreGraphics import kCGEventLeftMouseUp
from Quartz.CoreGraphics import kCGMouseButtonLeft
from Quartz.CoreGraphics import kCGHIDEventTap

from Quartz import CGDisplayBounds
from Quartz import CGMainDisplayID

def mouseEvent(type, posx, posy):
    theEvent = CGEventCreateMouseEvent(
                None,
                type,
                (posx,posy),
                kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, theEvent)

def mousemove(posx,posy,isHeld):
    mouseEvent(kCGEventMouseMoved, posx,posy)
    if isHeld:
        mouseEvent(kCGEventLeftMouseDragged, posx,posy)

def mouseclick(posx,posy):
    #mouseEvent(kCGEventMouseMoved, posx,posy)
    mouseEvent(kCGEventLeftMouseDown, posx,posy)
    mouseEvent(kCGEventLeftMouseUp, posx,posy)

def mousedown(posx,posy):
    mouseEvent(kCGEventLeftMouseDown, posx,posy)

def mouseup(posx,posy):
    mouseEvent(kCGEventLeftMouseUp, posx,posy)

def screenSize():
    mainMonitor = CGDisplayBounds(CGMainDisplayID())
    return (mainMonitor.size.width, mainMonitor.size.height)






#Connected Devices
devices = {};



class mouseletProtocol(Protocol):
    def connectionMade(self):
        self.factory.clients.append(self)
        print "A client ("+str(hex(id(self)))+") connected, total",len(self.factory.clients),"client(s):", map(lambda x:hex(id(x)),self.factory.clients)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print "Client",hex(id(self)),"removed, total",len(self.factory.clients),"client(s):", map(lambda x:hex(id(x)),self.factory.clients)

    def dataReceived(self, data):
        print "Data received from "+str(hex(id(self)))+":",data
        processMessage(data, self.sendData)

    def sendData(self, message):
        print "Server sent messsage:",message
        self.transport.write(message+"\n")


def processMessage(message, fn):
    splitmsg = message.strip().split(":");
    if splitmsg[0] == "verify":
        screenS = screenSize()
        devices[splitmsg[1]] = {}
        devices[splitmsg[1]]["x"] = screenS[0]/2
        devices[splitmsg[1]]["y"] = screenS[1]/2
        devices[splitmsg[1]]["xM"] = screenS[0]
        devices[splitmsg[1]]["yM"] = screenS[1]
        devices[splitmsg[1]]["LMBHeld"] = False
        fn("sendstart:"+splitmsg[1])
    elif splitmsg[0] == "data":
        devices[splitmsg[1]]["x"] = devices[splitmsg[1]]["x"] + float(splitmsg[2])
        newX = devices[splitmsg[1]]["x"]
        devices[splitmsg[1]]["y"] = devices[splitmsg[1]]["y"] + float(splitmsg[3])
        newY = devices[splitmsg[1]]["y"]
        if (newX >= devices[splitmsg[1]]["xM"]) or newX <0:
            fn("resetX:"+splitmsg[1])
            newX = max(min(newX,devices[splitmsg[1]]["xM"]-1),0)
        if (newY >= devices[splitmsg[1]]["yM"]) or newY <0:
            fn("resetY:"+splitmsg[1])
            newY = max(min(newY,devices[splitmsg[1]]["yM"]-1),0)
        mousemove(newX, newY,devices[splitmsg[1]]["LMBHeld"])
    elif splitmsg[0] == "reset":
        if devices[splitmsg[1]]:
            devices[splitmsg[1]]["x"] = devices[splitmsg[1]]["xM"]/2
            devices[splitmsg[1]]["y"] = devices[splitmsg[1]]["yM"]/2
            newX = devices[splitmsg[1]]["x"]
            newY = devices[splitmsg[1]]["y"]
            mousemove(newX, newY,devices[splitmsg[1]]["LMBHeld"])
    elif splitmsg[0] == "statusLMB":
        if devices[splitmsg[1]]:
            wasHeld = devices[splitmsg[1]]["LMBHeld"]
            isHeld = splitmsg[2] == "1"
            if (wasHeld != isHeld):
                devices[splitmsg[1]]["LMBHeld"] = isHeld
                if isHeld:
                    mousedown(devices[splitmsg[1]]["x"],devices[splitmsg[1]]["y"])
                else:
                    mouseup(devices[splitmsg[1]]["x"],devices[splitmsg[1]]["y"])


def main():
    factory = Factory()
    factory.clients = []
    factory.protocol = mouseletProtocol
    reactor.listenTCP(22096, factory)

    print "mouselet communication server started"
    reactor.run()



if __name__ == '__main__':
    main()
