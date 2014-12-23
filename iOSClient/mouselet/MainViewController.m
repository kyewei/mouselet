//
//  ViewController.m
//  mouselet
//
//  Created by Kye on 2014-12-19.
//  Copyright (c) 2014 Kye. All rights reserved.
//

#import "MainViewController.h"
#import <math.h>

@interface MainViewController ()

@end

@implementation MainViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    
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
    
    self.needToResetMouse = true; //clears and resets values;
    
    self.motionManager = [[CMMotionManager alloc] init];
    self.motionManager.deviceMotionUpdateInterval = 0.001;
    
    
    if ([self.motionManager isDeviceMotionAvailable])
    {
        NSOperationQueue *queue = [[NSOperationQueue alloc] init];
        [self.motionManager startDeviceMotionUpdatesToQueue:queue withHandler:^(CMDeviceMotion *motion, NSError *error) {
            dispatch_async(dispatch_get_main_queue(), ^{
                
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
                
                if (self.needToResetMouse){
                    [self resetMouse:nil];
                    self.needToResetMouse = false;
                }
                
                //Remote Control-like
                //self.xAccel = self.rawZRotationRate * 1;
                //self.yAccel = self.rawXRotationRate * -1;
                
                //Linear Distance-not Accurate
                //self.xAccel = self.rawXUserAcceleration;
                //self.yAccel = self.rawYUserAcceleration;
                
                //Platform-style
                self.xAccel = self.rawYRotationRate * -1;
                self.yAccel = self.rawXRotationRate * 1;
                
                
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
                
                self.buttonSX = self.CircleX.constant + self.deltaSX;
                self.buttonSY = self.CircleY.constant + self.deltaSY;
                
                
                //Boundaries of Screen
                if (self.buttonSX<0) {
                    //self.buttonSX *=-1;
                    //self.buttonVX *=-1;
                    self.buttonSX=0;
                }
                else if (self.buttonSX > self.subview.frame.size.width) {
                    //self.buttonSX -= 2*(self.buttonSX - self.subview.frame.size.width);
                    self.buttonSX = self.subview.frame.size.width;
                    //self.buttonVX *=-1;
                }
                
                if (self.buttonSY<0) {
                    //self.buttonSY *=-1;
                    //self.buttonVY *=-1;
                    self.buttonSY=0;
                }
                else if (self.buttonSY > self.subview.frame.size.height) {
                    //self.buttonSY -= 2*(self.buttonSY - self.subview.frame.size.height);
                    self.buttonSY = self.subview.frame.size.height;
                    //self.buttonVY *=-1;
                }
                self.CircleX.constant = self.buttonSX;
                self.CircleY.constant = self.buttonSY;
                
                
                self.timeChange.text = [NSString stringWithFormat:@"%.10f", self.dt];
                
                
                self.xAxisAccel.text = [NSString stringWithFormat:@"%.10f",self.buttonAX];
                self.yAxisAccel.text = [NSString stringWithFormat:@"%.10f",self.buttonAY];
                //self.zAxisAccel.text = [NSString stringWithFormat:@"%.10f",self.buttonAZ];
            });
        }];
    } else
        NSLog(@"Motion not active");
    
}

- (NSNumber *) averageOfAllIn:(NSMutableArray *) array {
    
    double count=0;
    
    for (NSNumber* number in array){
        count+=number.doubleValue;
    }
    return [NSNumber numberWithDouble:(count/self.movingAveragePointCount)];
    
}

- (IBAction)resetMouse:(id)sender{
    self.buttonSX = self.subview.frame.size.width/2;
    self.buttonSY = self.subview.frame.size.height/2;
    self.deltaSX = 0;
    self.deltaSY = 0;
    self.buttonVX = 0;
    self.buttonVY = 0;
    self.buttonAX = 0;
    self.buttonAY = 0;
    
    self.CircleX.constant = self.subview.frame.size.width/2;
    self.CircleY.constant = self.subview.frame.size.height/2;
}

/*- (void) handleDeviceMotion:(CMDeviceMotion *)m atTime:(NSDate *)time
{
    // calculate user acceleration in the direction of gravity
    double verticalAcceleration = m.gravity.x * m.userAcceleration.x +
    m.gravity.y * m.userAcceleration.y +
    m.gravity.z * m.userAcceleration.z;
    
    // update the bias in low pass filter (bias is an object variable)
    double delta = verticalAcceleration - bias;
    if (ABS(delta) < 0.1) bias += 0.01 * delta;
    
    // remove bias from user acceleration
    CMAcceleration acceleration;
    acceleration.x = m.userAcceleration.x - bias * m.gravity.x;
    acceleration.y = m.userAcceleration.y - bias * m.gravity.y;
    acceleration.z = m.userAcceleration.z - bias * m.gravity.z;
    
    // do something with acceleration
}*/



- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)multiplierChanged:(id)sender {
    self.multiplier = pow(10,self.MultiplierSlider.value);
    self.MultiplierText.text = [NSString stringWithFormat:@"%.2f",self.multiplier];
}
- (IBAction)frictionChanged:(id)sender {
    self.friction = pow(10,self.FrictionSlider.value);
    self.FrictionText.text = [NSString stringWithFormat:@"%.2f",self.friction];
}
@end
