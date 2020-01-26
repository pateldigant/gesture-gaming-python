# directkeys.py is taken from https://stackoverflow.com/questions/14489013/simulate-python-keypresses-for-controlling-a-game
# inspired from pyimagesearch ball tracking https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from directkeys import  W, A, S, D
from directkeys import PressKey, ReleaseKey 

# define the lower and upper boundaries of the "orange" object in the HSV color space
orangeLower = np.array([0, 129, 100])
orangeUpper = np.array([180,255,255])

vs = VideoStream(src=0).start()
 
# allow the camera or video file to warm up
time.sleep(2.0)
initial = True
flag = False
current_key_pressed = set()
circle_radius = 30
windowSize = 160
lr_counter = 0
# keep looping
while True:
    keyPressed = False
    keyPressed_lr = False
    # grab the current frame
    frame = vs.read()
    height,width = frame.shape[:2]
 
    # resize the frame, blur it, and convert it to the HSV color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # crteate a mask for the orange color and perform dilation and erosion to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
 
    # find contours in the mask and initialize the current
    # (x, y) center of the orange object

    # divide the frame into two halves so that we can have one half control the acceleration/brake 
    # and other half control the left/right steering.
    left_mask = mask[:,0:width//2,]
    right_mask = mask[:,width//2:,]

    #find the contours in the left and right frame to find the center of the object
    cnts_left = cv2.findContours(left_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_left = imutils.grab_contours(cnts_left)
    center_left = None

    cnts_right = cv2.findContours(right_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_right = imutils.grab_contours(cnts_right)
    center_right = None
 
    # only proceed if at least one contour was found
    if len(cnts_left) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and centroid
        c = max(cnts_left, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        # find the center from the moments 0.000001 is added to the denominator so that divide by 
        # zero exception doesn't occur
        center_left = (int(M["m10"] / (M["m00"]+0.000001)), int(M["m01"] / (M["m00"]+0.000001)))
    
        # only proceed if the radius meets a minimum size
        if radius > circle_radius:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center_left, 5, (0, 0, 255), -1)

            #the window size is kept 160 pixels in the center of the frame(80 pixels above the center and 80 below)
            if center_left[1] < (height/2 - windowSize//2):
                cv2.putText(frame,'LEFT',(20,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255))
                PressKey(A)
                current_key_pressed.add(A)
                keyPressed = True
                keyPressed_lr = True
            elif center_left[1] > (height/2 + windowSize//2):
                cv2.putText(frame,'RIGHT',(20,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255))
                PressKey(D)
                current_key_pressed.add(D)
                keyPressed = True
                keyPressed_lr = True
    
    # only proceed if at least one contour was found
    if len(cnts_right) > 0:
        c2 = max(cnts_right, key=cv2.contourArea)
        ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
        M2 = cv2.moments(c2)
        center_right = (int(M2["m10"] / (M2["m00"]+0.000001)), int(M2["m01"] / (M2["m00"]+0.000001)))
        center_right = (center_right[0]+width//2,center_right[1])
    
        # only proceed if the radius meets a minimum size
        if radius2 > circle_radius:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, (int(x2)+width//2, int(y2)), int(radius2),
                (0, 255, 255), 2)
            cv2.circle(frame, center_right, 5, (0, 0, 255), -1)
            if center_right[1] < (height//2 - windowSize//2):
                cv2.putText(frame,'UP',(200,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255))
                PressKey(W)
                keyPressed = True
                current_key_pressed.add(W)
            elif center_right[1] > (height//2 + windowSize//2):
                cv2.putText(frame,'DOWN',(200,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255))
                PressKey(S)
                keyPressed = True
                current_key_pressed.add(S)
  

    # show the frame to our screen
    frame_copy = frame.copy()
    frame_copy = cv2.rectangle(frame_copy,(0,height//2 - windowSize//2),(width,height//2 + windowSize//2),(255,0,0),2)
    cv2.imshow("Frame", frame_copy)

    #We need to release the pressed key if none of the key is pressed else the program will keep on sending
    # the presskey command 
    if not keyPressed and len(current_key_pressed) != 0:
        for key in current_key_pressed:
            ReleaseKey(key)
        current_key_pressed = set()

    #to release keys for left/right with keys of up/down remain pressed   
    if not keyPressed_lr and ((A in current_key_pressed) or (D in current_key_pressed)):
        if A in current_key_pressed:
            ReleaseKey(A)
            current_key_pressed.remove(A)
        elif D in current_key_pressed:
            ReleaseKey(D)
            current_key_pressed.remove(D)

    key = cv2.waitKey(1) & 0xFF
 
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
 

vs.stop() 
# close all windows
cv2.destroyAllWindows()