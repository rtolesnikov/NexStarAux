import numpy as np
import cv2

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
cap = cv2.VideoCapture(0)
# Capture frame-by-frame
ret, frame = cap.read()

# Our operations on the frame come here
img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
print(img.shape)


cv2.namedWindow('image')
cv2.setMouseCallback('image',zoom_region)
for i in range(5):
    (x,y) = pick_list[i]
    x_min = max(x - half_zoom_size, 0)
    x_max = min(x + half_zoom_size, img.shape[0])
    y_min = max(y - half_zoom_size, 0)
    y_max = min(y + half_zoom_size, img.shape[1])
    # print(x_min, x_max, y_min, y_max)
    cv2.imshow("Zoom %d"%i, cv2.resize(img[y_min:y_max+1, x_min:x_max+1], None, fx=2, fy=2))
    cv2.moveWindow("Zoom %d"%i, 100, 20 + i * 2 * zoom_factor * (10+half_zoom_size) )


cv2.imshow('image',img)
k = cv2.waitKey(20) & 0xFF

while k != ord('x'):
    if k == ord('1'):
        current_pick = 0
        print ("Current zoom select: %d"%(current_pick+1))
    if k == ord('2'):
        current_pick = 1
        print ("Current zoom select: %d"%(current_pick+1))
    if k == ord('3'):
        current_pick = 2
        print ("Current zoom select: %d"%(current_pick+1))
    if k == ord('4'):
        current_pick = 3
        print ("Current zoom select: %d"%(current_pick+1))
    if k == ord('5'):
        current_pick = 4
        print ("Current zoom select: %d"%(current_pick+1))
    #Draw full window
    ret, frame = cap.read()
    # Our operations on the frame come here
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('image',img)
    # Draw zoom windows at 200% zoom
    for i in range(5):
        (x,y) = pick_list[i]
        if x != -1:
            x_min = max(x - half_zoom_size, 0)
            x_max = min(x + half_zoom_size, img.shape[1])
            y_min = max(y - half_zoom_size, 0)
            y_max = min(y + half_zoom_size, img.shape[0])
            # print(x_min, x_max, y_min, y_max)
            cv2.imshow("Zoom %d"%i, cv2.resize(img[y_min:y_max+1, x_min:x_max+1], None, fx=zoom_factor, fy=zoom_factor))
        
    k = cv2.waitKey(20) & 0xFF

cv2.destroyAllWindows()
