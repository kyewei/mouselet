//
//  mouseletData.h
//  mouselet
//
//  Created by Kye on 2014-12-23.
//  Copyright (c) 2014 Kye. All rights reserved.
//

//This class controls the raw data collected, as well as sends it to a server



#import <Foundation/Foundation.h>
#import <CoreMotion/CoreMotion.h>
#import <UIKit/UIKit.h>

@interface mouseletData : NSObject <NSStreamDelegate>

@property NSInputStream *inputStream;
@property NSOutputStream *outputStream;


//Device Info
@property NSString* deviceName;
@property NSString* deviceIP;
- (NSString*) deviceStatus;
@property NSString* serverIP;

//Ready or not?
@property bool isConnectedToServer;

//Raw data
@property double rawXRotationRate;
@property double rawYRotationRate;
@property double rawZRotationRate;
@property double rawXUserAcceleration;
@property double rawYUserAcceleration;
@property double rawZUserAcceleration;
@property double rawXGravity;
@property double rawYGravity;
@property double rawZGravity;
@property double rawRoll;
@property double rawPitch;
@property double rawYaw;


//Track time passing
@property double t_i;
@property double t_f;
@property double dt;


//Moving average to smooth out data (somewhat)
@property (nonatomic, strong) NSMutableArray *movingAverageAccelX;
@property (nonatomic, strong) NSMutableArray *movingAverageAccelY;
@property (nonatomic, strong) NSMutableArray *movingAverageAccelZ;
@property int index;
@property int movingAveragePointCount;
- (NSNumber *) averageOfAllIn:(NSMutableArray *) array;


//Processed Acceleration
@property double xAccel;
@property double yAccel;
@property double zAccel;

//Multiplier: default 2.47712 (300), from (1) 10 to (4) 10000
@property double multiplier;

//Friction: default 0 (1), from (-1) 0.1 to (2) 100
@property double friction;


//Kinematics
@property double deltaSX;
@property double deltaSY;
@property double buttonSX;
@property double buttonSY;
@property double buttonVX;
@property double buttonVY;
@property double buttonAX;
@property double buttonAY;

-(void)reset;

-(void)motionApiUpdate:(CMDeviceMotion *)motion;



@end
