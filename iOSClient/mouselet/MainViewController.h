//
//  ViewController.h
//  mouselet
//
//  Created by Kye on 2014-12-19.
//  Copyright (c) 2014 Kye. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreMotion/CoreMotion.h>
#import "mouseletData.h"

@interface MainViewController : UIViewController


@property mouseletData* myData;

//Mouse reset to center
@property bool needToResetMouse;
- (IBAction)resetMouse:(id)sender;

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


//Since Autolayout prevented me from directly editing the mouseball's position, a CGRect called frame, so
// I had to edit the constraint holding the mouseball. It worked out.
@property (weak, nonatomic) IBOutlet NSLayoutConstraint *CircleX;
@property (weak, nonatomic) IBOutlet NSLayoutConstraint *CircleY;

//Slightly gray subview
@property (weak, nonatomic) IBOutlet UIView *subview;

//CoreMotion API
@property (nonatomic, strong) CMMotionManager *motionManager;

//Track time passing
@property double t_i;
@property double t_f;
@property double dt;

//Output UILabels
@property (nonatomic, strong) IBOutlet UILabel *timeChange;
@property (nonatomic, strong) IBOutlet UILabel *xAxisAccel;
@property (nonatomic, strong) IBOutlet UILabel *yAxisAccel;
@property (nonatomic, strong) IBOutlet UILabel *zAxisAccel;

//Emulated mouse-ball
@property (nonatomic, strong) IBOutlet UILabel *buttonO;

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
@property (weak, nonatomic) IBOutlet UISlider *MultiplierSlider;
- (IBAction)multiplierChanged:(id)sender;
@property (weak, nonatomic) IBOutlet UILabel *MultiplierText;
@property double multiplier;

//Friction: default 0 (1), from (-1) 0.1 to (2) 100
@property (weak, nonatomic) IBOutlet UISlider *FrictionSlider;
- (IBAction)frictionChanged:(id)sender;
@property (weak, nonatomic) IBOutlet UILabel *FrictionText;
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


- (void) setData:(mouseletData*) newData;


@end

