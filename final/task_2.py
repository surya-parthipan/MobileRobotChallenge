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

    # Sort contours by area and choose the largest one
    if filtered_contours:
        largest_contour = max(filtered_contours, key=cv2.contourArea)
        return largest_contour
    else:
        return None

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (640,480)
        camera.framerate = 32

        sleep(2)  # Camera warm-up time
        count_flag = 0
        dist_array = []
        while True:
            camera.capture(stream, 'bgr', use_video_port=True)
            image = stream.array
            image = cv2.flip(image, -1)
            y=0
            x=0
            h=100
            w=200
            #image = image[y:y+h, x:x+w]

            #height, width, channels = image.shape
            #image = image[int(height / 2):height, 0:width]

            center = image.shape
            x = center[1]/2 - w/2
            y = center[0]/2 - h/2

	    image = image[int(y):int(y+h), int(x):int(x+w)]
        # let's upscale the image using new  width and height
        #up_width = 640
        #up_height = 480
        #up_points = (up_width, up_height)
        #image = cv2.resize(image, up_points, interpolation= cv2.INTER_LINEAR)
            object_contour = detect_object(image)

            if object_contour is not None:
		peri = cv2.arcLength(object_contour, True)
		approx = cv2.approxPolyDP(object_contour, 0.03 * peri, True)
                # Calculate object width in pixels
                x, y, w, h = cv2.boundingRect(approx)
                # Calculate distance to object
                distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, w)
                dist_array.append(distance)
                count_flag += 1
                # Draw a bounding box around the object and display the distance
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, str(distance), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                #cv2.putText(image, f"{distance:.1f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Show the image
            cv2.imshow('Object Detection and Distance Measurement', image)

            # Reset the stream before the next capture
            stream.truncate(0)

            # Break the loop if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q') or count_flag > 40:
                print(np.round(dist_array))
                #find unique values in array along with their counts
                vals, counts = np.unique(dist_array, return_counts=True)
                #find mode
                mode_value = np.argwhere(counts == np.max(counts))
                mode_values = vals[mode_value]
                distance_measured = np.mean(mode_values)
                
                print(mode_values)
                print(distance_measured)
                break
            
cv2.destroyAllWindows()

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

PerformMove(1,1, cal_time(distance_measured))
time.sleep(1)
PerformMove(0,0.5,0.5)
#time.sleep(1)
PerformMove(0.5,0.5,1)
#time.sleep(1)
PerformMove(0.5,0,1.5)
#time.sleep(1)
PerformMove(0.5,0.5, 1)
#time.sleep(1)
PerformMove(0,0.5,1)
#time.sleep(0.5)
PerformMove(0.5,0.5,cal_time(200-distance_measured))
