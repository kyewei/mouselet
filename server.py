#!/usr/bin/env python2.7
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor


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
        fn("sendstart:"+splitmsg[1])

def main():
    factory = Factory()
    factory.clients = []
    factory.protocol = mouseletProtocol
    reactor.listenTCP(22096, factory)

    print "mouselet communication server started"
    reactor.run()



if __name__ == '__main__':
    main()
