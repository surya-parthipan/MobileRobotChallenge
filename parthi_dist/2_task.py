import cv2
import numpy as np
import picamera
import picamera.array
from time import sleep
import time

import ZeroBorg

ZB = ZeroBorg.ZeroBorg()

# Parameters
KNOWN_WIDTH = 10 # The actual width of the object in centimeters (change this to your target object width)
FOCAL_LENGTH = 250 # The focal length of the camera in pixels (change this to your camera's focal length)

def distance_to_camera(known_width, focal_length, per_width):
    return (known_width * focal_length) / per_width

def detect_object(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7,7), 0)
    # Apply edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out small contours
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]



# Variables
xPos = 0;
steerMultiplier = 0.8

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                   # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print ('No ZeroBorg found, check you are attached :)')
    else:
        print ('No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress))
        for board in boards:
            print ('    %02X (%d)' % (board, board))
        print ('If you need to change the IC address change the setup line so it is correct, e.g.')
        print ('ZB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()
#ZB.SetEpoIgnore(True)                  # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.SetCommsFailsafe(False)              # Disable the communications failsafe
ZB.ResetEpo()

# Movement settings (worked out from our YetiBorg v2 on a smooth surface)
timeForward1m = 5.7                     # Number of seconds needed to move about 1 meter
timeSpin360   = 4.8                     # Number of seconds needed to make a full left / right spin
testMode = False                        # True to run the motion tests, False to run the normal sequence

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Function to perform a general movement
def PerformMove(driveLeft, driveRight, numSeconds):
    # Set the motors running
    ZB.SetMotor1(-driveRight * maxPower) # Rear right
    ZB.SetMotor2(-driveRight * maxPower) # Front right
    ZB.SetMotor3(-driveLeft  * maxPower) # Front left
    ZB.SetMotor4(-driveLeft  * maxPower) # Rear left
    # Wait for the time
    time.sleep(numSeconds)
    # Turn the motors off
    ZB.MotorsOff()

def cal_time(dist):
    calib = 45.0 # 40.0 or 35.0 
    print(dist/calib)
    return dist/calib

#PerformMove(1,1, cal_time(100))
#time.sleep(1)
PerformMove(0.5,0,0.5)
#time.sleep(1)
#PerformMove(0.5,0.5,1)
#time.sleep(1)
#PerformMove(0.5,0,1.5)
#time.sleep(1)
#PerformMove(0.5,0.5, 1)
#time.sleep(1)
#PerformMove(0,0.5,1)
#time.sleep(0.5)
#PerformMove(0.5,0.5,1)
