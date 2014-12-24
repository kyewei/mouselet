//
//  mouseletData.m
//  mouselet
//
//  Created by Kye on 2014-12-23.
//  Copyright (c) 2014 Kye. All rights reserved.
//

#import "mouseletData.h"
#include <ifaddrs.h>
#include <arpa/inet.h>

//Forward Declarations
@interface MainViewController : UIViewController
@end
@interface SettingsViewController : UITableViewController
- (void)connectionStatusUpdate;
@end


@implementation mouseletData 

- (id) init {
    self = [super init];
    if (self) {
        
        self.currentStatus = NOTCONNECTED;
        
        self.multiplier = 300;
        self.friction = 1;
        self.movingAveragePointCount = 3;
        self.movingAverageAccelX = [[NSMutableArray alloc] initWithCapacity:self.movingAveragePointCount];
        self.movingAverageAccelY = [[NSMutableArray alloc] initWithCapacity:self.movingAveragePointCount];
        self.movingAverageAccelZ = [[NSMutableArray alloc] initWithCapacity:self.movingAveragePointCount];
        
        for (NSInteger i = 0; i < self.movingAveragePointCount; ++i)
        {
            [self.movingAverageAccelX addObject:[NSNumber numberWithDouble:0]];
            [self.movingAverageAccelY addObject:[NSNumber numberWithDouble:0]];
            [self.movingAverageAccelZ addObject:[NSNumber numberWithDouble:0]];
        }
        self.index = 0;
        [self reset];
        
        self.deviceName = [[UIDevice currentDevice] name];
        self.deviceIP = [self getIPAddress];
        NSLog(@"%@",self.deviceIP);
        self.serverIP = @"192.168.222.100"; 
    }
    return self;
}

-(void) reset {
    self.deltaSX = 0;
    self.deltaSY = 0;
    self.buttonVX = 0;
    self.buttonVY = 0;
    self.buttonAX = 0;
    self.buttonAY = 0;
    
    //Rest of values are assigned per API update anyways, so it doesn't matter;
}

-(void)motionApiUpdate:(CMDeviceMotion *)motion {
    
    self.rawXRotationRate = motion.rotationRate.x;
    self.rawYRotationRate = motion.rotationRate.y;
    self.rawZRotationRate = motion.rotationRate.z;
    self.rawXUserAcceleration = motion.userAcceleration.x;
    self.rawYUserAcceleration = motion.userAcceleration.y;
    self.rawZUserAcceleration = motion.userAcceleration.z;
    self.rawXGravity = motion.gravity.x;
    self.rawYGravity = motion.gravity.y;
    self.rawZGravity = motion.gravity.z;
    self.rawRoll = motion.attitude.roll;
    self.rawPitch = motion.attitude.pitch;
    self.rawYaw = motion.attitude.yaw;
    
    
    //Remote Control-like
    //self.xAccel = self.rawZRotationRate * 1;
    //self.yAccel = self.rawXRotationRate * -1;
    
    //Linear Distance-not Accurate
    //self.xAccel = self.rawXUserAcceleration;
    //self.yAccel = self.rawYUserAcceleration;
    
    //Half-Remote/Platform-style
    self.xAccel = self.rawYRotationRate * -1;
    self.yAccel = self.rawXRotationRate * 1;
    
    //Gravity platform-style
    //self.xAccel = self.rawXGravity * -1;
    //self.yAccel = self.rawYGravity * -1;
    
    
    self.t_i = self.t_f;
    self.t_f = motion.timestamp; //motion.timestamp is time from boot, so first value is exceedingly high
    self.dt = ((self.t_f-self.t_i) < 10? (self.t_f-self.t_i): 0);
    
    //Manage moving average
    [self.movingAverageAccelX replaceObjectAtIndex:self.index withObject:[NSNumber numberWithDouble:self.xAccel]];
    [self.movingAverageAccelY replaceObjectAtIndex:self.index withObject:[NSNumber numberWithDouble:self.yAccel]];
    [self.movingAverageAccelZ replaceObjectAtIndex:self.index withObject:[NSNumber numberWithDouble:self.zAccel]];
    self.index = (self.index+1)%self.movingAveragePointCount;
    
    //Get working accelerating values
    double accelX = [self averageOfAllIn:self.movingAverageAccelX].doubleValue;
    double accelY = [self averageOfAllIn:self.movingAverageAccelY].doubleValue;
    //double accelZ = [self averageOfAllIn:self.movingAverageAccelZ].doubleValue;
    
    self.buttonAX = accelX * -10;
    self.buttonAY = accelY * -10;
    //Friction in use
    self.buttonAX -= self.buttonVX * self.friction;
    self.buttonAY -= self.buttonVY * self.friction;
    
    
    self.buttonVX = self.buttonVX + self.buttonAX * self.dt;
    self.buttonVY = self.buttonVY + self.buttonAY * self.dt;
    
    
    self.deltaSX = self.multiplier*(self.buttonVX*self.dt);
    self.deltaSY = -self.multiplier*(self.buttonVY*self.dt);
}

