#!/usr/bin/env python2.7

#Import python socket library and threading
import socket
import select

#Distinguish between OS
#if OS X, currentPlatform = "darwin"
#if Windows, currentPlatform = "win32"
#if Cygwin, currentPlatform = "cygwin"
import sys
currentPlatform = sys.platform


#OS X only: import Objective C library for mouse control
if currentPlatform == "darwin":
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

    #global mousemove, mouseclick, mousedown, mouseup, screenSize
    def mouseEvent(type,posx,posy):
        theEvent = CGEventCreateMouseEvent(
                    None,
                    type,
                    (posx,posy),
                    kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)

    def mousemove(posx,posy,isHeld,device):
        mouseEvent(kCGEventMouseMoved, posx,posy)
        if isHeld:
            mouseEvent(kCGEventLeftMouseDragged, posx,posy)

    def mouseclick(posx,posy,device):
        #mouseEvent(kCGEventMouseMoved, posx,posy)
        mouseEvent(kCGEventLeftMouseDown, posx,posy)
        mouseEvent(kCGEventLeftMouseUp, posx,posy)

    def mousedown(posx,posy,device):
        mouseEvent(kCGEventLeftMouseDown, posx,posy)

    def mouseup(posx,posy,device):
        mouseEvent(kCGEventLeftMouseUp, posx,posy)

    def screenSize():
        mainMonitor = CGDisplayBounds(CGMainDisplayID())
        return (mainMonitor.size.width, mainMonitor.size.height)

#Windows only: use native c libraries to set position, etc
#not working in cygwin, but works in native windows python so doesn't matter
elif currentPlatform == "win32":
    import ctypes
    #SetCursorPos = ctypes.windll.user32.SetCursorPos
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    #MOUSEEVENTF_RIGHTDOWN = 0x0008
    #MOUSEEVENTF_RIGHTUP = 0x0010
    #MOUSEEVENTF_MIDDLEDOWN = 0x0020
    #MOUSEEVENTF_MIDDLEUP = 0x0040
    #MOUSEEVENTF_WHEEL = 0x0800
    MOUSEEVENTF_ABSOLUTE = 0x8000
    MOUSEEVENTF_MOVEABS = MOUSEEVENTF_MOVE + MOUSEEVENTF_ABSOLUTE

    mouse_event = ctypes.windll.user32.mouse_event
    #SetCursorPos = ctypes.windll.user32.SetCursorPos
    def getX(posx,maxx):
        return 65536L * long(posx) / maxx + 1

    def getY(posy,maxy):
        return 65536L * long(posy) / maxy + 1

    def screenSize():
        return (ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1))

    def mousemove(posx,posy,isHeld,device):
        #dragging is just mousedown+ move mouse + mouseup, no nothing special
        #however, there is a quirk with dragging so that down-move-up must not be instantaneous
        #  or there wont be drag... thankfully since the device updates every x seconds, this
        #  adds a delay itself, otherwise i'd have to delay and block here, which is bad
        mouse_event(MOUSEEVENTF_MOVEABS,getX(posx,device["xM"]),getY(posy,device["yM"]),0,0)
        #SetCursorPos(posx,posy)

    def mouseclick(posx,posy,device):
        mousedown(posx,posy,device)
        mouseup(posx,posy,device)

    def mousedown(posx,posy,device):
        mousemove(posx,posy,False,device)
        mouse_event(MOUSEEVENTF_LEFTDOWN,0,0,0,0)

    def mouseup(posx,posy,device):
        mousemove(posx,posy,True,device)
        mouse_event(MOUSEEVENTF_LEFTUP,0,0,0,0)


#Connected Devices
devices = {};


def processMessage(message, fn):
    # if theres a delay, messages are sent in bursts, so separate out each line
    splitmsgarr =message.strip().split("\n")
    for line in splitmsgarr: #then do processing on each line, which is a command
        splitmsg = line.strip().split(":");
        if splitmsg[0] == "verify" and len(splitmsg) == 2:
            screenS = screenSize()
            devices[splitmsg[1]] = {}
            devices[splitmsg[1]]["x"] = screenS[0]/2
            devices[splitmsg[1]]["y"] = screenS[1]/2
            devices[splitmsg[1]]["xM"] = screenS[0]
            devices[splitmsg[1]]["yM"] = screenS[1]
            devices[splitmsg[1]]["LMBHeld"] = False
            fn("sendstart:"+splitmsg[1])
        elif splitmsg[0] == "data" and len(splitmsg) == 5:
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
            mousemove(newX,newY,devices[splitmsg[1]]["LMBHeld"],devices[splitmsg[1]])
        elif splitmsg[0] == "reset" and len(splitmsg) == 2:
            if devices[splitmsg[1]]:
                devices[splitmsg[1]]["x"] = devices[splitmsg[1]]["xM"]/2
                devices[splitmsg[1]]["y"] = devices[splitmsg[1]]["yM"]/2
                newX = devices[splitmsg[1]]["x"]
                newY = devices[splitmsg[1]]["y"]
                mousemove(newX,newY,devices[splitmsg[1]]["LMBHeld"],devices[splitmsg[1]])
        elif splitmsg[0] == "statusLMB" and len(splitmsg) == 3:
            if devices[splitmsg[1]]:
                wasHeld = devices[splitmsg[1]]["LMBHeld"]
                isHeld = splitmsg[2] == "1"
                if (wasHeld != isHeld):
                    devices[splitmsg[1]]["LMBHeld"] = isHeld
                    if isHeld:
                        mousedown(devices[splitmsg[1]]["x"],devices[splitmsg[1]]["y"],devices[splitmsg[1]])
                    else:
                        mouseup(devices[splitmsg[1]]["x"],devices[splitmsg[1]]["y"],devices[splitmsg[1]])

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
                #try:
                    data = socket.recv(RECV_BUFFER)
                    if data:
                        print "Data received from "+str(hex(id(socket)))+":",data
                        processMessage(data,wrapfn(socket.sendall))
                    else:
                        socket.close()
                        CONNECTION_LIST.remove(socket)
                        print "Client",hex(id(socket)),"removed, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)
                #except:
                    #socket.close()
                    #CONNECTION_LIST.remove(socket)
                    #print "Exception"
                    #print "Client",hex(id(socket)),"removed, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)
                    #continue

    server_socket.close()

if __name__ == '__main__':
    main()
