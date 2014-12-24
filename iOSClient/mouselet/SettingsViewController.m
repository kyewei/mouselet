//
//  SettingsViewController.m
//  mouselet
//
//  Created by Kye on 2014-12-23.
//  Copyright (c) 2014 Kye. All rights reserved.
//

#import "SettingsViewController.h"

@interface SettingsViewController ()

@end

@implementation SettingsViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    NSLog(@"Settings loaded!");
    
    self.myData.settingsViewController = self;
    
    self.clientName.text = self.myData.deviceName;
    self.clientIP.text = self.myData.deviceIP;
    self.serverIP.text = self.myData.serverIP;
    [self.serverIP setDelegate:self];
    [self connectionStatusUpdate];
    
    // Uncomment the following line to preserve selection between presentations.
    // self.clearsSelectionOnViewWillAppear = NO;
    
    // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
    // self.navigationItem.rightBarButtonItem = self.editButtonItem;
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - Table view data source

/*- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
#warning Potentially incomplete method implementation.
    // Return the number of sections.
    return 2;
}*/

/*- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
#warning Incomplete method implementation.
    // Return the number of rows in the section.
    //return 0;
    if (section ==0)
        return self.settingsOptions.count;
    else //if (section ==1) {
        return self.settingsButtons.count;
}*/


/*- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    NSString *reuseCellIdentifier = (indexPath.section ==0? @"userChangeCell": @"actionCell");
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:reuseCellIdentifier forIndexPath:indexPath];
    
    // Configure the cell...
    
    if (cell == nil) {
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleValue1 reuseIdentifier:reuseCellIdentifier];
    }
    
    if (indexPath.section ==0) {
        cell.textLabel.text = [self.settingsOptions objectAtIndex:indexPath.row];
        cell.detailTextLabel.text = [self.settingsOptionsDefaults objectAtIndex:indexPath.row];
    } else {//if (indexPath.section ==1)
        cell.textLabel.text = [self.settingsButtons objectAtIndex:indexPath.row];
        cell.detailTextLabel.text = @"hmm";
    }
    return cell;
}*/

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    [tableView deselectRowAtIndexPath:indexPath animated:NO];
    
    //[tableView reloadRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationNone];
}

/*
// Override to support conditional editing of the table view.
- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
    // Return NO if you do not want the specified item to be editable.
    return YES;
}
*/

/*
// Override to support editing the table view.
- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        // Delete the row from the data source
        [tableView deleteRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationFade];
    } else if (editingStyle == UITableViewCellEditingStyleInsert) {
        // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
    }   
}
*/

/*
// Override to support rearranging the table view.
- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath {
}
*/

/*
// Override to support conditional rearranging of the table view.
- (BOOL)tableView:(UITableView *)tableView canMoveRowAtIndexPath:(NSIndexPath *)indexPath {
    // Return NO if you do not want the item to be re-orderable.
    return YES;
}
*/

- (void) setData:(mouseletData*) newData {
    
    self.myData = newData;
}

#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
    if ([segue.destinationViewController respondsToSelector:@selector(setData:)]) {
        [segue.destinationViewController performSelector:@selector(setData:) withObject:self.myData];
    }
}


- (IBAction)serverIPChange:(id)sender{
    [self.myData disconnect:nil];
    self.myData.serverIP = self.serverIP.text;
    self.myData.currentStatus = NOTCONNECTED;
    NSLog(@"Updated: %@",self.serverIP.text);
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
    if( [[textField text] isEqualToString:self.serverIP.text] ) {
        [self serverIPChange:nil];
    }
    NSLog(@"Resign");
    [textField resignFirstResponder];
    return NO;
}


- (IBAction)sendButtonRequest:(id)sender {
    connectionStatus status = self.myData.currentStatus;
    switch (status){
        case CONNECTED:
            [self.myData disconnect:nil];
            break;
        case NOTCONNECTED:
            [self.myData initNetworkCommunication];
            break;
        case UNABLETOCONNECT:
            break;
        case QUERYINGCONNECTION:
            [self.myData disconnect:nil];
        default:
            break;
    }
}

- (void) connectionStatusUpdate {
    connectionStatus status = self.myData.currentStatus;
    switch (status) {
        case CONNECTED:
            self.connectionStatus.text = @"Connected";
            self.requestButton.enabled = YES;
            [self.requestButton setTitle:@"Disconnect!" forState:UIControlStateNormal];
            break;
        case NOTCONNECTED:
            self.connectionStatus.text = @"Disconnected";
            self.requestButton.enabled = YES;
            [self.requestButton setTitle:@"Connect!" forState:UIControlStateNormal];
            break;
        case UNABLETOCONNECT:
            self.connectionStatus.text = @"Error";
            self.requestButton.enabled = NO;
            [self.requestButton setTitle:@"Connect!" forState:UIControlStateNormal];
            break;
        case QUERYINGCONNECTION:
            self.connectionStatus.text = @"Connecting...";
            self.requestButton.enabled = YES;
            [self.requestButton setTitle:@"Cancel" forState:UIControlStateNormal];
            break;
        default:
            break;
    }
    
    
}

@end
