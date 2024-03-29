#!/usr/bin/env python
import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# This runs in coamo environment at the moment due to difficult cv2 (open CV) dependency

current_pick = -1
pick_list = [(0,0)] * 5  # Keey a set of x,y tuples for each active window, init to center
half_zoom_size = 25 # one-half size of the zoom window.
zoom_factor = 3

def zoom_region(event,x,y,flags,param):
    global current_pick, pick_list 
    if current_pick != -1 and event == cv2.EVENT_LBUTTONDBLCLK:
        pick_list[current_pick] = (x,y)
        # print(pick_list)

# Load an color image in grayscale
# img = cv2.imread('M67-005_10sec.png',0)
_size = (1920, 1088)
camera = PiCamera()
camera.resolution = _size
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=_size)

# allow the camera to warmup
time.sleep(0.1)
img = np.zeros(_size, dtype=np.uint8)

cv2.namedWindow('image')
cv2.setMouseCallback('image',zoom_region)
for i in range(5):
    (x,y) = pick_list[i]
    x_min = max(x - half_zoom_size, 0)
    x_max = min(x + half_zoom_size, img.shape[0])
    y_min = max(y - half_zoom_size, 0)
    y_max = min(y + half_zoom_size, img.shape[1])
    # print(x_min, x_max, y_min, y_max)
    cv2.imshow("Zoom %d"%i, cv2.resize(img[y_min:y_max+1, x_min:x_max+1], None, fx=zoom_factor, fy=zoom_factor))
    cv2.moveWindow("Zoom %d"%i, 100, 20 + i * 2 * zoom_factor * (10+half_zoom_size) )


k = cv2.waitKey(20) & 0xFF

for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    img = cv2.cvtColor(frame.array, cv2.COLOR_RGB2GRAY)

    # show the frame
    cv2.imshow("image", cv2.resize(img, None, fx=0.25, fy=0.25))

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    
    if k == ord('1'):
        current_pick = 0
        print ("Current zoom select: %d"%(current_pick+1))
    elif k == ord('2'):
        current_pick = 1
        print ("Current zoom select: %d"%(current_pick+1))
    elif k == ord('3'):
        current_pick = 2
        print ("Current zoom select: %d"%(current_pick+1))
    elif k == ord('4'):
        current_pick = 3
        print ("Current zoom select: %d"%(current_pick+1))
    elif k == ord('5'):
        current_pick = 4
        print ("Current zoom select: %d"%(current_pick+1))
    elif k == ord('x'):
        break
    # Draw zoom windows at 200% zoom
    for i in range(5):
        (x,y) = pick_list[i]
        if x != -1:
            x_min = max(x - half_zoom_size, 0)
            x_max = min(x + half_zoom_size, img.shape[0])
            y_min = max(y - half_zoom_size, 0)
            y_max = min(y + half_zoom_size, img.shape[1])
            # print(x_min, x_max, y_min, y_max)
            cv2.imshow("Zoom %d"%i, cv2.resize(img[y_min:y_max+1, x_min:x_max+1], None, fx=zoom_factor, fy=zoom_factor))
        
    k = cv2.waitKey(20) & 0xFF

cv2.destroyAllWindows()
