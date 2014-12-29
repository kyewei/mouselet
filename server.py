#!/usr/bin/env python2.7

#Import python socket library and threading
import socket
import select

#Distinguish between OS
#if OS X, currentPlatform = "darwin"
#if Windows, currentPlatform = "win32"
#if Cygwin, currentPlatform = "cygwin"
#if Linux, currentPlatform = "linux2"
import sys
currentPlatform = sys.platform


#OS X only: import Objective C library for mouse control
if currentPlatform == "darwin":
    from Quartz.CoreGraphics import CGEventCreateMouseEvent
    from Quartz.CoreGraphics import CGEventPost
    from Quartz.CoreGraphics import CGEventSetIntegerValueField
    from Quartz.CoreGraphics import CGEventSetType
    from Quartz.CoreGraphics import kCGEventMouseMoved
    from Quartz.CoreGraphics import kCGEventLeftMouseDown
    from Quartz.CoreGraphics import kCGEventLeftMouseDragged
    from Quartz.CoreGraphics import kCGEventLeftMouseUp
    from Quartz.CoreGraphics import kCGEventRightMouseDown
    from Quartz.CoreGraphics import kCGEventRightMouseDragged
    from Quartz.CoreGraphics import kCGEventRightMouseUp
    from Quartz.CoreGraphics import kCGMouseEventClickState
    from Quartz.CoreGraphics import kCGMouseButtonLeft
    from Quartz.CoreGraphics import kCGMouseButtonRight
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

    def mousemove(posx,posy,isHeldL,isHeldR,device):
        mouseEvent(kCGEventMouseMoved,posx,posy)
        if isHeldL:
            mouseEvent(kCGEventLeftMouseDragged,posx,posy)
        if isHeldR:
                mouseEvent(kCGEventRightMouseDragged,posx,posy)

    def mouseclick(posx,posy,device,count):
        theEvent = CGEventCreateMouseEvent(
                    None,
                    kCGEventLeftMouseDown,
                    (posx,posy),
                    kCGMouseButtonLeft)

        CGEventSetIntegerValueField(theEvent,kCGMouseEventClickState,count)
        CGEventPost(kCGHIDEventTap, theEvent)
        CGEventSetType(theEvent,kCGEventLeftMouseUp)
        CGEventPost(kCGHIDEventTap, theEvent)

        for i in range(count-1):
            CGEventSetType(theEvent,kCGEventLeftMouseDown)
            CGEventPost(kCGHIDEventTap, theEvent)
            CGEventSetType(theEvent,kCGEventLeftMouseUp)
            CGEventPost(kCGHIDEventTap, theEvent)

    def mousedown(posx,posy,device,isLeft):
        if isLeft:
            mouseEvent(kCGEventLeftMouseDown, posx,posy)
        else:
            mouseEvent(kCGEventRightMouseDown, posx,posy)

    def mouseup(posx,posy,device,isLeft):
        if isLeft:
            mouseEvent(kCGEventLeftMouseUp, posx,posy)
        else:
            mouseEvent(kCGEventRightMouseUp, posx,posy)

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

    def mouseclick(posx,posy,device,count):
        mousedown(posx,posy,device)
        mouseup(posx,posy,device)

    def mousedown(posx,posy,device):
        mousemove(posx,posy,False,device)
        mouse_event(MOUSEEVENTF_LEFTDOWN,0,0,0,0)

    def mouseup(posx,posy,device):
        mousemove(posx,posy,True,device)
        mouse_event(MOUSEEVENTF_LEFTUP,0,0,0,0)

#Linux only: use Xlibs
elif currentPlatform == "linux2":
    from Xlib.display import Display
    from Xlib import X
    from Xlib.ext.xtest import fake_input

    display = Display(':0')

    def screenSize():
        return (display.screen().width_in_pixels,display.screen().height_in_pixels)

    def mousemove(posx,posy,isHeld,device):
        fake_input(display, X.MotionNotify, x=posx, y=posy)
        display.sync()

    def mousedown(posx,posy,device):
        mousemove(posx,posy,False,device)
        fake_input(display, X.ButtonPress, 1)
        display.sync()

    def mouseup(posx,posy,device):
        mousemove(posx,posy,False,device)
        fake_input(display, X.ButtonRelease, 1)
        display.sync()

    def mouseclick(posx,posy,device,count):
        mousedown(posx,posy,device)
        mouseup(posx,posy,device)

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
            devices[splitmsg[1]]["RMBHeld"] = False
            fn("sendstart:"+splitmsg[1])
        elif devices[splitmsg[1]]:
            mouse = devices[splitmsg[1]]

            if splitmsg[0] == "data" and len(splitmsg) == 5:
                mouse["x"] = mouse["x"] + float(splitmsg[2])
                newX = mouse["x"]
                mouse["y"] = mouse["y"] + float(splitmsg[3])
                newY = mouse["y"]
                if (newX >= mouse["xM"]) or newX <0:
                    fn("resetX:"+splitmsg[1])
                    newX = max(min(newX,mouse["xM"]-1-1),0+1)
                if (newY >= mouse["yM"]) or newY <0:
                    fn("resetY:"+splitmsg[1])
                    newY = max(min(newY,mouse["yM"]-1-1),0+1)
                mousemove(newX,newY,mouse["LMBHeld"],mouse["RMBHeld"],mouse)
            elif splitmsg[0] == "reset" and len(splitmsg) == 2:
                mouse["x"] = mouse["xM"]/2
                mouse["y"] = mouse["yM"]/2
                newX = mouse["x"]
                newY = mouse["y"]
                mousemove(newX,newY,mouse["LMBHeld"],mouse["RMBHeld"],mouse)
            elif splitmsg[0] == "statusLMB" and len(splitmsg) == 3:
                wasHeld = mouse["LMBHeld"]
                isHeld = splitmsg[2] == "1"
                if (wasHeld != isHeld):
                    mouse["LMBHeld"] = isHeld
                    if isHeld:
                        mousedown(mouse["x"],mouse["y"],mouse,True)
                    else:
                        mouseup(mouse["x"],mouse["y"],mouse,True)
            elif splitmsg[0] == "statusRMB" and len(splitmsg) == 3:
                wasHeld = mouse["RMBHeld"]
                isHeld = splitmsg[2] == "1"
                if (wasHeld != isHeld):
                    mouse["RMBHeld"] = isHeld
                    if isHeld:
                        mousedown(mouse["x"],mouse["y"],mouse,False)
                    else:
                        mouseup(mouse["x"],mouse["y"],mouse,False)
            elif splitmsg[0] == "LMBDoubleClick" and len(splitmsg) == 2:
                mouseclick(mouse["x"],mouse["y"],mouse,2)


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
                    #print "Client",hex(id(socket)),"removed!, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)
                    #continue

    server_socket.close()

if __name__ == '__main__':
    main()
