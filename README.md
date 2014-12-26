mouselet
========

"mouselet" is an iOS Client App and TCP Server combination that allows an iPod touch/iPhone to control a computer's cursor like a mouse.
To control the computer, start the server, connect to the server's IP through the iOS app, and then rotate the iDevice.
The on-device gyroscope tracks and controls the mouse cursor.

###How to Run
To run the server, run either ``` python server.py ``` or ``` chmod +x server.py && ./server.py ``` depending on platform.

A working installation of python 2.x is required. 
The server can run on: 
* Mac OS X (tested: 10.9.5 Mavericks)
* Windows (tested: 7 & 8) 
* Most Linux distros (tested: Arch Linux)

The socket TCP server runs on port ```22096```.

On Linux variants, the respective Python 2 X Library (``` python2-xlib ```  for Arch in the AUR) is needed also.
Although the iOS app will probably not be in the App Store ($100 fee for iOS Developer Program), the Xcode source is hosted here, and can be compiled. 
I might also upload an .ipa for jailbroken devices.


###Operation and Mouse Control 
There are two numeric settings, one for the multiplier, which is how much a unit turn is multiplied into screen pixel distance.
The second is the grip/friction, which is how quick the mouse velocity decreases over time. 
These can be adjusted with the 2 sliders.

There are 4 primary control styles which are more or less accurate, and an experimental style that is highly inaccurate.
The first 4 depend on rotation rate of the iDevice, while the last style tries to calculate the distance the iDevice slides over a flat surface (hence the inaccuracy).
All depend on double integration of the the respective acceleration.

* Ball-Rolling Platform Style
* Sideways Platform Style
* Remote Control Style
* Gravity Platform Style
* Traditional Mouse (highly inaccurate, only implemented because a mouse is a mouse after all)

There is also a reset button that resets and centers the cursor in the middle of the screen.
