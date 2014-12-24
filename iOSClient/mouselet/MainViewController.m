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
    
    self.myData = [[mouseletData alloc] init];
    self.myData.mainViewController = self;
    
    self.needToResetMouse = true;
    self.motionManager = [[CMMotionManager alloc] init];
    self.motionManager.deviceMotionUpdateInterval = 0.001;
    
    if ([self.motionManager isDeviceMotionAvailable])
    {
        NSOperationQueue *queue = [[NSOperationQueue alloc] init];
        [self.motionManager startDeviceMotionUpdatesToQueue:queue withHandler:^(CMDeviceMotion *motion, NSError *error) {
            dispatch_async(dispatch_get_main_queue(), ^{
                
                if (self.needToResetMouse){
                    [self resetMouse:nil];
                    self.needToResetMouse = false;
                }

                //Tell model to update based on data from motion API
                [self.myData motionApiUpdate:motion];
                
                //Compute new boundaries of circle
                double newCircleX = self.CircleX.constant + self.myData.deltaSX;
                double newCircleY = self.CircleY.constant + self.myData.deltaSY;
                
                
                //Boundaries of Screen
                if (newCircleX<0) {
                    newCircleX=0;
                }
                else if (newCircleX > self.subview.frame.size.width) {
                    newCircleX = self.subview.frame.size.width;
                }
                
                if (newCircleY<0) {
                    newCircleY=0;
                }
                else if (newCircleY > self.subview.frame.size.height) {
                    newCircleY = self.subview.frame.size.height;
                }
                
                //Assign
                self.CircleX.constant = newCircleX;
                self.CircleY.constant = newCircleY;
                
                self.timeChange.text = [NSString stringWithFormat:@"%.10f",self.myData.dt];
                self.xAxisAccel.text = [NSString stringWithFormat:@"%.10f",self.myData.buttonAX];
                self.yAxisAccel.text = [NSString stringWithFormat:@"%.10f",self.myData.buttonAY];
                
                //self.zAxisAccel.text = [NSString stringWithFormat:@"%.10f",self.buttonAZ];
                
            });
        }];
    } else
        NSLog(@"Motion not active");
    
}


- (IBAction)resetMouse:(id)sender{
    [self.myData reset];
    
    self.CircleX.constant = self.subview.frame.size.width/2;
    self.CircleY.constant = self.subview.frame.size.height/2;
}



- (void) setData:(mouseletData*) newData {
    self.myData = newData;
}


- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)multiplierChanged:(id)sender {
    self.myData.multiplier = pow(10,self.MultiplierSlider.value);
    self.MultiplierText.text = [NSString stringWithFormat:@"%.2f",self.myData.multiplier];
}
- (IBAction)frictionChanged:(id)sender {
    self.myData.friction = pow(10,self.FrictionSlider.value);
    self.FrictionText.text = [NSString stringWithFormat:@"%.2f",self.myData.friction];
}



#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    //This is only called when main view -> settings
    //I need to send my model so it is sent using this
    
    
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
    if ([segue.destinationViewController respondsToSelector:@selector(setData:)]) {
        [segue.destinationViewController performSelector:@selector(setData:) withObject:self.myData];
        
    }
}


@end
