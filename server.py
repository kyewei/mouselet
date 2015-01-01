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
    #First import all things from library
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

    from Quartz import CGDisplayBounds #Also import monitor size
    from Quartz import CGMainDisplayID

    #global mousemove, mouseclick, mousedown, mouseup, screenSize
    def mouseEvent(type,posx,posy):
        #Make Quartz Event and Post (instantiate) it
        theEvent = CGEventCreateMouseEvent(
                    None,
                    type,
                    (posx,posy),
                    kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)

    def mousemove(posx,posy,isHeldL,isHeldR,device):
        #Move mouse to x,y
        mouseEvent(kCGEventMouseMoved,posx,posy)
        #Only OS X has this quirk where dragging must also be explicitly done, 
        #  instead of just doing mouseDown + move
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
        #Had to manually do the clicking, since kCGMouseEventClickState needs to be set as well for double click to register
        #  Simply doing up+down x2 was not enough
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
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    #MOUSEEVENTF_MIDDLEDOWN = 0x0020
    #MOUSEEVENTF_MIDDLEUP = 0x0040
    #MOUSEEVENTF_WHEEL = 0x0800
    MOUSEEVENTF_ABSOLUTE = 0x8000
    MOUSEEVENTF_MOVEABS = MOUSEEVENTF_MOVE + MOUSEEVENTF_ABSOLUTE

    mouse_event = ctypes.windll.user32.mouse_event
    #SetCursorPos = ctypes.windll.user32.SetCursorPos
    def getX(posx,maxx): #Needed to convert to appropriate numbers for who knows why
        return 65536L * long(posx) / maxx + 1

    def getY(posy,maxy): #Needed to convert to appropriate numbers for who knows why
        return 65536L * long(posy) / maxy + 1

    def screenSize():
        return (ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1))

    def mousemove(posx,posy,isHeldL,isHeldR,device):
        #dragging is just mousedown+ move mouse + mouseup, no nothing special
        #however, there is a quirk with dragging so that down-move-up must not be instantaneous
        #  or there wont be drag... thankfully since the device updates every x seconds, this
        #  adds a delay itself, otherwise i'd have to delay and block here, which is bad
        mouse_event(MOUSEEVENTF_MOVEABS,getX(posx,device["xM"]),getY(posy,device["yM"]),0,0)
        #SetCursorPos(posx,posy)

    def mouseclick(posx,posy,device,count): #Windows API is simpler, just down+up x number_of_times
        for i in range(count):
            mousedown(posx,posy,device,True)
            mouseup(posx,posy,device,True)

    def mousedown(posx,posy,device,isLeft):
        if isLeft:
            mousemove(posx,posy,False,device["RMBHeld"],device)
            mouse_event(MOUSEEVENTF_LEFTDOWN,0,0,0,0)
        else:
            mousemove(posx,posy,device["LMBHeld"],False,device)
            mouse_event(MOUSEEVENTF_RIGHTDOWN,0,0,0,0)
    def mouseup(posx,posy,device,isLeft):
        if isLeft:
            mousemove(posx,posy,True,device["RMBHeld"],device)
            mouse_event(MOUSEEVENTF_LEFTUP,0,0,0,0)
        else:
            mousemove(posx,posy,device["LMBHeld"],True,device)
            mouse_event(MOUSEEVENTF_RIGHTUP,0,0,0,0)

#Linux only: use Xlibs
elif currentPlatform == "linux2":
    from Xlib.display import Display
    from Xlib import X
    from Xlib.ext.xtest import fake_input

    display = Display(':0')

    def screenSize():
        return (display.screen().width_in_pixels,display.screen().height_in_pixels)

    def mousemove(posx,posy,isHeldL,isHeldR,device):
        fake_input(display, X.MotionNotify, x=posx, y=posy)
        display.sync()
        
    #LMB is X.Button1, RMB is X.Button3
    def mousedown(posx,posy,device,isLeft):
        mousemove(posx,posy,False,False,device)
        if isLeft:
            fake_input(display, X.ButtonPress, X.Button1)
        else:
            fake_input(display, X.ButtonPress, X.Button3)
        display.sync()

    def mouseup(posx,posy,device,isLeft):
        mousemove(posx,posy,False,False,device)
        if isLeft:
            fake_input(display, X.ButtonRelease, X.Button1)
        else:
            fake_input(display, X.ButtonRelease, X.Button3)
        display.sync()

    def mouseclick(posx,posy,device,count): #Simple down+up x count times
        for i in range(count):
            mousedown(posx,posy,device,True)
            mouseup(posx,posy,device,True)

#Connected Devices
devices = {};


