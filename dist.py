import cv2
import numpy as np
import picamera
import picamera.array
from time import sleep
import time

import ZeroBorg

ZB = ZeroBorg.ZeroBorg()

# Parameters
KNOWN_WIDTH = 16.0 # The actual width of the object in centimeters (change this to your target object width)
FOCAL_LENGTH = 500 # The focal length of the camera in pixels (change this to your camera's focal length)
focal_length = 50

object_width = 16  
def distance_to_camera(known_width, focal_length, per_width):
    return (known_width * focal_length) / per_width

def detect_object(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)

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
distances = []
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
            frame = cv2.flip(image, -1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            blurred = cv2.GaussianBlur(gray, (7, 7), 0)

            edges = cv2.Canny(blurred, 50, 150)

            contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)

                if area < 500:
                    continue

                perimeter = cv2.arcLength(contour, True)

                approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)

                x, y, w, h = cv2.boundingRect(approx)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                distance = (object_width * focal_length) / w

                cv2.putText(frame, str(distance), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                distances.append(distance)
	stream.truncate()
        stream.seek(0)
        cv2.imshow("Frame", frame)

    # if len(distances) > 10:
    #     break

        print(distances)
        cv2.destroyAllWindows()