- (NSNumber *) averageOfAllIn:(NSMutableArray *) array {
    
    double count=0;
    
    for (NSNumber* number in array){
        count+=number.doubleValue;
    }
    return [NSNumber numberWithDouble:(count/self.movingAveragePointCount)];
    
}


- (void)initNetworkCommunication {
    
    CFStringRef server = CFBridgingRetain([NSString stringWithString:self.serverIP]);
    CFReadStreamRef readStream;
    CFWriteStreamRef writeStream;
    CFStreamCreatePairWithSocketToHost(NULL, (CFStringRef)server, 22096, &readStream, &writeStream);
    self.inputStream = (NSInputStream *)CFBridgingRelease(readStream);
    self.outputStream = (NSOutputStream *)CFBridgingRelease(writeStream);
    
    [self.inputStream setDelegate:self];
    [self.outputStream setDelegate:self];
    
    [self.inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [self.outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    
    [self.inputStream open];
    [self.outputStream open];
    self.currentStatus = QUERYINGCONNECTION;
    [self.settingsViewController connectionStatusUpdate];
    NSLog(@"Tried connecting to %@",server);
    
}

- (void)connect:(id)sender {
    
    NSString *deviceName = self.deviceName;
    
    NSString *response  = [NSString stringWithFormat:@"Connect:%@", deviceName];
    NSData *data = [[NSData alloc] initWithData:[response dataUsingEncoding:NSASCIIStringEncoding]];
    [self.outputStream write:[data bytes] maxLength:[data length]];
    
};

- (void)sendData:(id)sender {
    
    NSString *message = @"hi";
    
    NSString *response  = [NSString stringWithFormat:@"msg:%@", message];
    NSData *data = [[NSData alloc] initWithData:[response dataUsingEncoding:NSASCIIStringEncoding]];
    [self.outputStream write:[data bytes] maxLength:[data length]];
}

- (void)stream:(NSStream *)theStream handleEvent:(NSStreamEvent)streamEvent {
    
    switch (streamEvent) {
            
        case NSStreamEventHasBytesAvailable:
            
            if (theStream == self.inputStream) {
                
                uint8_t buffer[1024];
                int len;
                
                while ([self.inputStream hasBytesAvailable]) {
                    len = [self.inputStream read:buffer maxLength:sizeof(buffer)];
                    if (len > 0) {
                        
                        NSString *output = [[NSString alloc] initWithBytes:buffer length:len encoding:NSASCIIStringEncoding];
                        
                        if (nil != output) {
                            NSLog(@"server said: %@", output);
                            [self messageReceived:output];
                        }
                    }
                }
            }
            break;
        
        case NSStreamEventOpenCompleted:
            NSLog(@"Stream opened");
            self.currentStatus = CONNECTED;
            [self.settingsViewController connectionStatusUpdate];
            break;
            
        case NSStreamEventErrorOccurred:
            NSLog(@"Cannot connect to the host!");
            self.currentStatus = UNABLETOCONNECT;
            [self.settingsViewController connectionStatusUpdate];
            break;
            
        case NSStreamEventEndEncountered:
            [self disconnect:nil];
            [self.settingsViewController connectionStatusUpdate];
            break;
            
        case NSStreamEventHasSpaceAvailable:
            break;
            
        case NSStreamEventNone:
            break;
            
        default:
            NSLog(@"%lu",streamEvent);
            NSLog(@"Unknown event");
    }
    
}

- (void) disconnect:(id)sender {
    [self.inputStream close];
    [self.inputStream removeFromRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [self.outputStream close];
    [self.outputStream removeFromRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    self.currentStatus = NOTCONNECTED;
    [self.settingsViewController connectionStatusUpdate];
}

- (void) messageReceived:(NSString *)message {
    
}

// Gotta give credits:
//http://stackoverflow.com/questions/6807788/how-to-get-ip-address-of-iphone-programatically
- (NSString *)getIPAddress {
    
    NSString *address = @"error";
    struct ifaddrs *interfaces = NULL;
    struct ifaddrs *temp_addr = NULL;
    int success = 0;
    // retrieve the current interfaces - returns 0 on success
    success = getifaddrs(&interfaces);
    if (success == 0) {
        // Loop through linked list of interfaces
        temp_addr = interfaces;
        while(temp_addr != NULL) {
            if(temp_addr->ifa_addr->sa_family == AF_INET) {
                // Check if interface is en0 which is the wifi connection on the iPhone
                if([[NSString stringWithUTF8String:temp_addr->ifa_name] isEqualToString:@"en0"]) {
                    // Get NSString from C String
                    address = [NSString stringWithUTF8String:inet_ntoa(((struct sockaddr_in *)temp_addr->ifa_addr)->sin_addr)];
                    
                }
                
            }
            
            temp_addr = temp_addr->ifa_next;
        }
    }
    // Free memory
    freeifaddrs(interfaces);
    return address;
    
}


@end
