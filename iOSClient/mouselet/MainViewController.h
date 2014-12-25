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


//Since Autolayout prevented me from directly editing the mouseball's position, a CGRect called frame, so
// I had to edit the constraint holding the mouseball. It worked out.
@property (weak, nonatomic) IBOutlet NSLayoutConstraint *CircleX;
@property (weak, nonatomic) IBOutlet NSLayoutConstraint *CircleY;

//Slightly gray subview
@property (weak, nonatomic) IBOutlet UIView *subview;

//CoreMotion API
@property (nonatomic, strong) CMMotionManager *motionManager;


//Output UILabels
@property (nonatomic, strong) IBOutlet UILabel *timeChange;
@property (nonatomic, strong) IBOutlet UILabel *xAxisAccel;
@property (nonatomic, strong) IBOutlet UILabel *yAxisAccel;

//Emulated mouse-ball
@property (nonatomic, strong) IBOutlet UILabel *buttonO;



//Multiplier: default 2.47712 (300), from (1) 10 to (4) 10000
@property (weak, nonatomic) IBOutlet UISlider *MultiplierSlider;
- (IBAction)multiplierChanged:(id)sender;
@property (weak, nonatomic) IBOutlet UILabel *MultiplierText;


//Friction: default 0 (1), from (-1) 0.1 to (2) 100
@property (weak, nonatomic) IBOutlet UISlider *FrictionSlider;
- (IBAction)frictionChanged:(id)sender;
@property (weak, nonatomic) IBOutlet UILabel *FrictionText;


- (void) setData:(mouseletData*) newData;

- (IBAction)LMBTouchDown:(id)sender;

- (IBAction)LMBTouchUp:(id)sender;

@end

