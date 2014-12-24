//
//  SettingsViewController.h
//  mouselet
//
//  Created by Kye on 2014-12-23.
//  Copyright (c) 2014 Kye. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "mouseletData.h"

@interface SettingsViewController : UITableViewController <UITextFieldDelegate>

@property mouseletData* myData;

- (void) setData:(mouseletData*) newData;

@property (weak, nonatomic) IBOutlet UILabel *clientName;
@property (weak, nonatomic) IBOutlet UILabel *clientIP;
@property (weak, nonatomic) IBOutlet UITextField *serverIP;


@property (weak, nonatomic) IBOutlet UILabel *connectionStatus;

- (IBAction)serverIPChange:(id)sender;

@property (weak, nonatomic) IBOutlet UIButton *requestButton;
- (IBAction)sendButtonRequest:(id)sender;

- (void) connectionStatusUpdate;

@end
