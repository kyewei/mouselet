#!/usr/bin/env python2.7
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

class mouseletProtocol(Protocol):
    def connectionMade(self):
        self.factory.clients.append(self)
        print "A client connected: ", self
        print "Total", len(self.factory.clients), "client(s):", self.factory.clients

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print self,"removed."


    def dataReceived(self, data):
        print "Data received:",data


factory = Factory()
factory.clients = []
factory.protocol = mouseletProtocol
reactor.listenTCP(22096, factory)
print "mouselet communication server started"
reactor.run()
