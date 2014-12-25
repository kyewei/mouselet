#!/usr/bin/env python2.7

#Import python socket library and threading
import socket
import select


#Distinguish between OS
#if OS X, currentPlatform = "darwin"
#if Windows, currentPlatform = "win32"
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

def wrapfn(sendfn):
    def displaysent(message):
        print "Server sent messsage:",message
        sendfn(message+"\n")
    return displaysent

def main():
    global socket #apparently imported things don't show up
    HOST = '' #all interfaces
    PORT = 22096
    CONNECTION_LIST = []
    RECV_BUFFER = 1024

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    CONNECTION_LIST.append(server_socket)
    print "mouselet communication server ("+str(hex(id(server_socket)))+") started on port:", PORT
    print "Total",len(CONNECTION_LIST),"connections(s)", map(lambda x:hex(id(x)),CONNECTION_LIST)

    while True:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        for socket in read_sockets:
            if socket == server_socket:
                client_socket, address = server_socket.accept()
                CONNECTION_LIST.append(client_socket)
                print "A client ("+str(hex(id(client_socket)))+") connected, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)

            else:
                try:
                    data = socket.recv(RECV_BUFFER)
                    if data:
                        print "Data received from "+str(hex(id(socket)))+":",data
                        processMessage(data,wrapfn(socket.sendall))
                    else:
                        socket.close()
                        CONNECTION_LIST.remove(socket)
                        print "Client",hex(id(socket)),"removed, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)
                except:
                    socket.close()
                    CONNECTION_LIST.remove(socket)
                    print "Client",hex(id(socket)),"removed, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)
                    continue

    server_socket.close()

if __name__ == '__main__':
    main()