def processMessage(message, fn): #Functions returns None if no problems, or incomplete last line if line is split up
    # if theres a delay, messages are sent in bursts, so separate out each line
    splitmsgarr =message.strip().split("\n")
    for line in splitmsgarr: #then do processing on each line, which is a command
        splitmsg = line.strip().split(":")
        
        #Processing of various commands. Look in protocolMessageSpec.txt for more information
        
        if len(splitmsg) == 2 and splitmsg[0] == "verify": #First message from client to server
            screenS = screenSize()
            devices[splitmsg[1]] = {} #Resets fields
            devices[splitmsg[1]]["x"] = screenS[0]/2 * 1.0
            devices[splitmsg[1]]["y"] = screenS[1]/2 * 1.0
            devices[splitmsg[1]]["xM"] = screenS[0]
            devices[splitmsg[1]]["yM"] = screenS[1]
            devices[splitmsg[1]]["LMBHeld"] = False
            devices[splitmsg[1]]["RMBHeld"] = False
            fn("sendstart:"+splitmsg[1]) #Server reply for client to start sending
        
        #Check to make sure splitmsg[1] and devices lookup exist to get rid of error
        elif len(splitmsg) >=2 and splitmsg[1] in devices: 
            mouse = devices[splitmsg[1]]
            
            #for each, check to see if Message is complete (has the required length)
            if len(splitmsg) == 5 and splitmsg[0] == "data": #Mouse position change
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
            elif len(splitmsg) == 2 and splitmsg[0] == "reset": #Reset mouse position to center
                mouse["x"] = mouse["xM"]/2
                mouse["y"] = mouse["yM"]/2
                newX = mouse["x"]
                newY = mouse["y"]
                mousemove(newX,newY,mouse["LMBHeld"],mouse["RMBHeld"],mouse)
            elif len(splitmsg) == 3 and splitmsg[0] == "statusLMB": #Tells server status of LMB: held/not held
                wasHeld = mouse["LMBHeld"]
                isHeld = splitmsg[2] == "1"
                if (wasHeld != isHeld):
                    mouse["LMBHeld"] = isHeld
                    if isHeld:
                        mousedown(mouse["x"],mouse["y"],mouse,True)
                    else:
                        mouseup(mouse["x"],mouse["y"],mouse,True)
            elif len(splitmsg) == 3 and splitmsg[0] == "statusRMB": #Tells server status of RMB: held/not held
                wasHeld = mouse["RMBHeld"]
                isHeld = splitmsg[2] == "1"
                if (wasHeld != isHeld):
                    mouse["RMBHeld"] = isHeld
                    if isHeld:
                        mousedown(mouse["x"],mouse["y"],mouse,False)
                    else:
                        mouseup(mouse["x"],mouse["y"],mouse,False)
            elif len(splitmsg) == 2 and splitmsg[0] == "LMBDoubleClick": #Tells server to execute doubleclick
                mouseclick(mouse["x"],mouse["y"],mouse,2)
            else: #Assume message is incomplete, return incomplete line
                return line
        else: #Assume message is incomplete, return incomplete line
            return line

def wrapfn(sendfn): #Wrap and curry so every message is logged
    def displaysent(message):
        print "Server sent messsage:",message
        sendfn(message+"\n")
    return displaysent

def main():
    global socket #apparently imported things don't show up
    HOST = '' #all interfaces
    PORT = 22096 #Hmm. These numbers aren't just random.
    CONNECTION_LIST = []
    RECV_BUFFER = 1024

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    CONNECTION_LIST.append(server_socket)
    print "mouselet communication server ("+str(hex(id(server_socket)))+") started on port:", PORT
    print "Total",len(CONNECTION_LIST),"connections(s)", map(lambda x:hex(id(x)),CONNECTION_LIST)
    
    #Associative array to lookup incomplete lines
    #Sometimes when a connection is really bad, lines are broken up mid-transfer
    #This saves the incomplete last line of a message, which will be prepended to the data of the next successful transfer
    incompleteMessage = {}
    
    
    while True:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        for socket in read_sockets:
            if socket == server_socket:
                client_socket, address = server_socket.accept()
                CONNECTION_LIST.append(client_socket)
                print "A client ("+str(hex(id(client_socket)))+") connected, total",len(CONNECTION_LIST),"connections(s):", map(lambda x:hex(id(x)),CONNECTION_LIST)
                incompleteMessage[str(hex(id(client_socket)))] = ""

            else:
                #try:
                    data = socket.recv(RECV_BUFFER)
                    if data:
                        print "Data received from "+str(hex(id(socket)))+":",data
                        
                        #Append previously incomplete last line
                        appendedData = incompleteMessage[str(hex(id(socket)))] + data 
                        incompleteMessage[str(hex(id(socket)))] = ""
                        
                        #Process message
                        result = processMessage(appendedData,wrapfn(socket.sendall))
                        if result != None: #function returned incomplete last line
                            incompleteMessage[str(hex(id(socket)))] = result
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
