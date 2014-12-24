//
//  SettingsViewController.h
//  mouselet
//
//  Created by Kye on 2014-12-23.
//  Copyright (c) 2014 Kye. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "mouseletData.h"

@interface SettingsViewController : UITableViewController

@property NSArray *settingsOptions;
@property NSArray *settingsOptionsDefaults;
@property NSArray *settingsButtons;
@property mouseletData* myData;

- (void) setData:(mouseletData*) newData;


@end
