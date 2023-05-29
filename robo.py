import cv2
import numpy as np
import picamera
import picamera.array
from time import sleep
import time

import ZeroBorg

ZB = ZeroBorg.ZeroBorg()
# cam = cv2.VideoCapture(0)

# cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

focal_length = 50

object_width = 16  # cm
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
            image = cv2.flip(image, -1)
    
            # ret, frame = cam.read()

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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

                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                distance = (object_width * focal_length) / w

                cv2.putText(image, str(distance), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                distances.append(distance)

            cv2.imshow("Frame", image)

            if cv2.waitKey(1) == ord('q'):
                break

print(distances)
# cam.release()
cv2.destroyAllWindows()
